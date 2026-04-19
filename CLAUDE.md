# TestPlatform - Claude 工作指南

## 项目概述

这是一个云手机测试平台，用于管理和执行自动化测试脚本。

- **前端**: React + TypeScript + Vite + Ant Design
- **后端**: Python + FastAPI + SQLite
- **测试目标**: GIDS 服务集成测试

## 核心目标

### 测试执行与验证
你的最终目标是确保测试用例能够成功执行并通过。具体要求：

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
   - 用例执行的结果和相关信息应保留在固定路径的日志文件中
   - 日志应包含足够的上下文信息，便于快速定位问题
   - 日志格式应清晰、结构化，包含时间戳、日志级别、详细错误堆栈等

## 项目结构

```
TestPlatfrom/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API 路由
│   │   ├── services/        # 业务逻辑
│   │   ├── models/          # 数据模型
│   │   └── main.py          # 应用入口
│   ├── data/
│   │   ├── local.db         # SQLite 数据库
│   │   └── uploads/         # 上传的脚本文件
│   └── logs/                # 日志文件目录（待实现）
├── frontend/
│   └── src/
│       ├── pages/           # 页面组件
│       └── services/        # API 服务
└── CLAUDE.md                # 本文件
```

## 环境配置

### 后端启动
```bash
cd backend
source .venv/Scripts/activate  # Windows Git Bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8011
```

### 前端启动
```bash
cd frontend
npm run dev
```

### GIDS 服务
- 默认地址: http://127.0.0.1:9090
- 配置位置: 数据库 `global_configs` 表中的 `GIDS_ADDR`

## 关键技术点

### Windows 异步子进程支持
- 后端在 Windows 上执行脚本需要设置 `WindowsProactorEventLoopPolicy`
- 已在 `app/main.py` 中配置，兼容 Windows 和 Linux

### 环境变量注入
- 全局配置（如 GIDS_ADDR）会自动注入到测试脚本的环境变量中
- 测试脚本可通过 `os.getenv('GIDS_ADDR')` 获取配置

### 日志系统（待完善）
- 当前日志存储在数据库 `execution_logs` 表中
- 需要增强：将日志同时写入文件系统，便于长期保存和分析
- 建议路径: `backend/logs/executions/{execution_id}.log`

## 工作流程

1. **上传脚本** → 脚本管理页面上传测试脚本
2. **配置环境** → 配置页面设置 GIDS_ADDR 等参数
3. **执行测试** → 点击执行按钮运行测试
4. **查看结果** → 执行管理页面查看日志和状态
5. **问题分析** → 如果失败，分析日志并修复
6. **重新验证** → 修复后重新执行，确保通过

## 注意事项

- 所有代码修改后，uvicorn 会自动重载（--reload 模式）
- 数据库表名使用 `test_scripts`、`test_executions` 等前缀
- 前端 API 基础地址配置在 `frontend/.env` 中
- 后端配置在 `backend/.env` 中

## 待改进项

1. **日志文件系统** - 将执行日志写入文件，便于长期保存和分析
2. **日志轮转** - 实现日志文件轮转，避免单个文件过大
3. **测试报告** - 生成结构化的测试报告（HTML/JSON）
4. **失败重试** - 支持测试失败后自动重试
5. **并发执行** - 支持多个测试用例并发执行
