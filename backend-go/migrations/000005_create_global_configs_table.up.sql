CREATE TABLE IF NOT EXISTS global_configs (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for key lookups
CREATE INDEX idx_global_configs_key ON global_configs(key);

-- Insert default configurations
INSERT INTO global_configs (key, value, description)
VALUES
    ('max_concurrent_executions', '100', 'Maximum number of concurrent test executions'),
    ('default_timeout_seconds', '3600', 'Default timeout for test execution in seconds'),
    ('log_retention_days', '30', 'Number of days to retain execution logs')
ON CONFLICT (key) DO NOTHING;
