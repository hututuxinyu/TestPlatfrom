package models

import "time"

type User struct {
	ID           int       `json:"id"`
	Username     string    `json:"username"`
	PasswordHash string    `json:"-"`
	Email        string    `json:"email"`
	IsActive     bool      `json:"is_active"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

type TestScript struct {
	ID          int       `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Language    string    `json:"language"`
	FilePath    string    `json:"file_path"`
	FileSize    int64     `json:"file_size"`
	FileHash    string    `json:"file_hash"`
	Tags        string    `json:"tags"`
	CreatedBy   *int      `json:"created_by"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}

type TestExecution struct {
	ID              int        `json:"id"`
	ScriptID        int        `json:"script_id"`
	ScriptName      string     `json:"script_name"`
	Status          string     `json:"status"`
	ExitCode        *int       `json:"exit_code"`
	StartedAt       *time.Time `json:"started_at"`
	CompletedAt     *time.Time `json:"completed_at"`
	DurationSeconds *float64   `json:"duration_seconds"`
	CreatedBy       *int       `json:"created_by"`
	CreatedAt       time.Time  `json:"created_at"`
}

type ExecutionLog struct {
	ID          int       `json:"id"`
	ExecutionID int       `json:"execution_id"`
	LogType     string    `json:"log_type"`
	Content     string    `json:"content"`
	CreatedAt   time.Time `json:"created_at"`
}

type GlobalConfig struct {
	ID          int       `json:"id"`
	Key         string    `json:"key"`
	Value       string    `json:"value"`
	Description string    `json:"description"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}
