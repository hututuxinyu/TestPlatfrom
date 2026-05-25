package executor

import (
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

// runCommand executes a command with timeout and captures output
func runCommand(ctx context.Context, cmd *exec.Cmd, timeout time.Duration, lb *logBuffer) (int, time.Duration) {
	startTime := time.Now()

	// Create pipes before starting
	stdoutPipe, err := cmd.StdoutPipe()
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create stdout pipe: %v\n", err))
		return 1, time.Since(startTime)
	}
	stderrPipe, err := cmd.StderrPipe()
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create stderr pipe: %v\n", err))
		return 1, time.Since(startTime)
	}

	// Start the process
	if err := cmd.Start(); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to start command: %v\n", err))
		return 1, time.Since(startTime)
	}

	// Read stdout and stderr concurrently while process is running
	var stdoutData, stderrData []byte
	var stdoutErr, stderrErr error
	stdoutDone := make(chan struct{})
	stderrDone := make(chan struct{})

	go func() {
		stdoutData, stdoutErr = io.ReadAll(stdoutPipe)
		close(stdoutDone)
	}()

	go func() {
		stderrData, stderrErr = io.ReadAll(stderrPipe)
		close(stderrDone)
	}()

	// Wait for process in a goroutine
	waitChan := make(chan error, 1)
	go func() {
		waitChan <- cmd.Wait()
	}()

	// Wait for completion or timeout
	var waitErr error
	select {
	case waitErr = <-waitChan:
		lb.write("[system] Process completed\n")
	case <-time.After(timeout):
		lb.write(fmt.Sprintf("[system] Process timeout after %.0f seconds, killing...\n", timeout.Seconds()))
		if cmd.Process != nil {
			cmd.Process.Kill()
		}
		waitErr = cmd.Wait()
		lb.write("[system] Process killed\n")
	}

	// Wait for output readers to finish
	<-stdoutDone
	<-stderrDone

	// Write stdout
	if stdoutErr == nil && len(stdoutData) > 0 {
		lines := strings.Split(string(stdoutData), "\n")
		for _, line := range lines {
			if line != "" {
				lb.write(fmt.Sprintf("[stdout] %s\n", line))
			}
		}
	}

	// Write stderr
	if stderrErr == nil && len(stderrData) > 0 {
		lines := strings.Split(string(stderrData), "\n")
		for _, line := range lines {
			if line != "" {
				lb.write(fmt.Sprintf("[stderr] %s\n", line))
			}
		}
	}

	// Get exit code
	exitCode := 0
	if waitErr != nil {
		if exitErr, ok := waitErr.(*exec.ExitError); ok {
			exitCode = exitErr.ExitCode()
		} else {
			exitCode = 1
		}
	}

	// If killed due to timeout, force exit code to 1
	if exitCode == -1 {
		exitCode = 1
	}

	return exitCode, time.Since(startTime)
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

	var cmd *exec.Cmd
	switch language {
	case "python":
		cmd = exec.Command("python", "-u", tmpFile)
	case "shell":
		cmd = exec.Command("bash", tmpFile)
	case "javascript":
		cmd = exec.Command("node", tmpFile)
	default:
		lb.write(fmt.Sprintf("[system] ERROR: Unsupported language: %s\n", language))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	env := os.Environ()
	env = append(env, "PYTHONIOENCODING=utf-8")
	env = append(env, "PYTHONUNBUFFERED=1")
	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				env = append(env, fmt.Sprintf("%s=%s", cfg.Key, cfg.Value))
			}
		}
	}
	cmd.Env = env

	exitCode, duration := runCommand(ctx, cmd, e.defaultTimeout, &lb)

	status := "completed"
	if exitCode != 0 {
		status = "failed"
	}
	lb.write(fmt.Sprintf("[system] 脚本执行完成，退出码: %d，状态: %s，耗时: %.1fs\n", exitCode, status, duration.Seconds()))

	e.flushAndFinish(ctx, execution, exitCode, duration, &lb)
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

