# 云手机测试平台

一个完整的端到端测试评测平台，支持测试脚本管理、执行和结果收集。

## 🚀 快速开始

### 方式一：一键启动（推荐）

**Windows 用户：**

双击运行 `scripts/start-all.bat` 或在项目根目录执行：

```cmd
.\scripts\start-all.bat
```

或使用 PowerShell：

```powershell
.\scripts\start-all.ps1
```

**Linux/Mac 用户：**

```bash
chmod +x scripts/start-all.sh
./scripts/start-all.sh
```

### 方式二：手动启动

#### 1. 首次安装依赖

```powershell
# Windows
.\scripts\setup-local.ps1

# Linux/Mac
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh
```

#### 2. 启动后端

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 3. 启动前端

```bash
cd frontend
npm run dev
```

### 访问系统

- **前端地址**：http://localhost:5173
- **后端地址**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **默认账号**：admin / admin123

## 📖 功能特性

### ✅ 用户认证
- JWT 令牌认证
- 密码安全存储（bcrypt）
- 登录/登出功能
- 路由守卫保护

### ✅ 脚本管理
- 上传测试脚本（支持 Python/Shell/JavaScript）
- 脚本 CRUD 操作
- 搜索和筛选
- 查看脚本内容

### ✅ 执行管理
- 一键执行测试脚本
- 异步执行引擎
- 实时状态更新
- 执行停止功能

### ✅ 结果收集
- stdout/stderr 实时采集
- 系统日志记录
- 日志查询和展示
- 执行时长统计

## 📝 完整测试流程

1. **登录系统** - 使用 admin/admin123 登录
2. **上传脚本** - 上传测试脚本（如 test_imsi_validation.py）
3. **执行测试** - 点击"执行"按钮
4. **查看结果** - 查看执行状态和日志

## 🛠️ 技术栈

### 后端
- FastAPI 0.128.8
- Python 3.9+
- SQLite
- bcrypt + PyJWT

### 前端
- React 19.2.4
- TypeScript 6.0.2
- Vite 8.0.4
- Ant Design 6.3.5

## 📁 项目结构

```
TestPlatfrom/
├── backend/              # 后端服务
│   ├── app/             # 应用代码
│   ├── data/            # 数据库和上传文件
│   └── .venv/           # Python 虚拟环境
├── frontend/            # 前端应用
│   ├── src/            # 源代码
│   └── node_modules/   # npm 依赖
├── scripts/            # 启动脚本
│   ├── start-all.bat   # Windows 一键启动
│   ├── start-all.ps1   # PowerShell 一键启动
│   ├── start-all.sh    # Linux/Mac 一键启动
│   ├── stop-all.ps1    # PowerShell 停止服务
│   └── stop-all.sh     # Linux/Mac 停止服务
└── docs/               # 文档
```

## 📚 文档

- **E2E_TESTING_GUIDE.md** - 完整的端到端测试指南
- **PROJECT_SUMMARY.md** - 项目总结和技术架构
- **LOCAL_DEV.md** - 本地开发说明
- **TESTING_GUIDE.md** - 测试指南

## 🎯 示例测试脚本

项目根目录下的 `test_imsi_validation.py` 是一个完整的测试脚本示例：

```python
#!/usr/bin/env python3
"""IMSI 非空验证测试脚本"""
import sys
import time

def test_imsi_not_empty():
    print("开始执行 IMSI 非空验证测试...")
    # ... 测试逻辑
    return True

if __name__ == "__main__":
    success = test_imsi_not_empty()
    sys.exit(0 if success else 1)
```

## 🔧 停止服务

**Windows：**
```powershell
.\scripts\stop-all.ps1
```

**Linux/Mac：**
```bash
./scripts/stop-all.sh
```

或直接关闭启动的终端窗口。

## 🐛 故障排查

### 端口被占用
如果 8000 或 5173 端口被占用，请先停止占用端口的进程。

### 数据库初始化失败
删除 `backend/data/local.db` 后重新运行启动脚本。

### 依赖安装失败
确保已安装 Python 3.9+ 和 Node.js 20+，然后重新运行 `setup-local.ps1`。

## 📊 API 接口

### 认证
- `POST /api/v1/auth/login` - 登录
- `POST /api/v1/auth/logout` - 登出
- `GET /api/v1/auth/me` - 获取当前用户

### 脚本管理
- `POST /api/v1/scripts/upload` - 上传脚本
- `GET /api/v1/scripts` - 获取脚本列表
- `GET /api/v1/scripts/{id}` - 获取脚本详情
- `PUT /api/v1/scripts/{id}` - 更新脚本
- `DELETE /api/v1/scripts/{id}` - 删除脚本

### 执行管理
- `POST /api/v1/executions` - 创建执行任务
- `GET /api/v1/executions` - 获取执行列表
- `GET /api/v1/executions/{id}/logs` - 获取执行日志
- `POST /api/v1/executions/{id}/stop` - 停止执行

## 🎓 开发指南

### 添加新的测试脚本
1. 编写测试脚本（Python/Shell/JavaScript）
2. 确保脚本有正确的退出码（0 成功，非 0 失败）
3. 通过前端上传或 API 上传

### 扩展功能
- 查看 `backend/app/api/v1/` 添加新的 API 路由
- 查看 `frontend/src/pages/` 添加新的页面
- 查看 `backend/app/services/` 添加新的业务逻辑

## 📞 支持

如有问题，请查看：
- API 文档：http://localhost:8000/docs
- 项目文档：查看 docs/ 目录
- 后端日志：控制台输出
- 前端日志：浏览器开发者工具

## 📄 许可证

本项目仅供内部使用。

---

**快速开始**：运行 `.\scripts\start-all.bat` 即可启动整个平台！
