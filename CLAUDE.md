# TestPlatform - Claude 工作指南

## 项目概述

这是一个云手机测试平台，用于管理和执行自动化测试脚本。

- **前端**: React + TypeScript + Vite + Ant Design
- **后端**: Go + Gin + MySQL
- **测试目标**: GIDS 服务集成测试

## 核心目标

### 测试执行与验证

1. **执行测试用例**
   - 点击执行按钮后，测试脚本应正常运行
   - 能够与 GIDS 服务（默认 127.0.0.1:9090）正常通信
   - 测试结果应清晰显示成功或失败状态

2. **失败分析与修复**
   - 如果测试失败，必须读取日志记录分析问题
   - 定位根本原因（代码问题、配置问题、环境问题等）
   - 修复问题并重新验证，直到测试通过

3. **日志与问题定位**
   - 后端必须具备完善的日志能力
   - 用例执行的结果和相关信息应保留在日志文件中
   - 日志应包含足够的上下文信息，便于快速定位问题

## 项目结构

```
TestPlatfrom/
├── backend-go/           # Go 后端服务
│   ├── cmd/server/       # 入口
│   ├── internal/         # 内部包
│   │   ├── auth/        # 认证 (JWT)
│   │   ├── config/      # 配置管理
│   │   ├── database/    # 数据库连接
│   │   ├── executor/    # 脚本执行器
│   │   ├── handlers/    # HTTP 处理器
│   │   ├── middleware/  # 中间件
│   │   ├── models/      # 数据模型
│   │   └── repository/  # 数据访问层
│   ├── migrations/      # 数据库迁移
│   ├── data/            # 数据目录
│   ├── logs/            # 日志目录
│   └── .env             # 环境配置
├── frontend/             # React 前端
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   └── services/    # API 服务
│   └── vite.config.ts  # Vite 配置
└── openspec/            # 设计文档
```

## 环境配置

### 后端启动

```bash
cd backend-go
go build -o server.exe cmd/server/main.go
./server.exe
```

端口: 8011 (固定，不可占用)

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

端口: 5173 (固定，不可占用)

### GIDS 服务

- 默认地址: http://127.0.0.1:9090
- 配置位置: 数据库 `global_configs` 表中的 `GIDS_ADDR`

### 数据库配置

在 `backend-go/.env` 中配置：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=1234
DB_NAME=testplatform
```

## 认证说明

- 使用 JWT 进行用户认证
- 密码在数据库中明文存储
- 默认用户: admin / admin123

## 工作流程

1. **上传脚本** → 脚本管理页面上传测试脚本
2. **配置环境** → 配置页面设置 GIDS_ADDR 等参数
3. **执行测试** → 点击执行按钮运行测试
4. **查看结果** → 执行管理页面查看日志和状态
5. **问题分析** → 如果失败，分析日志并修复
6. **重新验证** → 修复后重新执行，确保通过

## 注意事项

- 前端 vite.config.ts 设置了 strictPort: true，端口占用会启动失败
- 后端 ListenAndServe 在端口占用时会报错退出
- 数据库使用 MySQL，不是 SQLite
- JWT 配置在 .env 中，secret 和 expiration 可配置
