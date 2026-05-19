# Test Suite Management

## ADDED Requirements

### Requirement: Suite name uniqueness
The system SHALL ensure suite names are unique across all suites.

#### Scenario: Creating suite with duplicate name fails
- **WHEN** user creates a suite with name "HTTP接口套" that already exists
- **THEN** system returns error "Suite name already exists"

### Requirement: Suite creation via ZIP upload
The system SHALL allow users to create a suite by uploading a ZIP file containing scripts.

#### Scenario: Successful ZIP upload creates suite
- **WHEN** user inputs suite name "HTTP接口套" and uploads a ZIP containing login.py and getUser.py
- **THEN** system creates the suite with 2 scripts stored in suite's directory

#### Scenario: ZIP upload failure leaves no trace
- **WHEN** ZIP upload fails midway (e.g., file read error)
- **THEN** system rolls back all created records and files, suite does not exist

### Requirement: Suite listing shows summary
The system SHALL display suite summary including: script count, total line count, latest upload time.

#### Scenario: Suite card displays correct summary
- **WHEN** user views suite list
- **THEN** each suite card shows: "[编号] 套名 | X个脚本 | Y行 | 上传时间: Z"

### Requirement: Suite rename
The system SHALL allow users to rename an existing suite.

#### Scenario: Successful rename
- **WHEN** user edits suite "HTTP接口套" to "HTTP测试套"
- **THEN** suite name is updated and new name is shown

### Requirement: Suite deletion requires deleting scripts first
The system SHALL require all scripts in a suite to be deleted before the suite can be deleted.

#### Scenario: Delete suite after deleting scripts
- **WHEN** user deletes all scripts in a suite, then deletes the suite
- **THEN** suite is removed and suite's directory is cleaned up

### Requirement: Suite export to ZIP
The system SHALL allow users to export all scripts in a suite as a ZIP file.

#### Scenario: Export suite creates valid ZIP
- **WHEN** user clicks "导出" on a suite with 3 scripts
- **THEN** system creates ZIP named "{suite_name}.zip" containing all 3 script files

### Requirement: Suite preview shows script list
The system SHALL display all scripts within a suite when user clicks "预览".

#### Scenario: Preview displays suite scripts
- **WHEN** user clicks "预览" on "HTTP接口套"
- **THEN** system navigates to suite detail view showing all scripts in a table
