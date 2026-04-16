# 📁 项目文件索引

快速查找项目中的重要文件和文档。

## 🚀 启动脚本

| 文件 | 用途 | 适用平台 |
|------|------|----------|
| `scripts/start-all.bat` | 一键启动（推荐） | Windows CMD |
| `scripts/start-all.ps1` | 一键启动 | Windows PowerShell |
| `scripts/start-all.sh` | 一键启动 | Linux/Mac |
| `scripts/stop-all.ps1` | 停止所有服务 | Windows PowerShell |
| `scripts/stop-all.sh` | 停止所有服务 | Linux/Mac |
| `scripts/setup-local.ps1` | 初始化环境 | Windows |

## 📖 文档

| 文件 | 说明 | 推荐阅读顺序 |
|------|------|--------------|
| **DELIVERY.md** | 项目交付总结 | ⭐ 1 |
| **QUICK_START.md** | 快速启动指南 | ⭐ 2 |
| **E2E_TESTING_GUIDE.md** | 端到端测试指南 | ⭐ 3 |
| **README.md** | 项目概述 | 4 |
| **PROJECT_SUMMARY.md** | 项目总结和技术架构 | 5 |
| **LOCAL_DEV.md** | 本地开发说明 | 6 |
| **TESTING_GUIDE.md** | 测试指南 | 7 |

## 🔧 后端核心文件

### API 路由
- `backend/app/api/v1/auth.py` - 认证接口
- `backend/app/api/v1/scripts.py` - 脚本管理接口
- `backend/app/api/v1/executions.py` - 执行管理接口
- `backend/app/api/deps.py` - 依赖注入

### 业务逻辑
- `backend/app/services/auth.py` - 认证服务
- `backend/app/services/script.py` - 脚本服务
- `backend/app/services/execution.py` - 执行服务

### 数据模型
- `backend/app/models/user.py` - 用户模型
- `backend/app/models/script.py` - 脚本模型
- `backend/app/models/execution.py` - 执行模型

### 核心模块
- `backend/app/core/config.py` - 配置管理
- `backend/app/core/errors.py` - 错误码定义
- `backend/app/core/response.py` - 统一响应
- `backend/app/core/exceptions.py` - 异常处理

### 数据库
- `backend/app/db.py` - 数据库初始化
- `backend/app/init_db.py` - 数据库初始化脚本
- `backend/data/local.db` - SQLite 数据库文件

### 配置文件
- `backend/.env` - 环境变量
- `backend/requirements.txt` - Python 依赖

### 入口文件
- `backend/app/main.py` - 应用入口

## 🎨 前端核心文件

### 页面组件
- `frontend/src/pages/LoginPage.tsx` - 登录页面
- `frontend/src/pages/HomePage.tsx` - 主页面布局
- `frontend/src/pages/ScriptManagementPage.tsx` - 脚本管理页面
- `frontend/src/pages/ExecutionManagementPage.tsx` - 执行管理页面

### 通用组件
- `frontend/src/components/ProtectedRoute.tsx` - 路由守卫

### 服务层
- `frontend/src/services/api.ts` - API 服务

### 类型定义
- `frontend/src/types/api.ts` - TypeScript 类型

### 入口文件
- `frontend/src/App.tsx` - 应用入口
- `frontend/src/main.tsx` - 渲染入口

### 配置文件
- `frontend/.env` - 环境变量
- `frontend/package.json` - npm 依赖
- `frontend/vite.config.ts` - Vite 配置
- `frontend/tsconfig.json` - TypeScript 配置

## 📝 示例文件

- `test_imsi_validation.py` - 示例测试脚本（IMSI 验证）

## 📊 OpenSpec 规范

- `openspec/changes/cloud-phone-test-platform/design.md` - 设计文档
- `openspec/changes/cloud-phone-test-platform/tasks.md` - 任务列表
- `openspec/changes/cloud-phone-test-platform/spec.md` - 规范文档

## 🗂️ 目录结构

