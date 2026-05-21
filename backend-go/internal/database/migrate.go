package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"
)

func RunMigrations(db *sql.DB) error {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := createUsersTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create users table: %w", err)
	}

	if err := createTestScriptsTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create test_scripts table: %w", err)
	}

	if err := createTestExecutionsTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create test_executions table: %w", err)
	}

	if err := createExecutionLogsTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create execution_logs table: %w", err)
	}

	if err := createGlobalConfigsTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create global_configs table: %w", err)
	}

	if err := createTestSuitesTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create test_suites table: %w", err)
	}

	if err := createTestTasksTable(ctx, db); err != nil {
		return fmt.Errorf("failed to create test_tasks table: %w", err)
	}

	return nil
}

func tableExists(ctx context.Context, db *sql.DB, tableName string) (bool, error) {
	query := `SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = ?`
	var count int
	err := db.QueryRowContext(ctx, query, tableName).Scan(&count)
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

func columnExists(ctx context.Context, db *sql.DB, tableName, columnName string) (bool, error) {
	query := `SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = ? AND column_name = ?`
	var count int
	err := db.QueryRowContext(ctx, query, tableName, columnName).Scan(&count)
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

func indexExists(ctx context.Context, db *sql.DB, tableName, indexName string) (bool, error) {
	query := `SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE() AND table_name = ? AND index_name = ?`
	var count int
	err := db.QueryRowContext(ctx, query, tableName, indexName).Scan(&count)
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

func createUsersTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "users")
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	query := `
	CREATE TABLE users (
		id INT AUTO_INCREMENT PRIMARY KEY,
		username VARCHAR(255) NOT NULL UNIQUE,
		password VARCHAR(255) NOT NULL,
		email VARCHAR(255),
		is_active BOOLEAN DEFAULT TRUE,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	_, err = db.ExecContext(ctx, `CREATE INDEX idx_users_username ON users(username)`)
	return err
}

func createTestScriptsTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "test_scripts")
	if err != nil {
		return err
	}
	if exists {
		if err := addColumnIfNotExists(ctx, db, "test_scripts", "uuid", "VARCHAR(36) NOT NULL DEFAULT ''"); err != nil {
			return err
		}
		if err := addColumnIfNotExists(ctx, db, "test_scripts", "suite_id", "INT NULL"); err != nil {
			return err
		}
		if err := addColumnIfNotExists(ctx, db, "test_scripts", "content", "LONGTEXT"); err != nil {
			return err
		}
		return nil
	}

	query := `
	CREATE TABLE test_scripts (
		id INT AUTO_INCREMENT PRIMARY KEY,
		uuid VARCHAR(36) NOT NULL DEFAULT '',
		name VARCHAR(255) NOT NULL,
		description TEXT,
		language VARCHAR(50) NOT NULL,
		file_path VARCHAR(512) NOT NULL,
		file_size BIGINT NOT NULL DEFAULT 0,
		file_hash VARCHAR(64),
		content LONGTEXT,
		suite_id INT NULL,
		tags VARCHAR(255),
		created_by INTEGER,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		CONSTRAINT fk_script_suite FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
		CONSTRAINT fk_script_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	indexes := []string{
		`CREATE INDEX idx_test_scripts_suite_id ON test_scripts(suite_id)`,
		`CREATE INDEX idx_test_scripts_language ON test_scripts(language)`,
		`CREATE INDEX idx_test_scripts_created_at ON test_scripts(created_at DESC)`,
	}
	for _, idx := range indexes {
		_, err = db.ExecContext(ctx, idx)
		if err != nil {
			return err
		}
	}
	return nil
}

func createTestExecutionsTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "test_executions")
	if err != nil {
		return err
	}
	if exists {
		if err := addColumnIfNotExists(ctx, db, "test_executions", "task_id", "INT NULL"); err != nil {
			return err
		}
		if err := addColumnIfNotExists(ctx, db, "test_executions", "script_uuid", "VARCHAR(36) NOT NULL DEFAULT ''"); err != nil {
			return err
		}
		if err := addColumnIfNotExists(ctx, db, "test_executions", "log_content", "TEXT"); err != nil {
			return err
		}
		return nil
	}

	query := `
	CREATE TABLE test_executions (
		id INT AUTO_INCREMENT PRIMARY KEY,
		task_id INT NULL,
		script_id INT NOT NULL,
		script_uuid VARCHAR(36) NOT NULL DEFAULT '',
		script_name VARCHAR(255) NOT NULL,
		status VARCHAR(50) NOT NULL DEFAULT 'pending',
		exit_code INT,
		started_at TIMESTAMP NULL,
		completed_at TIMESTAMP NULL,
		duration_seconds DOUBLE,
		created_by INTEGER,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT chk_execution_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'stopped')),
		CONSTRAINT fk_execution_task FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE SET NULL,
		CONSTRAINT fk_execution_script FOREIGN KEY (script_id) REFERENCES test_scripts(id) ON DELETE CASCADE,
		CONSTRAINT fk_execution_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	indexes := []string{
		`CREATE INDEX idx_test_executions_task_id ON test_executions(task_id)`,
		`CREATE INDEX idx_test_executions_script_id ON test_executions(script_id)`,
		`CREATE INDEX idx_test_executions_status ON test_executions(status)`,
		`CREATE INDEX idx_test_executions_created_at ON test_executions(created_at DESC)`,
	}
	for _, idx := range indexes {
		_, err = db.ExecContext(ctx, idx)
		if err != nil {
			return err
		}
	}
	return nil
}

func createExecutionLogsTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "execution_logs")
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	query := `
	CREATE TABLE execution_logs (
		id INT AUTO_INCREMENT PRIMARY KEY,
		execution_id INT NOT NULL,
		log_type VARCHAR(50) NOT NULL,
		content TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		CONSTRAINT chk_log_type CHECK (log_type IN ('stdout', 'stderr', 'system')),
		CONSTRAINT fk_log_execution FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	_, err = db.ExecContext(ctx, `CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id)`)
	return err
}

func createGlobalConfigsTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "global_configs")
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	query := `
	CREATE TABLE global_configs (
		id INT AUTO_INCREMENT PRIMARY KEY,
		key VARCHAR(255) NOT NULL UNIQUE,
		value TEXT NOT NULL,
		description VARCHAR(255),
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	_, err = db.ExecContext(ctx, `CREATE INDEX idx_global_configs_key ON global_configs(key)`)
	return err
}

func createTestSuitesTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "test_suites")
	if err != nil {
		return err
	}
	if exists {
		return nil
	}

	query := `
	CREATE TABLE test_suites (
		id INT AUTO_INCREMENT PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		created_by INTEGER,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
		CONSTRAINT fk_suite_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	_, err = db.ExecContext(ctx, `CREATE INDEX idx_test_suites_created_at ON test_suites(created_at DESC)`)
	return err
}

