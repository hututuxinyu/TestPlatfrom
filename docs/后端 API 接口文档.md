# TestPlatform API 文档

## 基础信息

- **基础地址**: `http://localhost:8011`
- **全局中间件**: CORS、Logger、Recovery、ErrorHandler

---

## 通用响应格式

### 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 错误响应

```json
{
  "code": <http_status>,
  "message": "<error description>"
}
```

---

## 认证方式

大多数接口需要 JWT 认证，在请求头中携带：

```
Authorization: Bearer <access_token>
```

Token 通过 `POST /api/v1/auth/login` 获取，默认过期时间 24 小时。

---

## 接口总览

| # | 方法 | 路径 | 说明 | 认证 |
|---|------|------|------|------|
| 1 | GET | `/health` | 健康检查 | 否 |
| 2 | GET | `/api/health` | 健康检查 | 否 |
| 3 | POST | `/api/v1/auth/login` | 用户登录 | 否 |
| 4 | POST | `/api/v1/auth/logout` | 用户登出 | 否 |
| 5 | POST | `/api/v1/scripts` | 上传脚本 | JWT |
| 6 | POST | `/api/v1/scripts/upload` | 上传脚本 | JWT |
| 7 | GET | `/api/v1/scripts` | 脚本列表 | JWT |
| 8 | GET | `/api/v1/scripts/:id` | 获取脚本详情 | JWT |
| 9 | GET | `/api/v1/scripts/:id/content` | 获取脚本内容 | JWT |
| 10 | PUT | `/api/v1/scripts/:id` | 更新脚本 | JWT |
| 11 | DELETE | `/api/v1/scripts/:id` | 删除脚本 | JWT |
| 12 | POST | `/api/v1/scripts/batch-delete` | 批量删除脚本 | JWT |
| 13 | POST | `/api/v1/executions` | 执行单个脚本 | JWT |
| 14 | POST | `/api/v1/executions/batch` | 批量执行脚本 | JWT |
| 15 | POST | `/api/v1/executions/batch-all` | 执行所有脚本 | JWT |
| 16 | GET | `/api/v1/executions` | 执行记录列表 | JWT |
| 17 | GET | `/api/v1/executions/batch-all` | 执行所有脚本 | JWT |
| 18 | GET | `/api/v1/executions/:id` | 获取执行详情 | JWT |
| 19 | GET | `/api/v1/executions/:id/logs` | 获取执行日志 | JWT |
| 20 | DELETE | `/api/v1/executions/:id` | 删除执行记录 | JWT |
| 21 | GET | `/api/v1/configs` | 配置列表 | JWT |
| 22 | GET | `/api/v1/configs/:key` | 获取单个配置 | JWT |
| 23 | POST | `/api/v1/configs` | 设置配置 | JWT |
| 24 | DELETE | `/api/v1/configs/:key` | 删除配置 | JWT |
| 25 | GET | `/api/v1/suites` | 套件列表 | JWT |
| 26 | POST | `/api/v1/suites` | 创建套件 | JWT |
| 27 | GET | `/api/v1/suites/:id` | 获取套件详情 | JWT |
| 28 | PUT | `/api/v1/suites/:id` | 更新套件 | JWT |
| 29 | DELETE | `/api/v1/suites/:id` | 删除套件 | JWT |
| 30 | GET | `/api/v1/suites/:id/scripts` | 套件内脚本列表 | JWT |
| 31 | POST | `/api/v1/suites/:id/scripts` | 向套件上传脚本 | JWT |
| 32 | GET | `/api/v1/suites/:id/export` | 导出套件为 ZIP | JWT |
| 33 | POST | `/api/v1/suites/:id/execute` | 执行套件中所有脚本 | JWT |
| 34 | GET | `/api/v1/tasks` | 任务列表 | JWT |
| 35 | GET | `/api/v1/tasks/:id` | 获取任务详情 | JWT |
| 36 | POST | `/api/v1/tasks/:id/stop` | 停止任务 | JWT |
| 37 | DELETE | `/api/v1/tasks/:id` | 删除任务 | JWT |
| 38 | GET | `/api/v1/tasks/:id/executions` | 任务下的执行记录 | JWT |

---

## 1. 健康检查

### GET /health
### GET /api/health

无需认证。

**响应示例：**

