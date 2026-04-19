package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/testplatform/backend/internal/models"
)

type ScriptRepository struct {
	db *sql.DB
}

func NewScriptRepository(db *sql.DB) *ScriptRepository {
	return &ScriptRepository{db: db}
}

// Create creates a new test script
func (r *ScriptRepository) Create(ctx context.Context, script *models.TestScript) error {
	query := `
		INSERT INTO test_scripts (name, description, language, file_path, file_size, file_hash, tags, created_by)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query,
		script.Name, script.Description, script.Language, script.FilePath,
		script.FileSize, script.FileHash, script.Tags, script.CreatedBy,
	)
	if err != nil {
		return fmt.Errorf("failed to create script: %w", err)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return fmt.Errorf("failed to get last insert id: %w", err)
	}
	script.ID = int(id)

	// Get timestamps
	query = `SELECT created_at, updated_at FROM test_scripts WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, script.ID).Scan(&script.CreatedAt, &script.UpdatedAt)
	if err != nil {
		return fmt.Errorf("failed to get timestamps: %w", err)
	}

	return nil
}

// GetByID retrieves a script by ID
func (r *ScriptRepository) GetByID(ctx context.Context, id int) (*models.TestScript, error) {
	query := `
		SELECT id, name, description, language, file_path, file_size, file_hash, tags, created_by, created_at, updated_at
		FROM test_scripts
		WHERE id = ?
	`
	script := &models.TestScript{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&script.ID, &script.Name, &script.Description, &script.Language,
		&script.FilePath, &script.FileSize, &script.FileHash, &script.Tags,
		&script.CreatedBy, &script.CreatedAt, &script.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get script by id: %w", err)
	}
	return script, nil
}

// GetByName retrieves a script by name
func (r *ScriptRepository) GetByName(ctx context.Context, name string) (*models.TestScript, error) {
	query := `
		SELECT id, name, description, language, file_path, file_size, file_hash, tags, created_by, created_at, updated_at
		FROM test_scripts
		WHERE name = ?
	`
	script := &models.TestScript{}
	err := r.db.QueryRowContext(ctx, query, name).Scan(
		&script.ID, &script.Name, &script.Description, &script.Language,
		&script.FilePath, &script.FileSize, &script.FileHash, &script.Tags,
		&script.CreatedBy, &script.CreatedAt, &script.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get script by name: %w", err)
	}
	return script, nil
}

// Update updates a test script
func (r *ScriptRepository) Update(ctx context.Context, script *models.TestScript) error {
	query := `
		UPDATE test_scripts
		SET description = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	`
	_, err := r.db.ExecContext(ctx, query, script.Description, script.Tags, script.ID)
	if err != nil {
		return fmt.Errorf("failed to update script: %w", err)
	}

	// Get updated timestamp
	query = `SELECT updated_at FROM test_scripts WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, script.ID).Scan(&script.UpdatedAt)
	if err != nil {
		return fmt.Errorf("failed to get updated timestamp: %w", err)
	}

	return nil
}

// Delete deletes a test script
func (r *ScriptRepository) Delete(ctx context.Context, id int) error {
	query := `DELETE FROM test_scripts WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete script: %w", err)
	}
	return nil
}

// List retrieves all scripts with optional filters
func (r *ScriptRepository) List(ctx context.Context, language string, limit, offset int) ([]*models.TestScript, error) {
	query := `
		SELECT id, name, description, language, file_path, file_size, file_hash, tags, created_by, created_at, updated_at
		FROM test_scripts
		WHERE (? = '' OR language = ?)
		ORDER BY created_at DESC
		LIMIT ? OFFSET ?
	`
	rows, err := r.db.QueryContext(ctx, query, language, language, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list scripts: %w", err)
	}
	defer rows.Close()

	var scripts []*models.TestScript
	for rows.Next() {
		script := &models.TestScript{}
		err := rows.Scan(
			&script.ID, &script.Name, &script.Description, &script.Language,
			&script.FilePath, &script.FileSize, &script.FileHash, &script.Tags,
			&script.CreatedBy, &script.CreatedAt, &script.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan script: %w", err)
		}
		scripts = append(scripts, script)
	}

	return scripts, nil
}

// Count returns the total number of scripts
func (r *ScriptRepository) Count(ctx context.Context, language string) (int, error) {
	query := `
		SELECT COUNT(*)
		FROM test_scripts
		WHERE (? = '' OR language = ?)
	`
	var count int
	err := r.db.QueryRowContext(ctx, query, language, language).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("failed to count scripts: %w", err)
	}
	return count, nil
}
