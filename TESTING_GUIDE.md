# 测试平台功能验证指南

## 技术栈

### 后端
- Go 1.21+
- Gin Web Framework
- MySQL 8.0
- JWT 认证

### 前端
- React 19
- TypeScript
- Vite
- Ant Design

## 快速开始

### 1. 启动后端

```bash
cd backend-go
go build -o server.exe cmd/server/main.go
./server.exe
```

后端端口: 8011

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端端口: 5173

### 3. 访问系统

- 前端地址: http://localhost:5173
- 后端地址: http://localhost:8011

### 4. 默认账号

- 用户名: admin
- 密码: admin123

## API 测试

### 登录

```bash
curl -X POST http://localhost:8011/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 上传脚本

```bash
TOKEN="your_access_token"
curl -X POST http://localhost:8011/api/v1/scripts/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.py" \
  -F "name=测试脚本" \
  -F "description=测试描述" \
  -F "language=python"
```

### 获取脚本列表

```bash
curl -X GET "http://localhost:8011/api/v1/scripts" \
  -H "Authorization: Bearer $TOKEN"
```

### 创建执行任务

```bash
curl -X POST http://localhost:8011/api/v1/executions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"script_id": 1}'
```

### 获取执行日志

```bash
curl -X GET http://localhost:8011/api/v1/executions/1/logs \
  -H "Authorization: Bearer $TOKEN"
```

## 数据库结构

### users 表
- id, username, password, email, is_active, created_at, updated_at

### test_scripts 表
- id, name, description, language, file_path, file_size, file_hash
- tags, created_by, created_at, updated_at

### test_executions 表
- id, script_id, script_name, status, exit_code
- started_at, completed_at, duration_seconds
- created_by, created_at

### execution_logs 表
- id, execution_id, log_type, content, created_at

### global_configs 表
- id, key, value, description, created_at, updated_at
