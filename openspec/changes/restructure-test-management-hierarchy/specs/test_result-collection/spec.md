## MODIFIED Requirements

### Requirement: Collect execution logs
The system SHALL collect and persist logs generated during script execution.

#### Scenario: Capture standard output and error streams
- **WHEN** a script execution is running
- **THEN** the system captures stdout and stderr streams in near real-time
- **AND** logs are persisted with timestamped entries

#### Scenario: Retrieve execution logs
- **WHEN** a user opens execution details
- **THEN** the system returns stored logs for the selected execution
- **AND** the response supports pagination or range retrieval for large logs

### Requirement: Collect artifacts from execution
The system SHALL collect execution artifacts including screenshots and media outputs when available.

#### Scenario: Store screenshot artifacts
- **WHEN** execution produces screenshots
- **THEN** the system stores screenshot files with references to execution and step identifiers
- **AND** screenshot metadata includes capture time and source step

#### Scenario: Store media recording artifacts
- **WHEN** E2E execution produces media recordings
- **THEN** the system stores recording file references and duration metadata
- **AND** recordings are retrievable from execution result details

### Requirement: Aggregate result data
The system SHALL aggregate raw execution outputs into normalized result records for reporting.

#### Scenario: Build execution result summary
- **WHEN** execution reaches terminal state
- **THEN** the system calculates summary fields including final status, duration, and step counts
- **AND** the system links summary to collected logs and artifacts

#### Scenario: Aggregate batch execution outcomes
- **WHEN** a batch execution (task) completes
- **THEN** the system aggregates passed/failed totals across all suites in the task
- **AND** the system stores aggregate result for report generation
- **AND** suite-level aggregates are also calculated
