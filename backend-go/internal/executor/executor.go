package executor

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
	"golang.org/x/sync/semaphore"
)

type Executor struct {
	executionRepo  *repository.ExecutionRepository
	taskRepo       *repository.TaskRepository
	configRepo     *repository.ConfigRepository
	semaphore      *semaphore.Weighted
	defaultTimeout time.Duration
}

type logBuffer struct {
	mu  sync.Mutex
	buf strings.Builder
}

func (lb *logBuffer) write(s string) {
	lb.mu.Lock()
	lb.buf.WriteString(s)
	lb.mu.Unlock()
}

func (lb *logBuffer) string() string {
	lb.mu.Lock()
	s := lb.buf.String()
	lb.mu.Unlock()
	return s
}

func NewExecutor(
	executionRepo *repository.ExecutionRepository,
	taskRepo *repository.TaskRepository,
	configRepo *repository.ConfigRepository,
	maxConcurrent int,
	defaultTimeout time.Duration,
) *Executor {
	return &Executor{
		executionRepo:  executionRepo,
		taskRepo:       taskRepo,
		configRepo:     configRepo,
		semaphore:      semaphore.NewWeighted(int64(maxConcurrent)),
		defaultTimeout: defaultTimeout,
	}
}

func (e *Executor) Execute(ctx context.Context, execution *models.TestExecution, scriptName, scriptContent, language, filePath string) {
	var lb logBuffer

	if err := e.semaphore.Acquire(ctx, 1); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to acquire semaphore: %v\n", err))
		return
	}
	defer e.semaphore.Release(1)

	now := time.Now()
	execution.Status = "running"
	execution.StartedAt = &now
	if err := e.executionRepo.Update(ctx, execution); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to update execution status: %v\n", err))
		return
	}

	lb.write(fmt.Sprintf("[system] 开始执行脚本: %s\n", scriptName))
	lb.write(fmt.Sprintf("[system] 脚本语言: %s\n", language))

	var interpreterPath string
	switch language {
	case "python":
		interpreterPath = "python"
	case "shell":
		interpreterPath = "bash"
	case "javascript":
		interpreterPath = "node"
	}

	if scriptContent == "" && filePath != "" {
		lb.write(fmt.Sprintf("[system] 脚本内容为空，尝试从文件读取: %s\n", filePath))
		if data, err := os.ReadFile(filePath); err == nil {
			scriptContent = string(data)
			lb.write(fmt.Sprintf("[system] 成功从文件读取脚本内容: %s (共 %d 字节)\n", filePath, len(data)))
		} else {
			lb.write(fmt.Sprintf("[system] 从文件读取脚本内容失败: %v\n", err))
		}
	}

	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				lb.write(fmt.Sprintf("[system] 注入环境变量: %s\n", cfg.Key))
			}
		}
	}

	tmpDir, err := os.MkdirTemp("", "script_exec_*")
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create temp dir: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
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
		lb.write(fmt.Sprintf("[system] ERROR: Failed to write temp script file: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	lb.write(fmt.Sprintf("[system] 使用临时文件: %s\n", tmpFile))
	lb.write(fmt.Sprintf("[system] 执行命令: %s %s\n", interpreterPath, tmpFile))

	execCtx, cancel := context.WithTimeout(ctx, e.defaultTimeout)
	defer cancel()

	var cmd *exec.Cmd
	switch language {
	case "python":
		cmd = exec.CommandContext(execCtx, "python", tmpFile)
	case "shell":
		cmd = exec.CommandContext(execCtx, "bash", tmpFile)
	case "javascript":
		cmd = exec.CommandContext(execCtx, "node", tmpFile)
	default:
		lb.write(fmt.Sprintf("[system] ERROR: Unsupported language: %s\n", language))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	env := os.Environ()
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

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create stdout pipe: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	stderr, err := cmd.StderrPipe()
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create stderr pipe: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	if err := cmd.Start(); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to start command: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	done := make(chan struct{})
	go readOutput(stdout, "stdout", &lb, done)
	go readOutput(stderr, "stderr", &lb, done)

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
	lb.write(fmt.Sprintf("[system] 脚本执行完成，退出码: %d，状态: %s\n", exitCode, status))

	e.flushAndFinish(ctx, execution, exitCode, duration, &lb)
}

func readOutput(reader io.Reader, logType string, lb *logBuffer, done chan struct{}) {
	defer func() { done <- struct{}{} }()

	scanner := bufio.NewScanner(reader)
	buf := make([]byte, 0, 64*1024)
	scanner.Buffer(buf, 1024*1024)
	for scanner.Scan() {
		line := scanner.Text()
		lb.write(fmt.Sprintf("[%s] %s\n", logType, line))
	}
}

func (e *Executor) flushAndFinish(ctx context.Context, execution *models.TestExecution, exitCode int, duration time.Duration, lb *logBuffer) {
	execution.LogContent = lb.string()

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
		completedCount := task.SuccessCount + task.FailedCount
		if completedCount >= task.TotalCount {
			allSuccess := task.FailedCount == 0
			if allSuccess {
				task.Status = "completed"
			} else {
				task.Status = "failed"
			}
			now := time.Now()
			task.CompletedAt = &now
			e.taskRepo.Update(ctx, task)
		}
	}
}
