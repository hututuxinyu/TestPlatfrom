# 快速启动指南

## 🚀 一键启动（最简单）

### Windows 用户

**方式 1：双击启动（推荐）**

直接双击 `scripts/start-all.bat` 文件即可！

**方式 2：命令行启动**

在项目根目录打开 CMD 或 PowerShell，执行：

```cmd
# CMD
.\scripts\start-all.bat

# PowerShell
.\scripts\start-all.ps1
```

### Linux/Mac 用户

在项目根目录打开终端，执行：

```bash
chmod +x scripts/start-all.sh
./scripts/start-all.sh
```

## ✅ 启动成功标志

启动脚本会自动：

1. ✅ 检查数据库是否初始化（如未初始化会自动初始化）
2. ✅ 启动后端服务（新窗口，端口 8000）
3. ✅ 启动前端服务（新窗口，端口 5173）
4. ✅ 自动打开浏览器访问 http://localhost:5173

你会看到两个新的终端窗口：
- **后端服务窗口** - 显示 FastAPI 日志
- **前端服务窗口** - 显示 Vite 开发服务器日志

## 🌐 访问系统

浏览器会自动打开，如果没有自动打开，请手动访问：

**http://localhost:5173**

默认账号：
- 用户名：`admin`
- 密码：`admin123`

## 🎯 快速测试流程

### 1. 登录
- 打开 http://localhost:5173
- 输入 admin / admin123
- 点击"登录"

### 2. 上传测试脚本
- 进入"脚本管理"页面
- 点击"上传脚本"
- 填写信息：
  - 名称：IMSI 非空验证测试
  - 描述：验证云手机的 IMSI 是否正确配置
  - 语言：Python
  - 标签：IMSI,功能测试
  - 文件：选择 `test_imsi_validation.py`
- 点击"确定"

### 3. 执行测试
- 在脚本列表中找到刚上传的脚本
- 点击"执行"按钮
- 系统自动跳转到执行管理页面

### 4. 查看结果
- 在执行管理页面查看执行状态
- 点击"日志"按钮查看详细日志
- 查看退出码和执行时长

## 🛑 停止服务

### Windows

**方式 1：关闭窗口**
直接关闭后端和前端的终端窗口即可。

**方式 2：运行停止脚本**
```powershell
.\scripts\stop-all.ps1
```

### Linux/Mac

```bash
./scripts/stop-all.sh
```

## ⚠️ 常见问题

### 问题 1：端口被占用

**错误信息**：`Address already in use` 或 `端口 8000/5173 已被占用`

**解决方法**：
1. 运行停止脚本停止之前的服务
2. 或手动查找并停止占用端口的进程

Windows：
```powershell
# 查找占用 8000 端口的进程
netstat -ano | findstr :8000
# 停止进程（替换 PID）
taskkill /PID <PID> /F
```

### 问题 2：数据库文件损坏

**错误信息**：`database disk image is malformed`

**解决方法**：
```bash
# 删除数据库文件
rm backend/data/local.db
# 重新运行启动脚本，会自动初始化
```

### 问题 3：依赖未安装

**错误信息**：`后端虚拟环境不存在` 或 `前端依赖未安装`

**解决方法**：
```powershell
# Windows
.\scripts\setup-local.ps1

# Linux/Mac
./scripts/setup-local.sh
```

### 问题 4：Python 版本不兼容

**错误信息**：`TypeError: unsupported operand type(s) for |`

**解决方法**：
确保使用 Python 3.9 或更高版本：
```bash
python --version
```

### 问题 5：浏览器未自动打开

**解决方法**：
手动打开浏览器访问 http://localhost:5173

## 📊 服务状态检查

### 检查后端服务

访问：http://localhost:8000/api/v1/health

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

### 检查前端服务

访问：http://localhost:5173

应该能看到登录页面。

### 检查 API 文档

访问：http://localhost:8000/docs

应该能看到 Swagger API 文档。

## 🔧 高级选项

### 仅启动后端

```bash
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 仅启动前端

```bash
cd frontend
npm run dev
```

### 修改端口

编辑配置文件：
- 后端端口：修改 `backend/.env` 中的 `APP_PORT`
- 前端端口：修改 `frontend/vite.config.ts` 中的 `server.port`

### 查看日志

**后端日志**：查看后端服务窗口的输出

**前端日志**：查看前端服务窗口的输出

**浏览器日志**：按 F12 打开开发者工具，查看 Console

## 📱 移动端访问

如果需要在同一局域网的其他设备访问：

1. 查找本机 IP 地址：
   ```bash
   # Windows
   ipconfig

   # Linux/Mac
   ifconfig
   ```

2. 在其他设备浏览器访问：
   ```
   http://<你的IP>:5173
   ```

3. 确保防火墙允许 5173 和 8000 端口访问。

## 🎉 成功启动的标志

当你看到以下内容时，说明启动成功：

✅ 后端窗口显示：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ 前端窗口显示：
```
VITE v8.0.4  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

✅ 浏览器自动打开并显示登录页面

## 💡 提示

- 启动脚本会自动检查并初始化数据库
- 服务启动后会自动打开浏览器
- 关闭终端窗口即可停止服务
- 修改代码后会自动热重载（无需重启）

---

**现在就开始吧！运行 `.\scripts\start-all.bat` 启动你的测试平台！** 🚀
