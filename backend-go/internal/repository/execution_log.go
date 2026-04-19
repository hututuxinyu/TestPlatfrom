package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/testplatform/backend/internal/models"
)

type ExecutionLogRepository struct {
	db *sql.DB
}

func NewExecutionLogRepository(db *sql.DB) *ExecutionLogRepository {
	return &ExecutionLogRepository{db: db}
}

// Create creates a new execution log entry
func (r *ExecutionLogRepository) Create(ctx context.Context, log *models.ExecutionLog) error {
	query := `
		INSERT INTO execution_logs (execution_id, log_type, content)
		VALUES (?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query, log.ExecutionID, log.LogType, log.Content)
	if err != nil {
		return fmt.Errorf("failed to create execution log: %w", err)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return fmt.Errorf("failed to get last insert id: %w", err)
	}
	log.ID = int(id)

	// Get created_at
	query = `SELECT created_at FROM execution_logs WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, log.ID).Scan(&log.CreatedAt)
	if err != nil {
		return fmt.Errorf("failed to get timestamp: %w", err)
	}

	return nil
}

// GetByExecutionID retrieves all logs for an execution
func (r *ExecutionLogRepository) GetByExecutionID(ctx context.Context, executionID int) ([]*models.ExecutionLog, error) {
	query := `
		SELECT id, execution_id, log_type, content, created_at
		FROM execution_logs
		WHERE execution_id = ?
		ORDER BY created_at ASC
	`
	rows, err := r.db.QueryContext(ctx, query, executionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get execution logs: %w", err)
	}
	defer rows.Close()

	var logs []*models.ExecutionLog
	for rows.Next() {
		log := &models.ExecutionLog{}
		err := rows.Scan(&log.ID, &log.ExecutionID, &log.LogType, &log.Content, &log.CreatedAt)
		if err != nil {
			return nil, fmt.Errorf("failed to scan execution log: %w", err)
		}
		logs = append(logs, log)
	}

	return logs, nil
}

// DeleteByExecutionID deletes all logs for an execution
func (r *ExecutionLogRepository) DeleteByExecutionID(ctx context.Context, executionID int) error {
	query := `DELETE FROM execution_logs WHERE execution_id = ?`
	_, err := r.db.ExecContext(ctx, query, executionID)
	if err != nil {
		return fmt.Errorf("failed to delete execution logs: %w", err)
	}
	return nil
}
