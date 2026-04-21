# Test Platform Backend (Golang)

云手机测试平台后端服务。

## 技术栈

- **语言**: Go 1.21+
- **Web 框架**: Gin
- **数据库**: MySQL 8.0
- **认证**: JWT
- **配置**: Viper

## 快速开始

### 1. 安装依赖

```bash
go mod download
```

### 2. 配置环境

编辑 `.env` 文件：

```env
SERVER_PORT=8011
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1234
DB_NAME=testplatform
JWT_SECRET=your-secret-key
JWT_EXPIRATION=24h
```

### 3. 启动服务

```bash
go build -o server.exe cmd/server/main.go
./server.exe
```

## API 接口

### 认证
- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/auth/logout` - 登出

### 脚本管理
- `POST /api/v1/scripts/upload` - 上传脚本
- `GET /api/v1/scripts` - 获取脚本列表
- `GET /api/v1/scripts/:id` - 获取脚本详情
- `PUT /api/v1/scripts/:id` - 更新脚本
- `DELETE /api/v1/scripts/:id` - 删除脚本

### 执行管理
- `POST /api/v1/executions` - 创建执行任务
- `GET /api/v1/executions` - 获取执行列表
- `GET /api/v1/executions/:id` - 获取执行详情
- `GET /api/v1/executions/:id/logs` - 获取执行日志
- `DELETE /api/v1/executions/:id` - 删除执行

### 配置管理
- `GET /api/v1/configs` - 获取配置列表
- `GET /api/v1/configs/:key` - 获取单个配置
- `POST /api/v1/configs` - 设置配置
- `DELETE /api/v1/configs/:key` - 删除配置

### 健康检查
- `GET /health`
- `GET /api/health`

## 项目结构

```
backend-go/
├── cmd/server/           # 入口
├── internal/
│   ├── auth/             # 认证 (JWT)
│   ├── config/           # 配置管理
│   ├── database/         # 数据库连接
│   ├── executor/         # 脚本执行器
│   ├── handlers/         # HTTP 处理器
│   ├── middleware/        # 中间件
│   ├── models/           # 数据模型
│   ├── repository/       # 数据访问层
│   └── server/           # HTTP 服务器
├── migrations/           # 数据库迁移
├── .env                  # 环境配置
├── docker-compose.yml    # Docker Compose
└── Dockerfile
```

## 数据库迁移

迁移在服务启动时自动执行。迁移文件位于 `migrations/` 目录。

## 默认账号

- 用户名: admin
- 密码: admin123
