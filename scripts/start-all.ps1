#!/usr/bin/env pwsh
# 云手机测试平台 - 一键启动脚本
# 用途：同时启动后端和前端服务

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  云手机测试平台 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否在项目根目录
if (-not (Test-Path "backend") -or -not (Test-Path "frontend")) {
    Write-Host "错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 检查后端虚拟环境
if (-not (Test-Path "backend/.venv")) {
    Write-Host "错误: 后端虚拟环境不存在，请先运行 setup-local.ps1" -ForegroundColor Red
    exit 1
}

# 检查前端依赖
if (-not (Test-Path "frontend/node_modules")) {
    Write-Host "错误: 前端依赖未安装，请先运行 setup-local.ps1" -ForegroundColor Red
    exit 1
}

# 检查数据库是否初始化
if (-not (Test-Path "backend/data/local.db")) {
    Write-Host "数据库未初始化，正在初始化..." -ForegroundColor Yellow
    Push-Location backend
    .venv/Scripts/python -m app.init_db
    Pop-Location
    Write-Host "数据库初始化完成" -ForegroundColor Green
    Write-Host ""
}

Write-Host "正在启动服务..." -ForegroundColor Green
Write-Host ""

# 启动后端服务（新窗口）
Write-Host "[1/2] 启动后端服务 (http://localhost:8000)" -ForegroundColor Cyan
$backendScript = @"
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  后端服务 - FastAPI' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '服务地址: http://localhost:8000' -ForegroundColor Green
Write-Host 'API 文档: http://localhost:8000/docs' -ForegroundColor Green
Write-Host ''
Write-Host '按 Ctrl+C 停止服务' -ForegroundColor Yellow
Write-Host ''
Set-Location '$PWD/backend'
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendScript

# 等待后端启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 启动前端服务（新窗口）
Write-Host "[2/2] 启动前端服务 (http://localhost:5173)" -ForegroundColor Cyan
$frontendScript = @"
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  前端服务 - Vite + React' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '服务地址: http://localhost:5173' -ForegroundColor Green
Write-Host ''
Write-Host '按 Ctrl+C 停止服务' -ForegroundColor Yellow
Write-Host ''
Set-Location '$PWD/frontend'
npm run dev
"@

Start-Process pwsh -ArgumentList "-NoExit", "-Command", $frontendScript

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "前端地址: " -NoNewline
Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "后端地址: " -NoNewline
Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "API 文档: " -NoNewline
Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "默认账号: " -NoNewline
Write-Host "admin / admin123" -ForegroundColor Yellow
Write-Host ""
Write-Host "提示: 两个服务窗口已打开，关闭窗口即可停止服务" -ForegroundColor Gray
Write-Host ""

# 等待 3 秒后自动打开浏览器
Write-Host "3 秒后自动打开浏览器..." -ForegroundColor Gray
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "按任意键退出此窗口（不影响服务运行）..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
