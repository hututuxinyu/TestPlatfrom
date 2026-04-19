CREATE TABLE IF NOT EXISTS test_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    script_id INTEGER NOT NULL,
    script_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    exit_code INTEGER,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    duration_seconds DECIMAL(10, 2),
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'stopped')),
    CONSTRAINT fk_script_id FOREIGN KEY (script_id) REFERENCES test_scripts(id) ON DELETE CASCADE,
    CONSTRAINT fk_execution_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for common queries
CREATE INDEX idx_test_executions_script_id ON test_executions(script_id);
CREATE INDEX idx_test_executions_status ON test_executions(status);
CREATE INDEX idx_test_executions_created_at ON test_executions(created_at DESC);
CREATE INDEX idx_test_executions_created_by ON test_executions(created_by);
