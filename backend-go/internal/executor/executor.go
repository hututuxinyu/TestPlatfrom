package executor

import (
	"bufio"
	"compress/gzip"
	"context"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"sync"
	"time"

	"github.com/testplatform/backend/internal/models"
	"github.com/testplatform/backend/internal/repository"
	"golang.org/x/sync/semaphore"
)

const (
	maxLogFileSize   = 10 * 1024 * 1024 // 10MB per log file
	maxLogFiles      = 10                // Keep 10 rotated log files
	logFileName      = "all.log"
)

type Executor struct {
	executionRepo    *repository.ExecutionRepository
	executionLogRepo *repository.ExecutionLogRepository
	configRepo       *repository.ConfigRepository
	semaphore        *semaphore.Weighted
	logDir           string
	defaultTimeout   time.Duration
	logFile          *os.File
	logMu            sync.Mutex // Mutex for thread-safe log file writing
}

// NewExecutor creates a new executor
func NewExecutor(
	executionRepo *repository.ExecutionRepository,
	executionLogRepo *repository.ExecutionLogRepository,
	configRepo *repository.ConfigRepository,
	maxConcurrent int,
	logDir string,
	defaultTimeout time.Duration,
) *Executor {
	executor := &Executor{
		executionRepo:    executionRepo,
		executionLogRepo: executionLogRepo,
		configRepo:       configRepo,
		semaphore:        semaphore.NewWeighted(int64(maxConcurrent)),
		logDir:           logDir,
		defaultTimeout:   defaultTimeout,
	}
	// Initialize shared log file
	executor.initLogFile()
	return executor
}

// initLogFile initializes the shared log file
func (e *Executor) initLogFile() {
	if err := os.MkdirAll(e.logDir, 0755); err != nil {
		fmt.Printf("Failed to create log directory: %v\n", err)
		return
	}

	logPath := filepath.Join(e.logDir, logFileName)
	file, err := os.OpenFile(logPath, os.O_APPEND|os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		fmt.Printf("Failed to open log file: %v\n", err)
		return
	}
	e.logFile = file
}

// Execute runs a test script
func (e *Executor) Execute(ctx context.Context, execution *models.TestExecution, scriptPath string, language string) {
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

	// Resolve absolute path
	absPath, err := filepath.Abs(scriptPath)
	if err != nil {
		absPath = scriptPath
	}

	// Log system info header (matching Python backend format)
	e.logSystem(ctx, execution.ID, fmt.Sprintf("开始执行脚本: %s", absPath))
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
	e.logSystem(ctx, execution.ID, fmt.Sprintf("使用绝对路径: %s", absPath))

	// Collect env vars to inject
	if e.configRepo != nil {
		configs, err := e.configRepo.List(ctx)
		if err == nil && len(configs) > 0 {
			for _, cfg := range configs {
				e.logSystem(ctx, execution.ID, fmt.Sprintf("注入环境变量: %s", cfg.Key))
			}
		}
	}

	// Log execution command
	if language == "python" {
		e.logSystem(ctx, execution.ID, fmt.Sprintf("执行命令: python %s", absPath))
	} else {
		e.logSystem(ctx, execution.ID, fmt.Sprintf("执行命令: %s %s", interpreterPath, absPath))
	}

	// Create timeout context
	execCtx, cancel := context.WithTimeout(ctx, e.defaultTimeout)
	defer cancel()

	// Determine command based on language
	var cmd *exec.Cmd
	switch language {
	case "python":
		cmd = exec.CommandContext(execCtx, "python", scriptPath)
	case "shell":
		cmd = exec.CommandContext(execCtx, "bash", scriptPath)
	case "javascript":
		cmd = exec.CommandContext(execCtx, "node", scriptPath)
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

	// Check if rotation is needed
	e.rotateLogIfNeeded()

	e.finishExecution(ctx, execution, exitCode, duration)
}

// readOutput reads from a pipe and logs to both database and file
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

		// Write to execution-specific log file without [stdout] prefix (matching Python backend format)
		e.writeExecutionLog(executionID, "STDOUT", line)
	}
}

