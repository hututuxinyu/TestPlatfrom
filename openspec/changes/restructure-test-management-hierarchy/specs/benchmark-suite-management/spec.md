## ADDED Requirements

### Requirement: Create benchmark suite
The system SHALL allow users to create a benchmark suite to group related test scripts.

#### Scenario: Create suite with name and description
- **WHEN** a user creates a benchmark suite with name and description
- **THEN** the system creates a suite record with generated ID
- **AND** the suite is initially empty (no scripts)

#### Scenario: Create suite with initial scripts
- **WHEN** a user creates a benchmark suite and specifies initial script IDs
- **THEN** the system creates a suite record and associates the specified scripts
- **AND** each script relationship is recorded

### Requirement: Add scripts to suite
The system SHALL allow users to add test scripts to an existing benchmark suite.

#### Scenario: Add single script to suite
- **WHEN** a user adds a script ID to a benchmark suite
- **THEN** the system creates a suite-script association
- **AND** duplicate associations are prevented

#### Scenario: Add multiple scripts to suite
- **WHEN** a user adds multiple script IDs to a benchmark suite
- **THEN** the system creates associations for all specified scripts
- **AND** existing associations are preserved

### Requirement: Remove scripts from suite
The system SHALL allow users to remove test scripts from a benchmark suite.

#### Scenario: Remove script from suite
- **WHEN** a user removes a script from a benchmark suite
- **THEN** the system deletes the suite-script association
- **AND** existing execution records are preserved

### Requirement: List benchmark suites
The system SHALL provide a list of all benchmark suites.

#### Scenario: List all suites
- **WHEN** a user requests the benchmark suite list
- **THEN** the system returns all suites with script count
- **AND** suites are sorted by created_at DESC

#### Scenario: List suites by task
- **WHEN** a user requests suites for a specific task
- **THEN** the system returns only suites associated with that task

### Requirement: Get benchmark suite details
The system SHALL provide detailed information about a specific benchmark suite.

#### Scenario: Get suite with scripts
- **WHEN** a user requests benchmark suite details
- **THEN** the system returns suite metadata including associated scripts
- **AND** execution statistics for each script are included

#### Scenario: Suite not found
- **WHEN** a user requests a non-existent benchmark suite
- **THEN** the system returns 404 error

### Requirement: Update benchmark suite
The system SHALL allow users to update suite metadata.

#### Scenario: Update suite name/description
- **WHEN** a user updates a benchmark suite's name or description
- **THEN** the system updates the corresponding fields
- **AND** updated_at timestamp is refreshed

### Requirement: Delete benchmark suite
The system SHALL allow users to delete a benchmark suite.

#### Scenario: Delete suite with associations
- **WHEN** a user deletes a benchmark suite
- **THEN** the system removes the suite and all its script associations
- **AND** associated execution records are preserved (orphaned but queryable)
