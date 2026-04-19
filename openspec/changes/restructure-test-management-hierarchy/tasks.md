## 1. Database Migrations

- [ ] 1.1 Create migration for `tasks` table (id, name, description, status, created_by, created_at, updated_at)
- [ ] 1.2 Create migration for `benchmark_suites` table (id, name, description, task_id, created_by, created_at, updated_at)
- [ ] 1.3 Create migration to add `task_id` and `suite_id` columns to `test_executions` table
- [ ] 1.4 Create migration for `suite_scripts` junction table (suite_id, script_id)
- [ ] 1.5 Verify all migrations run correctly

## 2. Backend - Models

- [ ] 2.1 Create Task model in `internal/models/task.go`
- [ ] 2.2 Create BenchmarkSuite model in `internal/models/benchmark_suite.go`
- [ ] 2.3 Create SuiteScript junction model in `internal/models/suite_script.go`
- [ ] 2.4 Update TestExecution model to include TaskID and SuiteID fields

## 3. Backend - Repositories

- [ ] 3.1 Implement TaskRepository (Create, GetByID, List, Update, Delete)
- [ ] 3.2 Implement BenchmarkSuiteRepository (Create, GetByID, List, AddScripts, RemoveScripts, Update, Delete)
- [ ] 3.3 Implement SuiteScriptRepository (AddScript, RemoveScript, GetBySuiteID)
- [ ] 3.4 Update ExecutionRepository to support task_id and suite_id filtering

## 4. Backend - Handlers

- [ ] 4.1 Create TaskHandler with endpoints: GET /tasks, POST /tasks, GET /tasks/:id, DELETE /tasks/:id
- [ ] 4.2 Create SuiteHandler with endpoints: GET /suites, POST /suites, GET /suites/:id, PUT /suites/:id, DELETE /suites/:id, POST /suites/:id/scripts
- [ ] 4.3 Update ExecutionHandler to accept suite_id and task_id parameters
- [ ] 4.4 Register new handlers in server router

## 5. Backend - Services

- [ ] 5.1 Create TaskService with status aggregation logic
- [ ] 5.2 Create BenchmarkSuiteService
- [ ] 5.3 Update ExecutorService to support suite-level execution
- [ ] 5.4 Update status calculation to propagate to task level

## 6. Frontend - API Client

- [ ] 6.1 Add Task API methods (list, get, create, delete)
- [ ] 6.2 Add BenchmarkSuite API methods (list, get, create, update, delete, addScripts)
- [ ] 6.3 Update Execution API to support task_id and suite_id filters

## 7. Frontend - Task Management Page

- [ ] 7.1 Create TaskListPage component with table view
- [ ] 7.2 Create TaskDetailPage component showing suites and execution status
- [ ] 7.3 Create TaskCreateModal for creating new tasks
- [ ] 7.4 Implement task status aggregation display (progress bar, counts)

## 8. Frontend - Benchmark Suite Management

- [ ] 8.1 Create SuiteListPage component
- [ ] 8.2 Create SuiteDetailPage showing scripts and execution history
- [ ] 8.3 Create SuiteCreateModal for creating new suites
- [ ] 8.4 Implement script selection UI for adding scripts to suite

## 9. Frontend - Execution Management Updates

- [ ] 9.1 Update ExecutionListPage to show task hierarchy
- [ ] 9.2 Update ExecutionDetailPage to show suite context
- [ ] 9.3 Add suite execution button on suite detail page

## 10. Testing & Verification

- [ ] 10.1 Write database migration tests
- [ ] 10.2 Write repository unit tests
- [ ] 10.3 Write handler integration tests
- [ ] 10.4 Manual testing: Create task → Add suite → Add scripts → Execute suite → View results
