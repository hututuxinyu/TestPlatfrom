# 测试平台API接口设计

## 🚀 基础信息

**Base URL**: `http://test-platform:8080/api/v1`

**认证方式**: JWT Token (Header: `Authorization: Bearer <token>`)

**响应格式**:
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

## 📝 API接口列表

### 1. 用户认证

#### 1.1 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password"
}

Response 200:
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiresIn": 7200,
    "user": {
      "id": "user_001",
      "username": "admin",
      "nickname": "管理员"
    }
  }
}
```

#### 1.2 用户登出
```http
POST /auth/logout
Authorization: Bearer <token>

Response 200:
{
  "code": 200,
  "message": "登出成功"
}
```

### 2. 测试脚本管理

#### 2.1 上传测试脚本
```http
POST /scripts/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

script_file: TC_SBG_Func_GIDS_001_004.py
script_name: GIDS宫格登录参数异常测试
script_type: api

Response 201:
{
  "code": 201,
  "message": "脚本上传成功",
  "data": {
    "id": "script_001",
    "name": "GIDS宫格登录参数异常测试",
    "script_file": "/data/scripts/TC_SBG_Func_GIDS_001_004.py",
    "script_type": "api",
    "created_at": "2025-04-15T10:00:00Z"
  }
}
```

#### 2.2 查询测试脚本列表
```http
GET /scripts
Authorization: Bearer <token>
?page=1&size=20&status=active&script_type=api

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 10,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": "script_001",
        "name": "GIDS宫格登录参数异常测试",
        "script_file": "/data/scripts/TC_SBG_Func_GIDS_001_004.py",
        "script_type": "api",
        "status": "active",
        "created_at": "2025-04-15T10:00:00Z"
      }
    ]
  }
}
```

#### 2.3 获取脚本详情
```http
GET /scripts/:id
Authorization: Bearer <token>

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": "script_001",
    "name": "GIDS宫格登录参数异常测试",
    "script_file": "/data/scripts/TC_SBG_Func_GIDS_001_004.py",
    "script_type": "api",
    "status": "active",
    "created_at": "2025-04-15T10:00:00Z"
  }
}
```

### 3. 测试执行管理

#### 3.1 执行测试脚本
```http
POST /executions
Authorization: Bearer <token>
Content-Type: application/json

{
  "script_id": "script_001",
  "executor": "admin"
}

Response 202:
{
  "code": 202,
  "message": "测试执行已开始",
  "data": {
    "id": "execution_001",
    "script_id": "script_001",
    "status": "running",
    "started_at": "2025-04-15T10:30:00Z"
  }
}
```

#### 3.2 批量执行测试脚本
```http
POST /executions/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "script_ids": ["script_001", "script_002", "script_003"],
  "executor": "admin"
}

Response 202:
{
  "code": 202,
  "message": "批量执行已开始",
  "data": {
    "execution_ids": ["execution_001", "execution_002", "execution_003"],
    "status": "running",
    "started_at": "2025-04-15T10:30:00Z"
  }
}
```

#### 3.3 查询执行记录
```http
GET /executions
Authorization: Bearer <token>
?page=1&size=20&status=passed&script_id=script_001

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 15,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": "execution_001",
        "script_id": "script_001",
        "script_name": "GIDS宫格登录参数异常测试",
        "status": "passed",
        "exit_code": 0,
        "duration": 2,
        "started_at": "2025-04-15T10:30:00Z",
        "finished_at": "2025-04-15T10:30:02Z",
        "executor": "admin",
        "error_message": null
      }
    ]
  }
}
```

#### 3.4 获取执行详情(含日志)
```http
GET /executions/:id
Authorization: Bearer <token>

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "id": "execution_001",
    "script_id": "script_001",
    "script_name": "GIDS宫格登录参数异常测试",
    "status": "passed",
    "exit_code": 0,
    "logs": "[INFO] 开始测试...\n[INFO] 步骤1...\n[SUCCESS] 测试通过",
    "logs_file": "/data/logs/execution_001.log",
    "started_at": "2025-04-15T10:30:00Z",
    "finished_at": "2025-04-15T10:30:02Z",
    "duration": 2,
    "executor": "admin",
    "error_message": null,
    "created_at": "2025-04-15T10:30:00Z"
  }
}
```

### 4. 测试集管理

#### 4.1 创建测试集
```http
POST /suites
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "GIDS API参数验证测试集",
  "description": "包含GIDS API参数相关的验证测试",
  "script_ids": ["script_001", "script_002", "script_003"]
}

Response 201:
{
  "code": 201,
  "message": "测试集创建成功",
  "data": {
    "id": "suite_001",
    "name": "GIDS API参数验证测试集",
    "description": "...",
    "script_ids": ["script_001", "script_002", "script_003"],
    "created_at": "2025-04-15T10:00:00Z"
  }
}
```

#### 4.2 执行测试集
```http
POST /suites/:id/executions
Authorization: Bearer <token>
Content-Type: application/json

{
  "executor": "admin"
}

Response 202:
{
  "code": 202,
  "message": "测试集执行已开始",
  "data": {
    "id": "suite_execution_001",
    "suite_id": "suite_001",
    "status": "running",
    "total_count": 3,
    "started_at": "2025-04-15T10:30:00Z"
  }
}
```

### 5. 结果归档管理

#### 5.1 查询归档列表
```http
GET /archives
Authorization: Bearer <token>
?page=1&size=20&date_from=2025-04-01&date_to=2025-04-30

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "total": 5,
    "page": 1,
    "size": 20,
    "items": [
      {
        "id": "archive_001",
        "suite_execution_id": "suite_exec_001",
        "archive_name": "suite_001_archive_20250415.zip",
        "archive_file": "/data/archives/suite_001_archive_20250415.zip",
        "file_size": 12582912,
        "file_count": 15,
        "created_at": "2025-04-15T11:00:00Z"
      }
    ]
  }
}
```

#### 5.2 下载归档文件
```http
GET /archives/:id/download
Authorization: Bearer <token>

Response 200:
Content-Type: application/zip
Content-Disposition: attachment; filename="suite_001_archive_20250415.zip"

<ZIP文件内容>
```

#### 5.3 获取归档文件清单
```http
GET /archives/:id/manifest
Authorization: Bearer <token>

Response 200:
{
  "code": 200,
  "message": "查询成功",
  "data": {
    "archive_name": "suite_001_archive_20250415.zip",
    "files": [
      {
        "path": "logs/execution_001.log",
        "size": 12345,
        "type": "text"
      },
      {
        "path": "scripts/TC_SBG_Func_GIDS_001_004.py",
        "size": 5678,
        "type": "text"
      }
    ]
  }
}
```

## 🔄 WebSocket接口

### 实时执行进度推送

**连接地址**: `ws://test-platform:8080/ws/executions/:id`

**推送消息格式**:
```json
{
  "type": "progress",
  "execution_id": "execution_001",
  "status": "running",
  "current_step": 2,
  "total_steps": 3,
  "log_line": "[INFO] 步骤2: 仅必选参数请求",
  "timestamp": 1713140400
}
```

**推送类型**:
- `started`: 执行开始
- `progress`: 执行进度
- `log_line`: 日志行
- `completed`: 执行完成

## 📊 错误码定义

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 502 | 脚本执行超时 |
| 503 | 脚本执行失败 |

## 🔒 权限说明

**当前版本**: 只需要用户登录认证,不实现复杂的角色权限

- 登录用户可以: 上传/删除脚本、执行测试、查看结果、下载归档
- 未登录用户: 只能查看公开的测试报告(可选功能)