func createTestTasksTable(ctx context.Context, db *sql.DB) error {
	exists, err := tableExists(ctx, db, "test_tasks")
	if err != nil {
		return err
	}
	if exists {
		if err := addColumnIfNotExists(ctx, db, "test_tasks", "task_type", "VARCHAR(50) NOT NULL DEFAULT 'suite_batch'"); err != nil {
			return err
		}
		if err := modifyColumnIfExists(ctx, db, "test_tasks", "suite_id", "INT NULL"); err != nil {
			return err
		}
		if err := addIndexIfNotExists(ctx, db, "test_tasks", "idx_test_tasks_task_type", "task_type"); err != nil {
			return err
		}
		return nil
	}

	query := `
	CREATE TABLE test_tasks (
		id INT AUTO_INCREMENT PRIMARY KEY,
		task_type VARCHAR(50) NOT NULL DEFAULT 'suite_batch',
		suite_id INT NULL,
		suite_name VARCHAR(255) NOT NULL,
		status VARCHAR(50) NOT NULL DEFAULT 'pending',
		total_count INT NOT NULL DEFAULT 0,
		success_count INT NOT NULL DEFAULT 0,
		failed_count INT NOT NULL DEFAULT 0,
		created_by INTEGER,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		completed_at TIMESTAMP NULL,
		CONSTRAINT chk_task_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'stopped')),
		CONSTRAINT chk_task_type CHECK (task_type IN ('single_script', 'suite_batch')),
		CONSTRAINT fk_task_suite FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE SET NULL,
		CONSTRAINT fk_task_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci`

	_, err = db.ExecContext(ctx, query)
	if err != nil {
		return err
	}

	indexes := []string{
		`CREATE INDEX idx_test_tasks_suite_id ON test_tasks(suite_id)`,
		`CREATE INDEX idx_test_tasks_status ON test_tasks(status)`,
		`CREATE INDEX idx_test_tasks_task_type ON test_tasks(task_type)`,
		`CREATE INDEX idx_test_tasks_created_at ON test_tasks(created_at DESC)`,
	}
	for _, idx := range indexes {
		_, err = db.ExecContext(ctx, idx)
		if err != nil {
			return err
		}
	}
	return nil
}

func addColumnIfNotExists(ctx context.Context, db *sql.DB, tableName, columnName, columnDef string) error {
	exists, err := columnExists(ctx, db, tableName, columnName)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}
	query := fmt.Sprintf("ALTER TABLE %s ADD COLUMN %s %s", tableName, columnName, columnDef)
	_, err = db.ExecContext(ctx, query)
	return err
}

func modifyColumnIfExists(ctx context.Context, db *sql.DB, tableName, columnName, columnDef string) error {
	exists, err := columnExists(ctx, db, tableName, columnName)
	if err != nil {
		return err
	}
	if !exists {
		return nil
	}
	query := fmt.Sprintf("ALTER TABLE %s MODIFY COLUMN %s %s", tableName, columnName, columnDef)
	_, err = db.ExecContext(ctx, query)
	return err
}

func addIndexIfNotExists(ctx context.Context, db *sql.DB, tableName, indexName, columns string) error {
	exists, err := indexExists(ctx, db, tableName, indexName)
	if err != nil {
		return err
	}
	if exists {
		return nil
	}
	query := fmt.Sprintf("CREATE INDEX %s ON %s(%s)", indexName, tableName, columns)
	_, err = db.ExecContext(ctx, query)
	return err
}