@echo off
REM 云手机测试平台 - 一键启动脚本 (Windows CMD)
REM 用途：同时启动后端和前端服务

echo ========================================
echo   云手机测试平台 - 一键启动
echo ========================================
echo.

REM 检查是否在项目根目录
if not exist "backend" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "frontend" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查后端虚拟环境
if not exist "backend\.venv" (
    echo 错误: 后端虚拟环境不存在，请先运行 setup-local.ps1
    pause
    exit /b 1
)

REM 检查前端依赖
if not exist "frontend\node_modules" (
    echo 错误: 前端依赖未安装，请先运行 setup-local.ps1
    pause
    exit /b 1
)

REM 检查数据库是否初始化
if not exist "backend\data\local.db" (
    echo 数据库未初始化，正在初始化...
    cd backend
    .venv\Scripts\python -m app.init_db
    cd ..
    echo 数据库初始化完成
    echo.
)

echo 正在启动服务...
echo.

REM 启动后端服务（新窗口）
echo [1/2] 启动后端服务 (http://localhost:8000)
start "后端服务 - FastAPI" cmd /k "cd /d %CD%\backend && echo ======================================== && echo   后端服务 - FastAPI && echo ======================================== && echo. && echo 服务地址: http://localhost:8000 && echo API 文档: http://localhost:8000/docs && echo. && echo 按 Ctrl+C 停止服务 && echo. && .venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM 等待后端启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

REM 启动前端服务（新窗口）
echo [2/2] 启动前端服务 (http://localhost:5173)
start "前端服务 - Vite + React" cmd /k "cd /d %CD%\frontend && echo ======================================== && echo   前端服务 - Vite + React && echo ======================================== && echo. && echo 服务地址: http://localhost:5173 && echo. && echo 按 Ctrl+C 停止服务 && echo. && npm run dev"

echo.
echo ========================================
echo   服务启动完成！
echo ========================================
echo.
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 默认账号: admin / admin123
echo.
echo 提示: 两个服务窗口已打开，关闭窗口即可停止服务
echo.

REM 等待 3 秒后自动打开浏览器
echo 3 秒后自动打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo 按任意键退出此窗口（不影响服务运行）...
pause >nul
