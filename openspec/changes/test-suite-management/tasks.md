## 1. Database Migration

- [x] 1.1 Create `test_suites` table migration
- [x] 1.2 Add `suite_id` and `uuid` columns to `test_scripts` table
- [x] 1.3 Create `test_tasks` table migration
- [x] 1.4 Add `task_id` and `script_uuid` columns to `test_executions` table
- [x] 1.5 Add foreign key constraints

## 2. Backend - Models

- [x] 2.1 Create `TestSuite` model struct
- [x] 2.2 Create `TestTask` model struct
- [x] 2.3 Update `TestScript` model with `SuiteID` and `UUID` fields
- [x] 2.4 Update `TestExecution` model with `TaskID` and `ScriptUUID` fields

## 3. Backend - Repository Layer

- [x] 3.1 Create `SuiteRepository` with CRUD operations
- [x] 3.2 Create `TaskRepository` with CRUD operations
- [x] 3.3 Update `ScriptRepository` to support suite_id and uuid
- [x] 3.4 Update `ExecutionRepository` to support task_id
- [x] 3.5 Add `DeleteBySuiteID` method to ScriptRepository
- [x] 3.6 Add `ListBySuiteID` method to ScriptRepository

## 4. Backend - Handlers

- [x] 4.1 Create `SuiteHandler` with:
  - [x] 4.1.1 List (GET /api/v1/suites)
  - [x] 4.1.2 Create with ZIP upload (POST /api/v1/suites)
  - [x] 4.1.3 Get (GET /api/v1/suites/:id)
  - [x] 4.1.4 Update/Rename (PUT /api/v1/suites/:id)
  - [x] 4.1.5 Delete (DELETE /api/v1/suites/:id)
  - [x] 4.1.6 List suite scripts (GET /api/v1/suites/:id/scripts)
  - [x] 4.1.7 Upload script to suite (POST /api/v1/suites/:id/scripts)
  - [x] 4.1.8 Export suite to ZIP (GET /api/v1/suites/:id/export)

- [x] 4.2 Create `TaskHandler` with:
  - [x] 4.2.1 List (GET /api/v1/tasks)
  - [x] 4.2.2 Get (GET /api/v1/tasks/:id)
  - [x] 4.2.3 Stop task (POST /api/v1/tasks/:id/stop)
  - [x] 4.2.4 List task executions (GET /api/v1/tasks/:id/executions)

- [x] 4.3 Update `ExecutionHandler`:
  - [x] 4.3.1 Add task_id filter to List
  - [x] 4.3.2 Add task_id and script_uuid to execution records

## 5. Backend - Executor Changes

- [x] 5.1 Update executor to accept task_id
- [x] 5.2 Add task statistics update on execution complete
- [x] 5.3 Implement task stop signal mechanism
- [x] 5.4 Create task on suite batch execution

## 6. Backend - Routes

- [x] 6.1 Register suite routes in router
- [x] 6.2 Register task routes in router
- [x] 6.3 Update existing script routes to support suite_id

## 7. Frontend - API Service

- [x] 7.1 Add suite API methods:
  - [x] 7.1.1 listSuites()
  - [x] 7.1.2 createSuite(formData)
  - [x] 7.1.3 getSuite(id)
  - [x] 7.1.4 updateSuite(id, data)
  - [x] 7.1.5 deleteSuite(id)
  - [x] 7.1.6 listSuiteScripts(suiteId)
  - [x] 7.1.7 uploadScriptToSuite(suiteId, file)
  - [x] 7.1.8 exportSuite(suiteId)

- [x] 7.2 Add task API methods:
  - [x] 7.2.1 listTasks(params)
  - [x] 7.2.2 getTask(id)
  - [x] 7.2.3 stopTask(id)
  - [x] 7.2.4 listTaskExecutions(taskId)

## 8. Frontend - Suite Management Page

- [x] 8.1 Create suite card grid view component
- [x] 8.2 Implement suite card with preview/export/delete buttons
- [x] 8.3 Implement upload suite ZIP modal
- [x] 8.4 Implement suite rename modal
- [x] 8.5 Add route for suite detail view (/scripts/:suiteId)

## 9. Frontend - Suite Detail View

- [x] 9.1 Reuse existing script table component
- [x] 9.2 Filter scripts by current suite_id
- [x] 9.3 Add "返回" button to go back to suite grid
- [x] 9.4 Add "上传脚本" button in suite view
- [x] 9.5 Add "一键执行" button in suite view
- [x] 9.6 Add upload script modal (single file)

## 10. Frontend - Execution Management Page

- [x] 10.1 Update execution page with task dropdown
- [x] 10.2 Implement task filtering by suite
- [x] 10.3 Display task summary in dropdown (suite + time + stats)
- [x] 10.4 Add task stop button
- [x] 10.5 Show execution records for selected task

## 11. Integration Testing

- [ ] 11.1 Test suite creation via ZIP upload
- [ ] 11.2 Test suite deletion (delete scripts first, then suite)
- [ ] 11.3 Test suite export
- [ ] 11.4 Test suite batch execution creates task
- [ ] 11.5 Test task stop functionality
- [ ] 11.6 Test task dropdown filtering