// logSystem logs a system message
func (e *Executor) logSystem(ctx context.Context, executionID int, message string) {
	log := &models.ExecutionLog{
		ExecutionID: executionID,
		LogType:     "system",
		Content:     message,
	}
	e.executionLogRepo.Create(ctx, log)
	e.writeExecutionLog(executionID, "SYSTEM", message)
}

// logError logs an error message
func (e *Executor) logError(ctx context.Context, executionID int, message string) {
	log := &models.ExecutionLog{
		ExecutionID: executionID,
		LogType:     "system",
		Content:     fmt.Sprintf("ERROR: %s", message),
	}
	e.executionLogRepo.Create(ctx, log)
	e.writeExecutionLog(executionID, "ERROR", message)
}

// writeExecutionLog writes a log entry to the shared all.log file
func (e *Executor) writeExecutionLog(executionID int, level string, message string) {
	e.logMu.Lock()
	defer e.logMu.Unlock()

	timestamp := time.Now().Format("2006-01-02 15:04:05")

	// Write to shared all.log
	if e.logFile != nil {
		fmt.Fprintf(e.logFile, "[%s] [execution_id=%d] [%s] %s\n", timestamp, executionID, level, message)
		e.logFile.Sync()
	}
}

// rotateLogIfNeeded checks log file size and rotates if necessary
func (e *Executor) rotateLogIfNeeded() {
	e.logMu.Lock()
	defer e.logMu.Unlock()

	if e.logFile == nil {
		return
	}

	stat, err := e.logFile.Stat()
	if err != nil {
		return
	}

	if stat.Size() < maxLogFileSize {
		return
	}

	// Close current file
	e.logFile.Close()

	// Rotate: all.log -> all.log.1.gz -> all.log.2.gz -> ...
	// First, compress the current log
	now := time.Now().Format("20060102_150405")
	rotatedName := fmt.Sprintf("all.log.%s.gz", now)
	rotatedPath := filepath.Join(e.logDir, rotatedName)

	// Compress the existing all.log to rotated file
	if err := e.compressFile(filepath.Join(e.logDir, logFileName), rotatedPath); err != nil {
		fmt.Printf("Failed to compress log file: %v\n", err)
		// Reopen original file for appending
		e.logFile, _ = os.OpenFile(filepath.Join(e.logDir, logFileName), os.O_APPEND|os.O_CREATE|os.O_RDWR, 0644)
		return
	}

	// Delete oldest rotated files if exceeding maxLogFiles
	e.cleanOldLogs()

	// Reopen the main log file (truncate)
	e.logFile, err = os.OpenFile(filepath.Join(e.logDir, logFileName), os.O_TRUNC|os.O_CREATE|os.O_RDWR, 0644)
	if err != nil {
		fmt.Printf("Failed to reopen log file: %v\n", err)
	}
}

// compressFile compresses a file using gzip
func (e *Executor) compressFile(src, dst string) error {
	srcFile, err := os.Open(src)
	if err != nil {
		return err
	}
	defer srcFile.Close()

	dstFile, err := os.Create(dst)
	if err != nil {
		return err
	}
	defer dstFile.Close()

	gzWriter := gzip.NewWriter(dstFile)
	defer gzWriter.Close()

	_, err = io.Copy(gzWriter, srcFile)
	return err
}

// cleanOldLogs removes the oldest rotated log files exceeding maxLogFiles
func (e *Executor) cleanOldLogs() {
	pattern := filepath.Join(e.logDir, "all.log.*.gz")
	matches, err := filepath.Glob(pattern)
	if err != nil {
		return
	}

	if len(matches) <= maxLogFiles {
		return
	}

	// Sort by name (which includes timestamp)
	sort.Strings(matches)

	// Delete oldest files
	deleteCount := len(matches) - maxLogFiles
	for i := 0; i < deleteCount; i++ {
		os.Remove(matches[i])
	}
}

// finishExecution updates execution with final status
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
}
