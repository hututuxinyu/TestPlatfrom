ALTER TABLE test_scripts ADD COLUMN suite_id INT;
ALTER TABLE test_scripts ADD COLUMN uuid VARCHAR(36) NOT NULL;

CREATE INDEX idx_test_scripts_suite_id ON test_scripts(suite_id);
CREATE INDEX idx_test_scripts_uuid ON test_scripts(uuid);

ALTER TABLE test_scripts ADD CONSTRAINT fk_script_suite FOREIGN KEY (suite_id) REFERENCES test_suites(id) ON DELETE CASCADE;
