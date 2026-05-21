package executor

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"time"

	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
	"golang.org/x/sync/semaphore"
)

type Executor struct {
	executionRepo    *repository.ExecutionRepository
	executionLogRepo *repository.ExecutionLogRepository
	taskRepo         *repository.TaskRepository
	configRepo       *repository.ConfigRepository
	semaphore        *semaphore.Weighted
	defaultTimeout   time.Duration
}

func NewExecutor(
	executionRepo *repository.ExecutionRepository,
	executionLogRepo *repository.ExecutionLogRepository,
	taskRepo *repository.TaskRepository,
	configRepo *repository.ConfigRepository,
	maxConcurrent int,
	defaultTimeout time.Duration,
) *Executor {
	return &Executor{
		executionRepo:    executionRepo,
		executionLogRepo: executionLogRepo,
		taskRepo:         taskRepo,
		configRepo:       configRepo,
		semaphore:        semaphore.NewWeighted(int64(maxConcurrent)),
		defaultTimeout:   defaultTimeout,
	}
}

func (e *Executor) Execute(ctx context.Context, execution *models.TestExecution, scriptName, scriptContent, language string) {
	// Acquire semaphore
	if err := e.semaphore.Acquire(ctx, 1); err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to acquire semaphore: %v", err))
		return
	}
	defer e.semaphore.Release(1)

	// Update status to running
	now := time.Now()
	execution.Status = "running"
	execution.StartedAt = &now
	if err := e.executionRepo.Update(ctx, execution); err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to update execution status: %v", err))
		return
	}

	// Log system info header (matching Python backend format)
	e.logSystem(ctx, execution.ID, fmt.Sprintf("开始执行脚本: %s", scriptName))
	e.logSystem(ctx, execution.ID, fmt.Sprintf("脚本语言: %s", language))

	// Get interpreter path
	var interpreterPath string
	switch language {
	case "python":
		interpreterPath = "python"
	case "shell":
		interpreterPath = "bash"
	case "javascript":
		interpreterPath = "node"
	}

	// Collect env vars to inject
	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				e.logSystem(ctx, execution.ID, fmt.Sprintf("注入环境变量: %s", cfg.Key))
			}
		}
	}

	// Write script content to temp file for execution
	tmpDir, err := os.MkdirTemp("", "script_exec_*")
	if err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to create temp dir: %v", err))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}
	defer os.RemoveAll(tmpDir)

	var ext string
	switch language {
	case "python":
		ext = ".py"
	case "shell":
		ext = ".sh"
	case "javascript":
		ext = ".js"
	default:
		ext = ".txt"
	}
	tmpFile := filepath.Join(tmpDir, scriptName+ext)
	if err := os.WriteFile(tmpFile, []byte(scriptContent), 0644); err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to write temp script file: %v", err))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}

	// Log execution command
	e.logSystem(ctx, execution.ID, fmt.Sprintf("使用临时文件: %s", tmpFile))
	e.logSystem(ctx, execution.ID, fmt.Sprintf("执行命令: %s %s", interpreterPath, tmpFile))

	// Create timeout context
	execCtx, cancel := context.WithTimeout(ctx, e.defaultTimeout)
	defer cancel()

	// Determine command based on language
	var cmd *exec.Cmd
	switch language {
	case "python":
		cmd = exec.CommandContext(execCtx, "python", tmpFile)
	case "shell":
		cmd = exec.CommandContext(execCtx, "bash", tmpFile)
	case "javascript":
		cmd = exec.CommandContext(execCtx, "node", tmpFile)
	default:
		e.logError(ctx, execution.ID, fmt.Sprintf("Unsupported language: %s", language))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}

	// Inject environment variables from global configs
	env := os.Environ()
	// Force UTF-8 output for Python to avoid encoding issues on Windows
	env = append(env, "PYTHONIOENCODING=utf-8")
	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				env = append(env, fmt.Sprintf("%s=%s", cfg.Key, cfg.Value))
			}
		}
	}
	cmd.Env = env

	// Set up pipes for stdout and stderr
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to create stdout pipe: %v", err))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}

	stderr, err := cmd.StderrPipe()
	if err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to create stderr pipe: %v", err))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}

	// Start command
	if err := cmd.Start(); err != nil {
		e.logError(ctx, execution.ID, fmt.Sprintf("Failed to start command: %v", err))
		e.finishExecution(ctx, execution, 1, time.Since(now))
		return
	}

	// Read stdout and stderr concurrently
	done := make(chan struct{})
	go e.readOutput(ctx, execution.ID, stdout, "stdout", done)
	go e.readOutput(ctx, execution.ID, stderr, "stderr", done)

	// Wait for command to finish
	err = cmd.Wait()
	<-done
	<-done

	exitCode := 0
	if err != nil {
		if exitErr, ok := err.(*exec.ExitError); ok {
			exitCode = exitErr.ExitCode()
		} else {
			exitCode = 1
		}
	}

	duration := time.Since(now)
	status := "completed"
	if exitCode != 0 {
		status = "failed"
	}
	e.logSystem(ctx, execution.ID, fmt.Sprintf("脚本执行完成，退出码: %d，状态: %s", exitCode, status))

	e.finishExecution(ctx, execution, exitCode, duration)
}

// readOutput reads from a pipe and logs to database only (no file output)
func (e *Executor) readOutput(ctx context.Context, executionID int, reader io.Reader, logType string, done chan struct{}) {
	defer func() { done <- struct{}{} }()

	scanner := bufio.NewScanner(reader)
	for scanner.Scan() {
		line := scanner.Text()

		// Write to database
		log := &models.ExecutionLog{
			ExecutionID: executionID,
			LogType:     logType,
			Content:     line,
		}
		e.executionLogRepo.Create(ctx, log)
	}
}

func (e *Executor) logSystem(ctx context.Context, executionID int, message string) {
	log := &models.ExecutionLog{
		ExecutionID: executionID,
		LogType:     "system",
		Content:     message,
	}
	e.executionLogRepo.Create(ctx, log)
}

func (e *Executor) logError(ctx context.Context, executionID int, message string) {
	log := &models.ExecutionLog{
		ExecutionID: executionID,
		LogType:     "system",
		Content:     fmt.Sprintf("ERROR: %s", message),
	}
	e.executionLogRepo.Create(ctx, log)
}

func (e *Executor) finishExecution(ctx context.Context, execution *models.TestExecution, exitCode int, duration time.Duration) {
	now := time.Now()
	execution.CompletedAt = &now
	execution.ExitCode = &exitCode
	durationSeconds := duration.Seconds()
	execution.DurationSeconds = &durationSeconds

	if exitCode == 0 {
		execution.Status = "completed"
	} else {
		execution.Status = "failed"
	}

	e.executionRepo.Update(ctx, execution)

	if execution.TaskID != nil {
		if exitCode == 0 {
			e.taskRepo.IncrementSuccess(ctx, *execution.TaskID)
		} else {
			e.taskRepo.IncrementFailed(ctx, *execution.TaskID)
		}
		e.checkAndCompleteTask(ctx, *execution.TaskID)
	}
}

func (e *Executor) checkAndCompleteTask(ctx context.Context, taskID int) {
	task, err := e.taskRepo.GetByID(ctx, taskID)
	if err != nil {
		return
	}

	executions, err := e.executionRepo.ListByTaskID(ctx, taskID)
	if err != nil {
		return
	}

	completedCount := 0
	for _, exec := range executions {
		if exec.Status == "completed" || exec.Status == "failed" {
			completedCount++
		}
	}

	if completedCount >= task.TotalCount {
		e.taskRepo.Complete(ctx, taskID, "completed")
	}
}
