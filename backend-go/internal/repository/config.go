package repository

import (
	"context"
	"database/sql"
	"fmt"

	"github.com/testplatform/backend/internal/models"
)

type ConfigRepository struct {
	db *sql.DB
}

func NewConfigRepository(db *sql.DB) *ConfigRepository {
	return &ConfigRepository{db: db}
}

// Get retrieves a config by key
func (r *ConfigRepository) Get(ctx context.Context, key string) (*models.GlobalConfig, error) {
	query := `
		SELECT id, ` + "`key`" + `, value, description, created_at, updated_at
		FROM global_configs
		WHERE ` + "`key`" + ` = ?
	`
	config := &models.GlobalConfig{}
	err := r.db.QueryRowContext(ctx, query, key).Scan(
		&config.ID, &config.Key, &config.Value, &config.Description,
		&config.CreatedAt, &config.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get config: %w", err)
	}
	return config, nil
}

// Set creates or updates a config
func (r *ConfigRepository) Set(ctx context.Context, config *models.GlobalConfig) error {
	query := `
		INSERT INTO global_configs (` + "`key`" + `, value, description)
		VALUES (?, ?, ?)
		ON DUPLICATE KEY UPDATE
		value = VALUES(value), description = VALUES(description), updated_at = CURRENT_TIMESTAMP
	`
	result, err := r.db.ExecContext(ctx, query, config.Key, config.Value, config.Description)
	if err != nil {
		return fmt.Errorf("failed to set config: %w", err)
	}

	id, err := result.LastInsertId()
	if err == nil {
		config.ID = int(id)
	}

	// Get timestamps
	query = `SELECT id, created_at, updated_at FROM global_configs WHERE ` + "`key`" + ` = ?`
	err = r.db.QueryRowContext(ctx, query, config.Key).Scan(&config.ID, &config.CreatedAt, &config.UpdatedAt)
	if err != nil {
		return fmt.Errorf("failed to get timestamps: %w", err)
	}

	return nil
}

// List retrieves all configs
func (r *ConfigRepository) List(ctx context.Context) ([]*models.GlobalConfig, error) {
	query := `
		SELECT id, ` + "`key`" + `, value, description, created_at, updated_at
		FROM global_configs
		ORDER BY ` + "`key`" + ` ASC
	`
	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to list configs: %w", err)
	}
	defer rows.Close()

	var configs []*models.GlobalConfig
	for rows.Next() {
		config := &models.GlobalConfig{}
		err := rows.Scan(
			&config.ID, &config.Key, &config.Value, &config.Description,
			&config.CreatedAt, &config.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan config: %w", err)
		}
		configs = append(configs, config)
	}

	return configs, nil
}

// Delete deletes a config by key
func (r *ConfigRepository) Delete(ctx context.Context, key string) error {
	query := `DELETE FROM global_configs WHERE ` + "`key`" + ` = ?`
	_, err := r.db.ExecContext(ctx, query, key)
	if err != nil {
		return fmt.Errorf("failed to delete config: %w", err)
	}
	return nil
}
