## ADDED Requirements

### Requirement: Script name auto-extraction from filename
The system SHALL automatically extract the script name from the uploaded filename when processing script uploads. The extracted name SHALL be used as the test script's name in the database.

#### Scenario: Upload with standard filename
- **WHEN** user uploads a script file with name `TC_SBG_Func_GIDS_001_004_optimized.py`
- **THEN** system SHALL store `TC_SBG_Func_GIDS_001_004_optimized` as the script name in the database

#### Scenario: Upload with simple filename
- **WHEN** user uploads a script file with name `test.py`
- **THEN** system SHALL store `test` as the script name in the database

### Requirement: Frontend upload form simplification
The frontend script upload form SHALL NOT require users to manually enter a script name. The name field SHALL be removed from the upload form.

#### Scenario: Upload form displays without name field
- **WHEN** user navigates to the script upload page
- **THEN** the upload form SHALL NOT contain a "name" or "名称" input field
- **AND** user only needs to select a file to upload

### Requirement: Upload API processes filename-only
The backend upload API endpoint SHALL derive the script name solely from the uploaded file's filename, ignoring any `name` field in the request body.

#### Scenario: Upload API ignores name parameter
- **WHEN** backend receives a script upload request
- **THEN** backend SHALL use the filename from the uploaded file as the script name
- **AND** any `name` field in the multipart form data SHALL be ignored
