ALTER TABLE test_executions ADD COLUMN task_id INT;
ALTER TABLE test_executions ADD COLUMN script_uuid VARCHAR(36) NOT NULL DEFAULT '';

CREATE INDEX idx_test_executions_task_id ON test_executions(task_id);

ALTER TABLE test_executions ADD CONSTRAINT fk_execution_task FOREIGN KEY (task_id) REFERENCES test_tasks(id) ON DELETE CASCADE;
