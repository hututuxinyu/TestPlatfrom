ALTER TABLE test_executions DROP FOREIGN KEY fk_execution_task;
ALTER TABLE test_executions DROP COLUMN task_id;
ALTER TABLE test_executions DROP COLUMN script_uuid;
