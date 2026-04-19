CREATE TABLE IF NOT EXISTS execution_logs (
    id SERIAL PRIMARY KEY,
    execution_id INTEGER NOT NULL REFERENCES test_executions(id) ON DELETE CASCADE,
    log_type VARCHAR(20) NOT NULL CHECK (log_type IN ('system', 'stdout', 'stderr')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX idx_execution_logs_created_at ON execution_logs(created_at DESC);
CREATE INDEX idx_execution_logs_log_type ON execution_logs(log_type);
