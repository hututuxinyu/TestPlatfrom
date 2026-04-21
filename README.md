# 云手机测试平台

一个完整的端到端测试评测平台，支持测试脚本管理、执行和结果收集。

## 技术栈

- **前端**: React + TypeScript + Vite + Ant Design
- **后端**: Go + Gin + MySQL
- **测试目标**: GIDS 服务集成测试

## 快速开始

### 1. 启动后端

```bash
cd backend-go
go build -o server.exe cmd/server/main.go
./server.exe
```

### 2. 启动前端

```bash
cd frontend
npm run dev
```

### 3. 访问系统

- **前端地址**: http://localhost:5173
- **后端地址**: http://localhost:8011
- **默认账号**: admin / admin123

## 项目结构

```
TestPlatfrom/
├── backend-go/           # Go 后端服务
│   ├── cmd/server/       # 入口
│   ├── internal/        # 内部包
│   │   ├── auth/        # 认证
│   │   ├── config/      # 配置
│   │   ├── database/    # 数据库
│   │   ├── executor/    # 执行器
│   │   ├── handlers/    # HTTP 处理器
│   │   ├── middleware/ # 中间件
│   │   ├── models/     # 数据模型
│   │   └── repository/ # 数据访问
│   ├── migrations/     # 数据库迁移
│   └── .env            # 环境配置
├── frontend/            # React 前端
│   ├── src/            # 源代码
│   └── vite.config.ts # Vite 配置
└── openspec/           # 设计文档
```

## 功能特性

- 用户认证 (JWT)
- 测试脚本管理 (CRUD)
- 测试执行管理
- 执行日志收集
- 全局配置管理

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

## 配置说明

后端配置在 `backend-go/.env` 中：

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

## 端口说明

- 前端: 5173
- 后端: 8011

如端口被占用，服务启动会失败（strictPort: true）