```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## 2. 认证

### POST /api/v1/auth/login

无需认证。使用用户名密码登录，获取 JWT Token。

**请求体：**

```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "username": "admin"
  }
}
```

**错误码：**
- `400` - 请求参数无效
- `401` - 凭据无效或账户已禁用

---

### POST /api/v1/auth/logout

无需认证。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Logged out successfully"
  }
}
```

---

## 3. 脚本管理

> 以下接口均需 JWT 认证。

### POST /api/v1/scripts
### POST /api/v1/scripts/upload

上传脚本文件，支持单个文件或 ZIP 压缩包。

**请求格式：** `multipart/form-data`

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | File | 是 | 脚本文件（.py/.sh/.js）或 ZIP |
| `description` | String | 否 | 脚本描述 |
| `language` | String | 否 | 语言（python/shell/javascript），不传则自动检测 |
| `tags` | String | 否 | 标签，逗号分隔 |

**单文件响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "uuid": "xxx",
    "name": "test.py",
    "description": "",
    "language": "python",
    "file_path": "scripts/xxx/test.py",
    "file_size": 1024,
    "file_hash": "sha256hex",
    "suite_id": null,
    "tags": "",
    "created_by": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

**ZIP 文件响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Uploaded 3 scripts from archive",
    "scripts": [ ... ],
    "total": 3
  }
}
```

**错误码：** `400` - 不支持的文件类型 / 无效请求，`500` - 内部错误

---

### GET /api/v1/scripts

获取脚本列表，支持分页和语言过滤。

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `language` | String | "" | 按语言过滤（python/shell/javascript） |
| `page` | Int | 1 | 页码 |
| `page_size` | Int | 20 | 每页条数（最大 100） |

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

---

### GET /api/v1/scripts/:id

获取单个脚本的详细信息。

**路径参数：** `id` - 脚本 ID

**响应：** `data` 返回单个 `TestScript` 对象

---

### GET /api/v1/scripts/:id/content

获取脚本文件内容。

**路径参数：** `id` - 脚本 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "content": "print('hello world')"
  }
}
```

---

### PUT /api/v1/scripts/:id

更新脚本信息。

**路径参数：** `id` - 脚本 ID

**请求体：**

```json
{
  "description": "新的描述",
  "tags": "tag1,tag2"
}
```

**响应：** `data` 返回更新后的 `TestScript` 对象

---

### DELETE /api/v1/scripts/:id

删除单个脚本（同时删除磁盘上的文件）。

**路径参数：** `id` - 脚本 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Script deleted successfully"
  }
}
```

---

### POST /api/v1/scripts/batch-delete

批量删除脚本。

**请求体：**

```json
{
  "script_ids": [1, 2, 3]
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Deleted 3 scripts successfully",
    "deleted_count": 3
  }
}
```

---

## 4. 执行管理

> 以下接口均需 JWT 认证。

### POST /api/v1/executions

开始执行单个脚本。会创建一个 `single_script` 类型的任务和一个执行记录，后台异步运行。

**请求体：**

```json
{
  "script_id": 1
}
```

**响应：** `data` 返回 `TestExecution` 对象，初始状态为 `"pending"`

---

### POST /api/v1/executions/batch

批量执行多个脚本。

**请求体：**

```json
{
  "script_ids": [1, 2, 3]
}
```

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 3,
    "succeeded": 2,
    "failed": 1,
    "executions": [ ... ],
    "failed_items": [
      { "script_id": 2, "error": "Script not found" }
    ]
  }
}
```

---

### POST /api/v1/executions/batch-all
### GET /api/v1/executions/batch-all

执行所有现有脚本。

**响应：** 与 `batch` 接口相同

---

### GET /api/v1/executions

获取执行记录列表。

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `script_id` | Int | 0 | 按脚本 ID 过滤 |
| `task_id` | Int | 0 | 按任务 ID 过滤 |
| `status` | String | "" | 按状态过滤（pending/running/completed/failed/stopped） |
| `page` | Int | 1 | 页码 |
| `page_size` | Int | 20 | 每页条数（最大 100） |

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 50,
    "page": 1,
    "page_size": 20
  }
}
```

---

### GET /api/v1/executions/:id

获取单条执行记录的详情。

**路径参数：** `id` - 执行记录 ID

**响应：** `data` 返回单个 `TestExecution` 对象

---

### GET /api/v1/executions/:id/logs

获取执行日志，按时间顺序排列的完整文本。

**路径参数：** `id` - 执行记录 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "logs": "[system] 开始执行脚本: test.py\n[stdout] hello world\n[stderr] warning: ...\n[system] 脚本执行完成，退出码: 0，状态: completed\n"
  }
}
```

