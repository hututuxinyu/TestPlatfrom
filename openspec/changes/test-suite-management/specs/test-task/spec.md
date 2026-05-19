# Test Task Management

## ADDED Requirements

### Requirement: Task created on batch execution
The system SHALL create a task record when suite batch execution is triggered.

#### Scenario: Task created with suite scripts
- **WHEN** user clicks "一键执行" on a suite with 5 scripts
- **THEN** a task record is created with total_count=5, status=pending

### Requirement: Task tracks execution statistics
The system SHALL update task success_count and failed_count as executions complete.

#### Scenario: Task counts updated on execution completion
- **WHEN** 3 scripts in a task complete successfully and 2 fail
- **THEN** task shows success_count=3, failed_count=2, status reflects final state

### Requirement: Task stop terminates all executions
The system SHALL stop all running executions when user stops a task.

#### Scenario: Stop task halts executions
- **WHEN** user clicks "停止" on a running task
- **THEN** task status becomes 'stopped' and all running executions are signaled to stop

### Requirement: Task listing for dropdown
The system SHALL list tasks grouped by suite with trigger time for dropdown selection.

#### Scenario: Task dropdown shows task summary
- **WHEN** user opens task dropdown in execution management
- **THEN** dropdown shows: "套名 - 触发时间 (成功 X/Y)"

### Requirement: Task filtering
The system SHALL allow filtering tasks by suite.

#### Scenario: Filter tasks by suite
- **WHEN** user selects a specific suite filter
- **THEN** only tasks belonging to that suite are shown

### Requirement: Task execution records
The system SHALL display all execution records belonging to a selected task.

#### Scenario: Task detail shows executions
- **WHEN** user selects a task from dropdown
- **THEN** execution table shows all executions for that task with: ID, 脚本名称, 状态, 耗时
