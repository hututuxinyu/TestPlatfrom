## MODIFIED Requirements

### Requirement: Execute single test script
The system SHALL support triggering execution of one selected test script.

#### Scenario: Start single execution
- **WHEN** a user triggers execution for a script from the script list
- **THEN** the system creates an execution record with status `pending` and transitions it to `running`
- **AND** the system starts the corresponding execution engine based on script type
- **AND** if suite_id is provided, the execution is linked to the suite

#### Scenario: Complete single execution
- **WHEN** a running execution finishes
- **THEN** the system updates execution status to `completed` or `failed`
- **AND** the system stores exit code, duration, and summary result
- **AND** suite and task status are recalculated

### Requirement: Execute scripts in batch mode
The system SHALL support batch execution for multiple selected scripts with queue-based scheduling.

#### Scenario: Submit batch execution request
- **WHEN** a user selects multiple scripts and starts batch execution
- **THEN** the system creates a task and enqueues each script execution task
- **AND** the system returns a task identifier for progress tracking

#### Scenario: Process queued batch tasks
- **WHEN** batch tasks are processed by workers
- **THEN** the system executes tasks according to configured concurrency limits
- **AND** each task status is tracked independently
- **AND** each execution is linked to the task

### Requirement: Execution control operations
The system SHALL provide control operations for running executions, including stop and retry.

#### Scenario: Stop running execution
- **WHEN** a user issues stop command for a running execution
- **THEN** the system terminates the execution process safely
- **AND** the execution status changes to `stopped` with stop reason recorded
- **AND** task/suite status is recalculated

#### Scenario: Retry failed execution
- **WHEN** a user retries a failed execution
- **THEN** the system creates a new execution attempt linked to the original execution
- **AND** the new attempt starts with status `pending`
- **AND** the new execution references the same task and suite (if applicable)
