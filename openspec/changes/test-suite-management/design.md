## Context

当前测试脚本以扁平列表管理（`test_scripts` 表），所有脚本混在一起，通过 `tags` 字段做简单分类。用户需要按业务维度（HTTP接口测试、功能测试、性能测试等）组织脚本，并支持 ZIP 批量上传、套内统一执行。

### 现有数据模型

```
test_scripts (现有)
├── id (自增主键)
├── name, description, language
├── file_path, file_size, file_hash
├── tags, created_by, created_at, updated_at
```

### 现有 API 模式

- Handler 放在 `internal/handlers/`
- Repository 放在 `internal/repository/`
- 统一使用 `SuccessResponse(c, data)` 返回
- 文件存储在配置目录 `Executor.UploadDir`

## Goals / Non-Goals

**Goals:**
- 实现测试套（TestSuite）概念，支持按业务维度分类管理脚本
- 支持 ZIP 批量上传测试套
- 实现任务（Task）粒度的执行管理，支持批量执行和停止
- 导出套内脚本为 ZIP

**Non-Goals:**
- 不迁移现有数据（用户会删库重建）
- 不实现脚本跨套共享（N:M 关系）
- 不实现预定义的套类型模板
- 不实现套的执行状态跟踪（只有上传状态）

## Decisions

### 1. 数据模型

**新增 `test_suites` 表**

```sql
CREATE TABLE test_suites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**修改 `test_scripts` 表**

```sql
ALTER TABLE test_scripts ADD COLUMN suite_id INT;
ALTER TABLE test_scripts ADD COLUMN uuid VARCHAR(36) NOT NULL;
-- uuid 使用程序生成（github.com/google/uuid）
```

```sql
CREATE TABLE test_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    suite_id INT NOT NULL,
    suite_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    total_count INT NOT NULL DEFAULT 0,
    success_count INT NOT NULL DEFAULT 0,
    failed_count INT NOT NULL DEFAULT 0,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL
);
```

**修改 `test_executions` 表**

```sql
ALTER TABLE test_executions ADD COLUMN task_id INT;
ALTER TABLE test_executions ADD COLUMN script_uuid VARCHAR(36) NOT NULL;
```

**关系图**

```
test_suites (1) ←→ (N) test_scripts
test_tasks (1) ←→ (N) test_executions
test_suites (1) ←→ (N) test_tasks
```

### 2. 文件存储结构

```
{upload_dir}/
├── suites/
│   └── {suite_id}/
│       ├── login.py
│       └── getUser.py
└── ...
```

每个套有独立子目录，套内脚本存储在该目录下。

### 3. UUID 生成策略

使用 `github.com/google/uuid` 生成全局唯一索引，替代自增 ID 作为脚本的对外标识。

### 4. ZIP 上传处理流程

```
1. 接收 ZIP 文件 + 套名称
2. 检查套名称是否已存在（唯一性校验）
3. 创建套记录
4. 解压 ZIP，遍历文件
5. 对每个脚本文件：
   - 计算 SHA256 生成 UUID
   - 保存到 {upload_dir}/suites/{suite_id}/
   - 创建 script 记录 (uuid, name, suite_id, ...)
6. 全部成功 → 返回成功
   任何失败 → 回滚（删除已创建的文件和记录）
```

### 5. 套内脚本上传

单个文件上传到指定套，不支持 ZIP。

### 6. 一键执行流程

```
1. 用户点击"一键执行"
2. 创建 task 记录 (status=pending)
3. 查询套内所有脚本
4. 为每个脚本创建 execution 记录 (task_id=新建task)
5. 异步执行每个脚本
6. 脚本执行完成时更新 execution 和 task 的计数
```

### 7. 任务停止流程

```
1. 用户点击"停止任务"
2. 更新 task status = 'stopped'
3. 通知执行器停止该任务下的所有运行中脚本
4. 执行器检查 task_id，已 stop 的跳过执行
```

### 8. 导出 ZIP 结构

```
{suite_name}.zip
├── login.py
├── getUser.py
└── order.py
```

遍历套内脚本，按原文件名打包。

### 9. API 设计

**Suite APIs**

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/suites | 列表（返回汇总信息） |
| POST | /api/v1/suites | 创建（ZIP 上传） |
| GET | /api/v1/suites/:id | 详情 |
| PUT | /api/v1/suites/:id | 更新（重命名） |
| DELETE | /api/v1/suites/:id | 删除（先删脚本再删套） |
| GET | /api/v1/suites/:id/scripts | 套内脚本列表 |
| POST | /api/v1/suites/:id/scripts | 上传脚本到套 |
| GET | /api/v1/suites/:id/export | 导出套为 ZIP |

**Task APIs**

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/tasks | 任务列表（支持下拉框筛选） |
| GET | /api/v1/tasks/:id | 任务详情 |
| POST | /api/v1/tasks/:id/stop | 停止任务 |
| GET | /api/v1/tasks/:id/executions | 任务下的执行记录 |

**Execution APIs（扩展）**

| Change | Description |
|--------|-------------|
| GET /api/v1/executions | 增加 task_id 筛选参数 |
| 新增响应字段 task_id, script_uuid |

### 10. 前端路由设计

```
/scripts              → 测试套网格视图（默认）
/scripts/:suiteId     → 套内脚本表格视图
/executions           → 执行管理（任务下拉框）
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| ZIP 上传大文件导致超时 | 设置合理超时，使用后台处理 |
| 套内脚本执行时间长 | 任务粒度跟踪，支持中途停止 |
| UUID 替换 ID 后的兼容问题 | 全新数据结构，不存在兼容 |

## Migration Plan

1. 创建新数据库表
2. 部署新的后端 API
3. 部署新的前端
4. 用户上传 ZIP 创建测试套

用户已确认会删库重建，无历史数据迁移需求。

## Open Questions

1. ~~是否需要支持套的描述字段？~~（用户未要求，暂不实现）
2. ~~套内脚本是否允许重命名？~~（暂不实现，只允许删除）
3. 任务停止机制需要执行器支持，目前执行器是同步启动 goroutine，需要确认停止信号如何传递