// ExecuteWithLibs executes a test script with lib files restored to correct directory structure
func (e *Executor) ExecuteWithLibs(ctx context.Context, execution *models.TestExecution, script *models.TestScript, libFiles []*models.TestScript) {
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

	lb.write(fmt.Sprintf("[system] 开始执行脚本: %s\n", script.Name))
	lb.write(fmt.Sprintf("[system] 脚本语言: %s\n", script.Language))

	interpreterPath := "python"
	if script.Language == "shell" {
		interpreterPath = "bash"
	} else if script.Language == "javascript" {
		interpreterPath = "node"
	}

	// Create temp directory
	tmpDir, err := os.MkdirTemp("", "suite_exec_*")
	if err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create temp dir: %v\n", err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}
	defer os.RemoveAll(tmpDir)

	lb.write(fmt.Sprintf("[system] 临时目录: %s\n", tmpDir))

	// Restore lib files to correct directory structure
	if len(libFiles) > 0 {
		lb.write(fmt.Sprintf("[system] 恢复 %d 个库文件目录结构\n", len(libFiles)))
		for _, libFile := range libFiles {
			libPath := libFile.FilePath
			libPath = strings.ReplaceAll(libPath, "\\", "/")

			fullPath := filepath.Join(tmpDir, libPath)

			dir := filepath.Dir(fullPath)
			if err := os.MkdirAll(dir, 0755); err != nil {
				lb.write(fmt.Sprintf("[system] ERROR: Failed to create lib directory %s: %v\n", dir, err))
				continue
			}

			if err := os.WriteFile(fullPath, []byte(libFile.Content), 0644); err != nil {
				lb.write(fmt.Sprintf("[system] ERROR: Failed to write lib file %s: %v\n", fullPath, err))
				continue
			}

			lb.write(fmt.Sprintf("[system] 已恢复库文件: %s\n", libPath))
		}
	}

	// Write test script to temp directory
	scriptPath := script.FilePath
	if scriptPath == "" {
		scriptPath = script.Name + ".py"
	}
	scriptPath = strings.ReplaceAll(scriptPath, "\\", "/")

	fullScriptPath := filepath.Join(tmpDir, scriptPath)

	scriptDir := filepath.Dir(fullScriptPath)
	if scriptDir != tmpDir {
		if err := os.MkdirAll(scriptDir, 0755); err != nil {
			lb.write(fmt.Sprintf("[system] ERROR: Failed to create script directory %s: %v\n", scriptDir, err))
			e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
			return
		}
	}

	// Preprocess script content for __file__
	scriptContent := script.Content
	lb.write(fmt.Sprintf("[system] 脚本内容长度: %d 字符\n", len(scriptContent)))

	hasFile := strings.Contains(scriptContent, "__file__")
	lb.write(fmt.Sprintf("[system] 是否包含 __file__: %v\n", hasFile))

	if hasFile && script.Language == "python" {
		lb.write("[system] 开始预处理 __file__ fallback\n")

		fileFallback := `
# __file__ fallback for execution environments where it's not defined
import sys, os
if '__file__' not in dir():
    __file__ = os.path.abspath(sys.argv[0]) if sys.argv else ''
`
		lines := strings.Split(scriptContent, "\n")
		insertPos := 0

		if len(lines) > 0 && strings.HasPrefix(lines[0], "#!") {
			insertPos = 1
		}

		if len(lines) > insertPos && strings.HasPrefix(lines[insertPos], "# -*-") {
			insertPos++
		}

		for insertPos < len(lines) && lines[insertPos] == "" {
			insertPos++
		}

		if insertPos < len(lines) && strings.HasPrefix(lines[insertPos], "\"\"\"") {
			insertPos++
			for insertPos < len(lines) {
				if strings.Contains(lines[insertPos], "\"\"\"") {
					insertPos++
					break
				}
				insertPos++
			}
		}

		for insertPos < len(lines) && lines[insertPos] == "" {
			insertPos++
		}

		if insertPos > 0 && insertPos <= len(lines) {
			fallbackLines := strings.Split(fileFallback, "\n")
			if len(fallbackLines) > 0 && fallbackLines[0] == "" {
				fallbackLines = fallbackLines[1:]
			}
			if len(fallbackLines) > 0 && fallbackLines[len(fallbackLines)-1] == "" {
				fallbackLines = fallbackLines[:len(fallbackLines)-1]
			}

			newLines := make([]string, 0, len(lines)+len(fallbackLines))
			newLines = append(newLines, lines[:insertPos]...)
			newLines = append(newLines, fallbackLines...)
			newLines = append(newLines, lines[insertPos:]...)
			scriptContent = strings.Join(newLines, "\n")
			lb.write(fmt.Sprintf("[system] 已在位置 %d 插入 __file__ fallback\n", insertPos))
		}
	}

	if err := os.WriteFile(fullScriptPath, []byte(scriptContent), 0644); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to write script file %s: %v\n", fullScriptPath, err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	lb.write(fmt.Sprintf("[system] 使用临时文件: %s\n", fullScriptPath))
	lb.write(fmt.Sprintf("[system] 执行命令: %s %s\n", interpreterPath, fullScriptPath))

	var cmd *exec.Cmd
	switch script.Language {
	case "python":
		cmd = exec.Command("python", "-u", fullScriptPath)
	case "shell":
		cmd = exec.Command("bash", fullScriptPath)
	case "javascript":
		cmd = exec.Command("node", fullScriptPath)
	default:
		lb.write(fmt.Sprintf("[system] ERROR: Unsupported language: %s\n", script.Language))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}

	// Set environment variables
	env := os.Environ()
	env = append(env, "PYTHONIOENCODING=utf-8")
	env = append(env, "PYTHONUNBUFFERED=1")
	testDir := filepath.Join(tmpDir, "test")
	if err := os.MkdirAll(testDir, 0755); err != nil {
		lb.write(fmt.Sprintf("[system] ERROR: Failed to create test directory %s: %v\n", testDir, err))
		e.flushAndFinish(ctx, execution, 1, time.Since(now), &lb)
		return
	}
	env = append(env, fmt.Sprintf("PYTHONPATH=%s", testDir))
	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				env = append(env, fmt.Sprintf("%s=%s", cfg.Key, cfg.Value))
			}
		}
	}
	cmd.Env = env

	// Set working directory
	cmd.Dir = testDir
	lb.write(fmt.Sprintf("[system] 工作目录: %s\n", testDir))
	lb.write(fmt.Sprintf("[system] PYTHONPATH: %s\n", testDir))

	exitCode, duration := runCommand(ctx, cmd, e.defaultTimeout, &lb)

	status := "completed"
	if exitCode != 0 {
		status = "failed"
	}
	lb.write(fmt.Sprintf("[system] 脚本执行完成，退出码: %d，状态: %s，耗时: %.1fs\n", exitCode, status, duration.Seconds()))
	lb.write(fmt.Sprintf("[system] 清理临时目录: %s\n", tmpDir))

	e.flushAndFinish(ctx, execution, exitCode, duration, &lb)
}