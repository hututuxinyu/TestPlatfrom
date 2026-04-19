## ADDED Requirements

### Requirement: Execute all scripts in a评测集
The system SHALL support executing all scripts in a benchmark suite as a single operation.

#### Scenario: Execute entire suite
- **WHEN** a user triggers execution for an entire benchmark suite
- **THEN** the system creates a task (if not exists) and starts execution for all scripts in the suite
- **AND** each script execution is linked to the task and suite

#### Scenario: Execute suite within existing task
- **WHEN** a user triggers suite execution within an existing task
- **THEN** the system starts execution for all scripts in the suite
- **AND** all executions are linked to the specified task

### Requirement: Track hierarchical execution status
The system SHALL track execution status at task, suite, and individual script levels.

#### Scenario: Task shows aggregated progress
- **WHEN** executions are running within a task
- **THEN** the task status reflects overall progress
- **AND** the response includes completed/total counts

#### Scenario: Suite shows individual script statuses
- **WHEN** a user views suite execution status
- **THEN** the system returns status for each script in the suite
- **AND** suite-level aggregation (passed/failed/total) is included

### Requirement: Execute single script within suite context
The system SHALL support executing a single script while maintaining suite context.

#### Scenario: Execute one script in suite
- **WHEN** a user triggers execution for a single script and specifies a suite ID
- **THEN** the system creates an execution linked to both the script and suite
- **AND** the execution is also linked to the current task (if specified)

### Requirement: Cancel task execution
The system SHALL support cancelling all executions within a task.

#### Scenario: Cancel entire task
- **WHEN** a user issues cancel command for a task
- **THEN** the system terminates all running executions within that task
- **AND** task status changes to `cancelled`

#### Scenario: Cancel single suite in task
- **WHEN** a user issues cancel command for a specific suite in a task
- **THEN** the system terminates only the running executions in that suite
- **AND** other suites continue execution
