CREATE TABLE IF NOT EXISTS execution_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    execution_id INTEGER NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_log_type CHECK (log_type IN ('system', 'stdout', 'stderr')),
    CONSTRAINT fk_execution_id FOREIGN KEY (execution_id) REFERENCES test_executions(id) ON DELETE CASCADE
);

-- Create indexes for common queries
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_created_at ON execution_logs(created_at DESC);
CREATE INDEX idx_execution_logs_log_type ON execution_logs(log_type);
