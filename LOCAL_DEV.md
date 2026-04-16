# 本地启动与联调说明

## 1) 环境要求

- Node.js `>= 20`
- npm `>= 10`
- Python `>= 3.9`（建议后续升级到 3.10+，当前先保证本地可启动）
- PowerShell（Windows）

## 2) 后端必须使用虚拟环境

项目已固定使用 `backend/.venv` 作为后端 Python 虚拟环境，不在全局 Python 安装业务依赖。

本地数据库默认使用 SQLite 文件：`backend/data/local.db`。

## 3) 一次性初始化

在仓库根目录执行：

```powershell
.\scripts\setup-local.ps1
```

如果前端依赖已有且你只想更新后端：

```powershell
.\scripts\setup-local.ps1 -SkipFrontend
```

## 4) 一键本地启动

```powershell
.\scripts\start-local.ps1
```

会自动打开两个终端：

- 前端: `http://localhost:5173`
- 后端: `http://localhost:8000`

## 5) 联调检查

后端健康检查：

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

期望响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "database": true
  }
}
```

测试登录 API：

```powershell
$body = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

Invoke-RestMethod -Uri http://localhost:8000/api/v1/auth/login -Method POST -Body $body -ContentType "application/json"
```

期望响应：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "username": "admin"
  }
}
```

默认用户：
- 用户名：`admin`
- 密码：`admin123`

## 6) 常见问题

- 前端安装 `EBUSY`（文件被占用）：
  - 关闭占用 `frontend/node_modules` 的进程（如正在运行的前端 dev server）
  - 重新执行 `.\scripts\setup-local.ps1`
- 后端依赖安装失败：
  - 确认使用的是 `backend/.venv/Scripts/python.exe`
  - 重新执行 `.\scripts\setup-local.ps1 -SkipFrontend`
- 需要重置本地数据库：
  - 删除 `backend/data/local.db`
  - 重新执行 `.\scripts\setup-local.ps1 -SkipFrontend`