日志前缀说明：`[system]` 系统日志 | `[stdout]` 标准输出 | `[stderr]` 错误输出

---

### DELETE /api/v1/executions/:id

删除执行记录。

**路径参数：** `id` - 执行记录 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Execution deleted successfully"
  }
}
```

---

## 5. 配置管理

> 以下接口均需 JWT 认证。
>
> 配置项用于在执行脚本时注入环境变量，如 `GIDS_ADDR`。

### GET /api/v1/configs

获取所有配置，按 key 升序排列。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "key": "GIDS_ADDR",
        "value": "http://127.0.0.1:9090",
        "description": "GIDS service address",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

---

### GET /api/v1/configs/:key

获取单个配置。

**路径参数：** `key` - 配置键名

**响应：** `data` 返回单个 `GlobalConfig` 对象

---

### POST /api/v1/configs

创建或更新配置（使用 `ON DUPLICATE KEY UPDATE`）。

**请求体：**

```json
{
  "key": "GIDS_ADDR",
  "value": "http://127.0.0.1:9090",
  "description": "GIDS service address"
}
```

**响应：** `data` 返回更新后的 `GlobalConfig` 对象

---

### DELETE /api/v1/configs/:key

删除配置。

**路径参数：** `key` - 配置键名

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Config deleted successfully"
  }
}
```

---

## 6. 测试套件

> 以下接口均需 JWT 认证。

### GET /api/v1/suites

获取所有套件列表，包含聚合信息。

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "name": "My Suite",
        "script_count": 10,
        "total_lines": 500,
        "latest_upload": "2024-01-01 12:00:00"
      }
    ],
    "total": 5
  }
}
```

---

### POST /api/v1/suites

创建套件。

**请求格式：** `multipart/form-data`

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | String | 是 | 套件名称（唯一） |
| `file` | File | 否 | 可选，上传 ZIP 解压到套件 |

**仅创建套件响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "name": "My Suite",
    "created_by": 1,
    "created_at": "...",
    "updated_at": "..."
  }
}
```

**带 ZIP 上传响应：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "suite": { ... },
    "scripts": [ ... ],
    "total": 5
  }
}
```

---

### GET /api/v1/suites/:id

获取套件详情。

**路径参数：** `id` - 套件 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "suite": {
      "id": 1,
      "name": "My Suite",
      "created_by": 1,
      "created_at": "...",
      "updated_at": "..."
    },
    "summary": {
      "id": 1,
      "name": "My Suite",
      "script_count": 10,
      "total_lines": 500,
      "latest_upload": "2024-01-01 12:00:00"
    }
  }
}
```

---

### PUT /api/v1/suites/:id

重命名套件。

**路径参数：** `id` - 套件 ID

**请求体：**

```json
{
  "name": "New Suite Name"
}
```

**响应：** `data` 返回更新后的 `TestSuite` 对象

---

### DELETE /api/v1/suites/:id

删除套件及其所有脚本（数据库和磁盘文件一并删除）。

**路径参数：** `id` - 套件 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Suite deleted successfully"
  }
}
```

---

### GET /api/v1/suites/:id/scripts

获取指定套件下的所有脚本。

**路径参数：** `id` - 套件 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 10
  }
}
```

---

### POST /api/v1/suites/:id/scripts

向套件上传单个脚本。

**路径参数：** `id` - 套件 ID

**请求格式：** `multipart/form-data`

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `file` | File | 是 | 脚本文件（.py/.sh/.js） |

**响应：** `data` 返回创建的 `TestScript` 对象

---

### GET /api/v1/suites/:id/export

将套件内所有脚本导出为 ZIP 文件。

**路径参数：** `id` - 套件 ID

**响应：** 流式 ZIP 文件下载

```
Content-Type: application/zip
Content-Disposition: attachment; filename="<suite-name>.zip"
```

---

### POST /api/v1/suites/:id/execute

执行套件中所有脚本。创建一个 `"suite_batch"` 类型的任务，后台异步执行。

