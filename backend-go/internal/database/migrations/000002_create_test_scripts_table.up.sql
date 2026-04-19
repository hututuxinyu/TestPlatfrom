CREATE TABLE IF NOT EXISTS test_scripts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    tags TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_language CHECK (language IN ('python', 'shell', 'javascript')),
    CONSTRAINT fk_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Create indexes for common queries
CREATE INDEX idx_test_scripts_language ON test_scripts(language);
CREATE INDEX idx_test_scripts_created_by ON test_scripts(created_by);
CREATE INDEX idx_test_scripts_created_at ON test_scripts(created_at DESC);
CREATE UNIQUE INDEX idx_test_scripts_name ON test_scripts(name);
