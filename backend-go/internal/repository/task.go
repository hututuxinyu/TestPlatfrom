package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/testplatform/backend/internal/models"
)

type TaskRepository struct {
	db *sql.DB
}

func NewTaskRepository(db *sql.DB) *TaskRepository {
	return &TaskRepository{db: db}
}

// Create creates a new test task
func (r *TaskRepository) Create(ctx context.Context, task *models.TestTask) error {
	query := `
		INSERT INTO test_tasks (suite_id, suite_name, status, total_count, success_count, failed_count, created_by)
		VALUES (?, ?, ?, ?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		task.SuiteID, task.SuiteName, task.Status, task.TotalCount,
		task.SuccessCount, task.FailedCount, task.CreatedBy,
	)
	if err != nil {
		return fmt.Errorf("failed to create task: %w", err)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return fmt.Errorf("failed to get last insert id: %w", err)
	}
	task.ID = int(id)

	// Get created_at
	query = `SELECT created_at FROM test_tasks WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, task.ID).Scan(&task.CreatedAt)
	if err != nil {
		return fmt.Errorf("failed to get timestamp: %w", err)
	}

	return nil
}

// GetByID retrieves a task by ID
func (r *TaskRepository) GetByID(ctx context.Context, id int) (*models.TestTask, error) {
	query := `
		SELECT id, suite_id, suite_name, status, total_count, success_count, failed_count, created_by, created_at, completed_at
		FROM test_tasks
		WHERE id = ?
	`
	task := &models.TestTask{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&task.ID, &task.SuiteID, &task.SuiteName, &task.Status,
		&task.TotalCount, &task.SuccessCount, &task.FailedCount,
		&task.CreatedBy, &task.CreatedAt, &task.CompletedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get task by id: %w", err)
	}
	return task, nil
}

// Update updates a task
func (r *TaskRepository) Update(ctx context.Context, task *models.TestTask) error {
	query := `
		UPDATE test_tasks
		SET status = ?, total_count = ?, success_count = ?, failed_count = ?, completed_at = ?
		WHERE id = ?
	`
	_, err := r.db.ExecContext(ctx, query,
		task.Status, task.TotalCount, task.SuccessCount, task.FailedCount,
		task.CompletedAt, task.ID,
	)
	if err != nil {
		return fmt.Errorf("failed to update task: %w", err)
	}
	return nil
}

// UpdateStatus updates task status
func (r *TaskRepository) UpdateStatus(ctx context.Context, id int, status string) error {
	query := `UPDATE test_tasks SET status = ? WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, status, id)
	if err != nil {
		return fmt.Errorf("failed to update task status: %w", err)
	}
	return nil
}

// IncrementSuccess increments success count
func (r *TaskRepository) IncrementSuccess(ctx context.Context, id int) error {
	query := `UPDATE test_tasks SET success_count = success_count + 1 WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to increment success count: %w", err)
	}
	return nil
}

// IncrementFailed increments failed count
func (r *TaskRepository) IncrementFailed(ctx context.Context, id int) error {
	query := `UPDATE test_tasks SET failed_count = failed_count + 1 WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to increment failed count: %w", err)
	}
	return nil
}

// Complete marks task as completed
func (r *TaskRepository) Complete(ctx context.Context, id int, status string) error {
	query := `UPDATE test_tasks SET status = ?, completed_at = ? WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, status, time.Now(), id)
	if err != nil {
		return fmt.Errorf("failed to complete task: %w", err)
	}
	return nil
}

// List retrieves tasks with optional suite filter
func (r *TaskRepository) List(ctx context.Context, suiteID int, limit, offset int) ([]*models.TestTask, error) {
	query := `
		SELECT id, suite_id, suite_name, status, total_count, success_count, failed_count, created_by, created_at, completed_at
		FROM test_tasks
		WHERE (? = 0 OR suite_id = ?)
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`
	rows, err := r.db.QueryContext(ctx, query, suiteID, suiteID, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list tasks: %w", err)
	}
	defer rows.Close()

	var tasks []*models.TestTask
	for rows.Next() {
		task := &models.TestTask{}
		err := rows.Scan(
			&task.ID, &task.SuiteID, &task.SuiteName, &task.Status,
			&task.TotalCount, &task.SuccessCount, &task.FailedCount,
			&task.CreatedBy, &task.CreatedAt, &task.CompletedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan task: %w", err)
		}
		tasks = append(tasks, task)
	}

	return tasks, nil
}

// Count returns the total number of tasks
func (r *TaskRepository) Count(ctx context.Context, suiteID int) (int, error) {
	query := `SELECT COUNT(*) FROM test_tasks WHERE (? = 0 OR suite_id = ?)`
	var count int
	err := r.db.QueryRowContext(ctx, query, suiteID, suiteID).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count tasks: %w", err)
	}
	return count, nil
}

// Delete deletes a task
func (r *TaskRepository) Delete(ctx context.Context, id int) error {
	query := `DELETE FROM test_tasks WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete task: %w", err)
	}
	return nil
}
