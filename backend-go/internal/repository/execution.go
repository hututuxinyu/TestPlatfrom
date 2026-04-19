package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/testplatform/backend/internal/models"
)

type ExecutionRepository struct {
	db *sql.DB
}

func NewExecutionRepository(db *sql.DB) *ExecutionRepository {
	return &ExecutionRepository{db: db}
}

// Create creates a new test execution
func (r *ExecutionRepository) Create(ctx context.Context, execution *models.TestExecution) error {
	query := `
		INSERT INTO test_executions (script_id, script_name, status, created_by)
		VALUES (?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		execution.ScriptID, execution.ScriptName, execution.Status, execution.CreatedBy,
	)
	if err != nil {
		return fmt.Errorf("failed to create execution: %w", err)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return fmt.Errorf("failed to get last insert id: %w", err)
	}
	execution.ID = int(id)

	// Get created_at
	query = `SELECT created_at FROM test_executions WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, execution.ID).Scan(&execution.CreatedAt)
	if err != nil {
		return fmt.Errorf("failed to get timestamp: %w", err)
	}

	return nil
}

// GetByID retrieves an execution by ID
func (r *ExecutionRepository) GetByID(ctx context.Context, id int) (*models.TestExecution, error) {
	query := `
		SELECT id, script_id, script_name, status, exit_code, started_at, completed_at, duration_seconds, created_by, created_at
		FROM test_executions
		WHERE id = ?
	`
	execution := &models.TestExecution{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&execution.ID, &execution.ScriptID, &execution.ScriptName, &execution.Status,
		&execution.ExitCode, &execution.StartedAt, &execution.CompletedAt,
		&execution.DurationSeconds, &execution.CreatedBy, &execution.CreatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get execution by id: %w", err)
	}
	return execution, nil
}

// Update updates an execution
func (r *ExecutionRepository) Update(ctx context.Context, execution *models.TestExecution) error {
	query := `
		UPDATE test_executions
		SET status = ?, exit_code = ?, started_at = ?, completed_at = ?, duration_seconds = ?
		WHERE id = ?
	`
	_, err := r.db.ExecContext(ctx, query,
		execution.Status, execution.ExitCode, execution.StartedAt,
		execution.CompletedAt, execution.DurationSeconds, execution.ID,
	)
	if err != nil {
		return fmt.Errorf("failed to update execution: %w", err)
	}
	return nil
}

// List retrieves executions with optional filters
func (r *ExecutionRepository) List(ctx context.Context, scriptID int, status string, limit, offset int) ([]*models.TestExecution, error) {
	query := `
		SELECT id, script_id, script_name, status, exit_code, started_at, completed_at, duration_seconds, created_by, created_at
		FROM test_executions
		WHERE (? = 0 OR script_id = ?) AND (? = '' OR status = ?)
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`
	rows, err := r.db.QueryContext(ctx, query, scriptID, scriptID, status, status, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list executions: %w", err)
	}
	defer rows.Close()

	var executions []*models.TestExecution
	for rows.Next() {
		execution := &models.TestExecution{}
		err := rows.Scan(
			&execution.ID, &execution.ScriptID, &execution.ScriptName, &execution.Status,
			&execution.ExitCode, &execution.StartedAt, &execution.CompletedAt,
			&execution.DurationSeconds, &execution.CreatedBy, &execution.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan execution: %w", err)
		}
		executions = append(executions, execution)
	}

	return executions, nil
}

// Count returns the total number of executions
func (r *ExecutionRepository) Count(ctx context.Context, scriptID int, status string) (int, error) {
	query := `
		SELECT COUNT(*)
		FROM test_executions
		WHERE (? = 0 OR script_id = ?) AND (? = '' OR status = ?)
	`
	var count int
	err := r.db.QueryRowContext(ctx, query, scriptID, scriptID, status, status).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count executions: %w", err)
	}
	return count, nil
}

// Delete deletes an execution
func (r *ExecutionRepository) Delete(ctx context.Context, id int) error {
	query := `DELETE FROM test_executions WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete execution: %w", err)
	}
	return nil
}
