package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/testplatform/backend/internal/models"
)

type SuiteRepository struct {
	db *sql.DB
}

func NewSuiteRepository(db *sql.DB) *SuiteRepository {
	return &SuiteRepository{db: db}
}

// Create creates a new test suite
func (r *SuiteRepository) Create(ctx context.Context, suite *models.TestSuite) error {
	now := time.Now()
	suite.CreatedAt = now
	suite.UpdatedAt = now

	query := `
		INSERT INTO test_suites (name, created_by, created_at, updated_at)
		VALUES (?, ?, ?, ?)
	`
	result, err := r.db.ExecContext(ctx, query, suite.Name, suite.CreatedBy, suite.CreatedAt, suite.UpdatedAt)
	if err != nil {
		return fmt.Errorf("failed to create suite: %w", err)
	}

	id, err := result.LastInsertId()
	if err != nil {
		return fmt.Errorf("failed to get last insert id: %w", err)
	}
	suite.ID = int(id)

	return nil
}

// GetByID retrieves a suite by ID
func (r *SuiteRepository) GetByID(ctx context.Context, id int) (*models.TestSuite, error) {
	query := `
		SELECT id, name, created_by, created_at, updated_at
		FROM test_suites
		WHERE id = ?
	`
	suite := &models.TestSuite{}
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&suite.ID, &suite.Name, &suite.CreatedBy, &suite.CreatedAt, &suite.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get suite by id: %w", err)
	}
	return suite, nil
}

// GetByName retrieves a suite by name
func (r *SuiteRepository) GetByName(ctx context.Context, name string) (*models.TestSuite, error) {
	query := `
		SELECT id, name, created_by, created_at, updated_at
		FROM test_suites
		WHERE name = ?
	`
	suite := &models.TestSuite{}
	err := r.db.QueryRowContext(ctx, query, name).Scan(
		&suite.ID, &suite.Name, &suite.CreatedBy, &suite.CreatedAt, &suite.UpdatedAt,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get suite by name: %w", err)
	}
	return suite, nil
}

// Update updates a suite name
func (r *SuiteRepository) Update(ctx context.Context, suite *models.TestSuite) error {
	query := `
		UPDATE test_suites
		SET name = ?, updated_at = CURRENT_TIMESTAMP
		WHERE id = ?
	`
	_, err := r.db.ExecContext(ctx, query, suite.Name, suite.ID)
	if err != nil {
		return fmt.Errorf("failed to update suite: %w", err)
	}

	// Get updated timestamp
	query = `SELECT updated_at FROM test_suites WHERE id = ?`
	err = r.db.QueryRowContext(ctx, query, suite.ID).Scan(&suite.UpdatedAt)
	if err != nil {
		return fmt.Errorf("failed to get updated timestamp: %w", err)
	}

	return nil
}

// Delete deletes a suite
func (r *SuiteRepository) Delete(ctx context.Context, id int) error {
	query := `DELETE FROM test_suites WHERE id = ?`
	_, err := r.db.ExecContext(ctx, query, id)
	if err != nil {
		return fmt.Errorf("failed to delete suite: %w", err)
	}
	return nil
}

// List retrieves all suites
func (r *SuiteRepository) List(ctx context.Context) ([]*models.TestSuite, error) {
	query := `
		SELECT id, name, created_by, created_at, updated_at
		FROM test_suites
		ORDER BY created_at DESC
	`
	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to list suites: %w", err)
	}
	defer rows.Close()

	var suites []*models.TestSuite
	for rows.Next() {
		suite := &models.TestSuite{}
		err := rows.Scan(
			&suite.ID, &suite.Name, &suite.CreatedBy, &suite.CreatedAt, &suite.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan suite: %w", err)
		}
		suites = append(suites, suite)
	}

	return suites, nil
}

// SuiteSummary contains aggregated info for a suite
type SuiteSummary struct {
	ID           int    `json:"id"`
	Name         string `json:"name"`
	ScriptCount  int    `json:"script_count"`
	TotalLines   int    `json:"total_lines"`
	LatestUpload string `json:"latest_upload"`
}

// GetSummary retrieves suite with aggregated script info (only test_case scripts)
func (r *SuiteRepository) GetSummary(ctx context.Context, id int) (*SuiteSummary, error) {
	query := `
		SELECT
			s.id,
			s.name,
			COUNT(sc.id) as script_count,
			COALESCE(SUM(
				CASE 
					WHEN sc.content IS NOT NULL AND sc.content != '' 
					THEN LENGTH(sc.content) - LENGTH(REPLACE(sc.content, '\n', '')) + 1
					ELSE 0
				END
			), 0) as total_lines,
			MAX(sc.created_at) as latest_upload
		FROM test_suites s
		LEFT JOIN test_scripts sc ON s.id = sc.suite_id AND sc.script_type = 'test_case'
		WHERE s.id = ?
		GROUP BY s.id, s.name
	`
	summary := &SuiteSummary{}
	var latestUpload sql.NullString
	err := r.db.QueryRowContext(ctx, query, id).Scan(
		&summary.ID, &summary.Name, &summary.ScriptCount, &summary.TotalLines, &latestUpload,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to get suite summary: %w", err)
	}
	if latestUpload.Valid {
		summary.LatestUpload = latestUpload.String
	}
	return summary, nil
}

// ListSummaries retrieves all suites with aggregated script info (only test_case scripts)
func (r *SuiteRepository) ListSummaries(ctx context.Context) ([]*SuiteSummary, error) {
	query := `
		SELECT
			s.id,
			s.name,
			COUNT(sc.id) as script_count,
			COALESCE(SUM(
				CASE 
					WHEN sc.content IS NOT NULL AND sc.content != '' 
					THEN LENGTH(sc.content) - LENGTH(REPLACE(sc.content, '\n', '')) + 1
					ELSE 0
				END
			), 0) as total_lines,
			MAX(sc.created_at) as latest_upload
		FROM test_suites s
		LEFT JOIN test_scripts sc ON s.id = sc.suite_id AND sc.script_type = 'test_case'
		GROUP BY s.id, s.name
		ORDER BY s.created_at DESC
	`
	rows, err := r.db.QueryContext(ctx, query)
	if err != nil {
		return nil, fmt.Errorf("failed to list suite summaries: %w", err)
	}
	defer rows.Close()

	var summaries []*SuiteSummary
	for rows.Next() {
		summary := &SuiteSummary{}
		var latestUpload sql.NullString
		err := rows.Scan(
			&summary.ID, &summary.Name, &summary.ScriptCount, &summary.TotalLines, &latestUpload,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan suite summary: %w", err)
		}
		if latestUpload.Valid {
			summary.LatestUpload = latestUpload.String
		}
		summaries = append(summaries, summary)
	}

	return summaries, nil
}
