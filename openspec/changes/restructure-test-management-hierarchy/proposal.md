## Why

当前测试管理以单个脚本执行为粒度，缺少对测试组织的上层抽象。用户需要按照"任务-评测集-脚本"的层级结构来管理测试执行，以便更好地组织和查看批量测试的结果。

## What Changes

### 1. 新增任务 (Task) 概念
- 任务是一次测试运行的顶层容器
- 任务包含多个评测集的执行
- 任务级别展示总体执行进度和状态

### 2. 新增评测集 (Benchmark Suite) 概念
- 评测集是一组相关测试脚本的集合
- 每个评测集独立记录执行状态和结果
- 一个任务可以包含多个评测集

### 3. 数据库模型变更
- 新增 `tasks` 表：存储任务元数据
- 新增 `benchmark_suites` 表：存储评测集定义和任务关联
- 修改 `test_executions` 表：添加 `suite_id` 和 `task_id` 外键

### 4. API 变更
- 新增 Task 相关 API（创建、查询、列表）
- 新增 Benchmark Suite 相关 API（创建、查询、关联脚本）
- 修改执行 API 支持按任务/评测集执行

### 5. 前端页面变更
- 新增任务管理页面
- 任务详情页展示评测集列表和执行状态
- 评测集详情展示包含的脚本执行记录

## Capabilities

### New Capabilities

- `task-management`: 任务生命周期管理，包括创建任务、查看任务列表、查看任务详情、任务状态跟踪
- `benchmark-suite-management`: 评测集管理，包括创建评测集、关联测试脚本、查看评测集执行状态
- `hierarchical-execution`: 支持按任务/评测集层级的批量执行能力

### Modified Capabilities

- `test-script-execution`: 修改执行模型，支持按评测集批量执行，execution 记录关联到 suite 和 task
- `test-result-collection`: 修改结果收集，支持按任务/评测集聚合结果

## Impact

### 数据库
- 需要新增 `tasks` 表
- 需要新增 `benchmark_suites` 表
- 需要修改 `test_executions` 表添加外键

### 后端 (Go)
- 新增 handlers: task, benchmark_suite
- 新增 models: Task, BenchmarkSuite
- 新增 repositories: task, benchmark_suite
- 修改 executor service 支持层级执行

### 前端 (React)
- 新增任务管理页面
- 修改执行管理页面支持层级展示
- 新增评测集管理 UI
