## ADDED Requirements

### Requirement: Batch delete with confirmation
The system SHALL require manual "delete" input before executing batch deletion of scripts.

#### Scenario: Confirm batch delete
- **WHEN** user selects multiple scripts and clicks "Delete"
- **THEN** system displays a confirmation modal requiring user to type "delete"
- **AND** delete button is disabled until user types "delete"
- **AND** system deletes only the selected scripts when confirmed
