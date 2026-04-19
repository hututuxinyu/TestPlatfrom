## Context

### 背景

当前系统以单个测试脚本为执行单位，`test_executions` 表直接关联 `test_scripts`。这种方式在执行单个脚本时工作良好，但当需要组织和批量执行多个相关脚本时缺乏上层抽象。

### 当前数据模型

```
test_scripts
    └── test_executions (script_id FK)
            └── execution_logs

users ──── created_by
```

### 目标数据模型

```
tasks ──────────────── benchmark_suites (task_id FK)
  │                         │
  │                         └── test_scripts (suite_id FK via execution)
  │                                 │
  │                                 └── test_executions (suite_id FK, task_id FK)
  │                                         │
  │                                         └── execution_logs
  │
  └── users (created_by)
```

## Goals / Non-Goals

**Goals:**
- 实现任务-评测集-脚本的三层执行结构
- 支持一次操作执行整个评测集
- 任务详情页展示所有评测集的执行聚合状态
- 评测集详情页展示该评测集下所有脚本的执行记录

**Non-Goals:**
- 不改变单个脚本的执行逻辑
- 不修改现有的用户认证系统
- 不实现评测集的自动调度或定时执行（后续特性）

## Decisions

### Decision 1: 数据库模型设计

**选择**: 新增 `tasks` 和 `benchmark_suites` 两张表，不修改现有的 `test_scripts` 表

**理由**:
- `test_scripts` 是脚本的静态元信息，不应直接关联任务
- 执行记录 `test_executions` 通过外键关联到 suite 和 task
- 保持脚本的复用性：一个脚本可属于多个评测集

** Alternatives considered**:
- 在 `test_scripts` 表添加 `suite_id`：缺点是脚本只能属于一个评测集，限制了灵活性
- 只用 `test_executions` 表的 `batch_id`：缺少任务级别的元数据和状态

### Decision 2: 任务状态的计算

**选择**: 任务状态由子级评测集状态推算

**规则**:
- `pending`: 所有评测集都是 pending
- `running`: 任意评测集 running
- `completed`: 所有评测集 completed 且无 failed
- `failed`: 任意评测集 failed/stopped
- `partial`: 部分评测集 completed，部分 failed

**理由**: 简化状态管理，避免状态不一致

### Decision 3: API 层级

**选择**: Task API 和 Suite API 分开，Execution API 通过 query param 关联

**理由**: 清晰的职责分离，便于扩展

**Endpoints**:
```
GET    /api/v1/tasks                 # 任务列表
POST   /api/v1/tasks                 # 创建任务
GET    /api/v1/tasks/:id             # 任务详情
GET    /api/v1/tasks/:id/suites      # 任务的评测集列表

GET    /api/v1/suites                # 评测集列表
POST   /api/v1/suites                # 创建评测集
GET    /api/v1/suites/:id            # 评测集详情
POST   /api/v1/suites/:id/scripts    # 关联脚本到评测集

POST   /api/v1/executions            # 执行脚本(support suite_id)
GET    /api/v1/executions            # 执行记录列表(support task_id, suite_id filter)
```

## Risks / Trade-offs

[Risk] 现有执行 API 兼容性问题
→ [Mitigation] 新增 `suite_id` 参数为可选，旧调用方式继续工作

[Risk] 数据库迁移复杂性
→ [Mitigation] 使用 Go 的 migrate 库，支持 forward/backward migration

[Risk] 前端改动较大
→ [Mitigation] 分阶段实现：先完成数据模型和API，前端逐步迁移

## Migration Plan

1. **Phase 1**: 数据库迁移
   - 创建 `tasks` 表
   - 创建 `benchmark_suites` 表
   - `test_executions` 表添加 `task_id`, `suite_id` 列（nullable）

2. **Phase 2**: 后端实现
   - 实现 Task handlers
   - 实现 Suite handlers
   - 修改 Execution handler 支持层级

3. **Phase 3**: 前端实现
   - 新增任务管理页面
   - 修改执行管理页面支持层级展示

## Open Questions

1. 评测集是否需要版本概念？（当前不需要）
2. 任务是否需要优先级？（当前不需要）
3. 是否支持任务内评测集的执行顺序？（当前按创建顺序）
