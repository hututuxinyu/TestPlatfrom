## ADDED Requirements

### Requirement: Upload and store test scripts
The system SHALL allow users to upload test scripts and persist both script files and metadata.

#### Scenario: Upload supported script file
- **WHEN** a user uploads a script file in a supported format
- **THEN** the system stores the file in script storage and creates a script metadata record
- **AND** the response returns script identifier and parsed basic attributes

#### Scenario: Reject unsupported script format
- **WHEN** a user uploads a script file with unsupported format or invalid structure
- **THEN** the system rejects the upload with validation error details
- **AND** no script metadata record is created

### Requirement: Manage script metadata lifecycle
The system SHALL support create, read, update, and delete operations for test script metadata.

#### Scenario: Update script metadata
- **WHEN** a user updates script metadata fields such as name, description, category, or tags
- **THEN** the system persists the updated metadata
- **AND** the system records the update time

#### Scenario: Delete script metadata
- **WHEN** a user deletes a script entry
- **THEN** the system removes metadata and marks associated script file as deleted or archived
- **AND** deleted script is no longer returned in active script list

### Requirement: Search and filter script catalog
The system SHALL provide script listing with filtering and keyword search.

#### Scenario: Filter by script type and status
- **WHEN** a user applies filters for script type and status in script list
- **THEN** the system returns only scripts matching all selected filters
- **AND** the response includes pagination metadata

#### Scenario: Search by script name keyword
- **WHEN** a user searches using a keyword in script list
- **THEN** the system returns scripts whose names or descriptions match the keyword
- **AND** the results are sorted by update time descending by default