**路径参数：** `id` - 套件 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Suite execution started with 10 scripts",
    "suite_id": 1,
    "suite_name": "My Suite",
    "script_count": 10,
    "task_id": 5
  }
}
```

---

## 7. 任务管理

> 以下接口均需 JWT 认证。
>
> 任务代表一批脚本执行。类型分为 `"single_script"`（单个执行）和 `"suite_batch"`（套件批量执行）。

### GET /api/v1/tasks

获取任务列表。

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `suite_id` | Int | 0 | 按套件 ID 过滤 |
| `page` | Int | 1 | 页码 |
| `page_size` | Int | 20 | 每页条数（最大 100） |

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "task_type": "single_script",
        "suite_id": null,
        "suite_name": "",
        "status": "completed",
        "total_count": 1,
        "success_count": 1,
        "failed_count": 0,
        "created_by": 1,
        "created_at": "...",
        "completed_at": "..."
      }
    ],
    "total": 20,
    "page": 1,
    "page_size": 20
  }
}
```

`status` 取值：`pending` | `running` | `completed` | `failed` | `stopped`

---

### GET /api/v1/tasks/:id

获取单个任务详情。

**路径参数：** `id` - 任务 ID

**响应：** `data` 返回单个 `TestTask` 对象

---

### POST /api/v1/tasks/:id/stop

停止正在运行的任务（仅对 `pending` 或 `running` 状态有效）。

> 注意：仅更新数据库状态为 `"stopped"`，不会杀死正在运行的脚本进程。

**路径参数：** `id` - 任务 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Task stopped successfully"
  }
}
```

---

### DELETE /api/v1/tasks/:id

删除任务。

**路径参数：** `id` - 任务 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "message": "Task deleted successfully"
  }
}
```

---

### GET /api/v1/tasks/:id/executions

获取任务下的所有执行记录。

**路径参数：** `id` - 任务 ID

**响应示例：**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [ ... ],
    "total": 5
  }
}
```

---

## 数据模型

### TestScript

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 主键 |
| `uuid` | String | 唯一标识 |
| `name` | String | 脚本文件名 |
| `description` | String | 描述 |
| `language` | String | 语言：python / shell / javascript |
| `file_path` | String | 文件存储路径 |
| `file_size` | Int64 | 文件大小（字节） |
| `file_hash` | String | SHA-256 哈希 |
| `suite_id` | Int / null | 所属套件 ID |
| `tags` | String | 标签（逗号分隔） |
| `created_by` | Int / null | 创建者 ID |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### TestTask

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 主键 |
| `task_type` | String | 类型：single_script / suite_batch |
| `suite_id` | Int / null | 关联套件 ID |
| `suite_name` | String | 套件名称 |
| `status` | String | pending / running / completed / failed / stopped |
| `total_count` | Int | 总脚本数 |
| `success_count` | Int | 成功数 |
| `failed_count` | Int | 失败数 |
| `created_by` | Int / null | 创建者 ID |
| `created_at` | DateTime | 创建时间 |
| `completed_at` | DateTime / null | 完成时间 |

### TestExecution

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 主键 |
| `task_id` | Int / null | 关联任务 ID |
| `script_id` | Int | 脚本 ID |
| `script_uuid` | String | 脚本 UUID |
| `script_name` | String | 脚本名称 |
| `status` | String | pending / running / completed / failed / stopped |
| `exit_code` | Int / null | 退出码 |
| `started_at` | DateTime / null | 开始时间 |
| `completed_at` | DateTime / null | 完成时间 |
| `duration_seconds` | Float / null | 执行耗时 |
| `log_content` | String | 完整执行日志（含 system/stdout/stderr） |
| `created_by` | Int / null | 创建者 ID |
| `created_at` | DateTime | 创建时间 |


### GlobalConfig

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 主键 |
| `key` | String | 配置键 |
| `value` | String | 配置值 |
| `description` | String | 描述 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### TestSuite

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 主键 |
| `name` | String | 套件名称（唯一） |
| `created_by` | Int / null | 创建者 ID |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### SuiteSummary

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Int | 套件 ID |
| `name` | String | 套件名称 |
| `script_count` | Int | 脚本数量 |
| `total_lines` | Int | 总行数 |
| `latest_upload` | String | 最近上传时间 |
