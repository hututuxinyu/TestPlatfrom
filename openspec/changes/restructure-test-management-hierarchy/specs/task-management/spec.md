## ADDED Requirements

### Requirement: Create task
The system SHALL allow users to create a new task for organizing test execution.

#### Scenario: Create task with评测集
- **WHEN** a user creates a task and specifies one or more benchmark suites
- **THEN** the system creates a task record with status `pending`
- **AND** the task is associated with the specified benchmark suites

#### Scenario: Create empty task
- **WHEN** a user creates a task without specifying benchmark suites
- **THEN** the system creates a task record with status `pending`
- **AND** benchmark suites can be added later

### Requirement: List tasks
The system SHALL provide a paginated list of all tasks.

#### Scenario: List tasks with pagination
- **WHEN** a user requests the task list
- **THEN** the system returns tasks sorted by created_at DESC
- **AND** the response includes task status, total suites count, completed suites count

#### Scenario: Filter tasks by status
- **WHEN** a user filters tasks by status
- **THEN** the system returns only tasks matching the specified status

### Requirement: Get task details
The system SHALL provide detailed information about a specific task.

#### Scenario: Get task with suites summary
- **WHEN** a user requests task details
- **THEN** the system returns task metadata including all associated benchmark suites
- **AND** each suite includes execution statistics (total, completed, failed)

#### Scenario: Task not found
- **WHEN** a user requests a non-existent task
- **THEN** the system returns 404 error

### Requirement: Task status aggregation
The system SHALL aggregate the status of child benchmark suites to determine task status.

#### Scenario: Calculate task status from suites
- **WHEN** task status is queried
- **THEN** the system calculates status based on suite statuses:
  - `pending`: all suites are pending
  - `running`: any suite is running
  - `completed`: all suites are completed with no failures
  - `failed`: any suite is failed or stopped
  - `partial`: some suites completed, some failed

### Requirement: Delete task
The system SHALL allow users to delete a task and optionally its associated execution records.

#### Scenario: Delete task with executions
- **WHEN** a user deletes a task
- **THEN** the system deletes the task and optionally all associated suite executions
- **AND** benchmark suites themselves are not deleted (they can be reused)
