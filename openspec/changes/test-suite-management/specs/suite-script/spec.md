# Suite Script Management

## ADDED Requirements

### Requirement: Scripts belong to a single suite
Each script SHALL belong to exactly one suite at upload time.

#### Scenario: Script uploaded to specific suite
- **WHEN** user uploads script.py to "HTTP接口套"
- **THEN** script is associated with that suite and cannot appear in other suites

### Requirement: Suite can add individual scripts
The system SHALL allow users to upload individual script files to an existing suite.

#### Scenario: Add script to existing suite
- **WHEN** user is in suite detail view and clicks "上传脚本"
- **THEN** file picker opens, and selected file is added to current suite

### Requirement: Scripts displayed in suite detail view
The system SHALL display scripts belonging to a suite in a table view.

#### Scenario: Suite detail shows scripts
- **WHEN** user enters a suite
- **THEN** table displays columns: ID, 脚本名称, 语言, 操作

### Requirement: Script operations in suite view
The system SHALL allow executing, viewing, and deleting individual scripts within a suite.

#### Scenario: Execute single script
- **WHEN** user clicks "执行" on a script in suite view
- **THEN** execution record is created and script runs

#### Scenario: View script content
- **WHEN** user clicks "查看" on a script
- **THEN** modal displays script file content

#### Scenario: Delete script from suite
- **WHEN** user clicks "删除" on a script
- **THEN** script record and file are removed from suite

### Requirement: Suite batch execution
The system SHALL execute all scripts in a suite when user clicks "一键执行".

#### Scenario: Batch execute creates task
- **WHEN** user clicks "一键执行" in suite view
- **THEN** a task record is created and all suite scripts begin execution