```
TestPlatfrom/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/v1/            # API 路由
│   │   ├── core/              # 核心模块
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic 模型
│   │   ├── services/          # 业务逻辑
│   │   ├── db.py              # 数据库
│   │   ├── init_db.py         # 初始化脚本
│   │   └── main.py            # 入口文件
│   ├── data/                  # 数据目录
│   │   ├── local.db           # SQLite 数据库
│   │   └── uploads/           # 上传的脚本
│   ├── .venv/                 # Python 虚拟环境
│   ├── .env                   # 环境变量
│   └── requirements.txt       # Python 依赖
│
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── services/         # API 服务
│   │   ├── types/            # TypeScript 类型
│   │   ├── App.tsx           # 应用入口
│   │   └── main.tsx          # 渲染入口
│   ├── node_modules/         # npm 依赖
│   ├── .env                  # 环境变量
│   ├── package.json          # npm 配置
│   └── vite.config.ts        # Vite 配置
│
├── scripts/                   # 启动脚本
│   ├── start-all.bat         # Windows 一键启动
│   ├── start-all.ps1         # PowerShell 一键启动
│   ├── start-all.sh          # Linux/Mac 一键启动
│   ├── stop-all.ps1          # PowerShell 停止服务
│   ├── stop-all.sh           # Linux/Mac 停止服务
│   └── setup-local.ps1       # 环境初始化
│
├── openspec/                  # OpenSpec 规范
│   └── changes/cloud-phone-test-platform/
│       ├── design.md         # 设计文档
│       ├── tasks.md          # 任务列表
│       └── spec.md           # 规范文档
│
├── test_imsi_validation.py   # 示例测试脚本
│
├── DELIVERY.md               # 项目交付总结 ⭐
├── QUICK_START.md            # 快速启动指南 ⭐
├── E2E_TESTING_GUIDE.md      # 端到端测试指南 ⭐
├── README.md                 # 项目概述
├── PROJECT_SUMMARY.md        # 项目总结
├── LOCAL_DEV.md              # 本地开发说明
├── TESTING_GUIDE.md          # 测试指南
└── FILE_INDEX.md             # 本文件
```

## 🔍 快速查找

### 我想...

**启动系统**
→ 运行 `scripts/start-all.bat`（Windows）或 `scripts/start-all.sh`（Linux/Mac）

**了解如何使用**
→ 阅读 `QUICK_START.md`

**查看完整功能**
→ 阅读 `E2E_TESTING_GUIDE.md`

**了解技术架构**
→ 阅读 `PROJECT_SUMMARY.md`

**修改后端 API**
→ 编辑 `backend/app/api/v1/*.py`

**修改前端页面**
→ 编辑 `frontend/src/pages/*.tsx`

**添加新的业务逻辑**
→ 编辑 `backend/app/services/*.py`

**修改数据库结构**
→ 编辑 `backend/app/db.py`

**修改错误码**
→ 编辑 `backend/app/core/errors.py`

**添加新的 API 接口**
→ 在 `backend/app/api/v1/` 创建新文件或修改现有文件

**添加新的前端页面**
→ 在 `frontend/src/pages/` 创建新文件，并在 `App.tsx` 中添加路由

**查看示例测试脚本**
→ 查看 `test_imsi_validation.py`

**停止服务**
→ 运行 `scripts/stop-all.ps1`（Windows）或 `scripts/stop-all.sh`（Linux/Mac）

## 📌 重要提示

1. **首次使用**：先阅读 `DELIVERY.md` 了解项目概况
2. **快速启动**：使用 `scripts/start-all.bat` 一键启动
3. **遇到问题**：查看 `QUICK_START.md` 的常见问题部分
4. **开发扩展**：参考 `PROJECT_SUMMARY.md` 的技术架构

## 🎯 核心文件（必读）

1. `DELIVERY.md` - 项目交付总结
2. `QUICK_START.md` - 快速启动指南
3. `scripts/start-all.bat` - 一键启动脚本
4. `backend/app/main.py` - 后端入口
5. `frontend/src/App.tsx` - 前端入口

---

**提示**：使用 Ctrl+F 在本文件中搜索你需要的内容！
