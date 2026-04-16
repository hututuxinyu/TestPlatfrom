#!/usr/bin/env pwsh
# 云手机测试平台 - 停止服务脚本

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  停止所有服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$stopped = $false

# 停止 uvicorn 进程（后端）
Write-Host "正在查找后端服务..." -ForegroundColor Yellow
$backendProcesses = Get-Process | Where-Object { $_.ProcessName -like "*python*" -and $_.CommandLine -like "*uvicorn*" }
if ($backendProcesses) {
    foreach ($proc in $backendProcesses) {
        Write-Host "停止后端服务 (PID: $($proc.Id))" -ForegroundColor Green
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
} else {
    Write-Host "未找到运行中的后端服务" -ForegroundColor Gray
}

# 停止 node 进程（前端）
Write-Host "正在查找前端服务..." -ForegroundColor Yellow
$frontendProcesses = Get-Process | Where-Object { $_.ProcessName -like "*node*" -and $_.CommandLine -like "*vite*" }
if ($frontendProcesses) {
    foreach ($proc in $frontendProcesses) {
        Write-Host "停止前端服务 (PID: $($proc.Id))" -ForegroundColor Green
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
} else {
    Write-Host "未找到运行中的前端服务" -ForegroundColor Gray
}

# 额外清理：停止所有相关的 PowerShell 窗口
Write-Host ""
Write-Host "清理相关进程..." -ForegroundColor Yellow

# 停止所有包含 uvicorn 的 Python 进程
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmdLine -like "*uvicorn*app.main*") {
        Write-Host "清理后端进程 (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
}

# 停止所有包含 vite 的 Node 进程
Get-Process node -ErrorAction SilentlyContinue | ForEach-Object {
    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmdLine -like "*vite*") {
        Write-Host "清理前端进程 (PID: $($_.Id))" -ForegroundColor Gray
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        $stopped = $true
    }
}

Write-Host ""
if ($stopped) {
    Write-Host "所有服务已停止" -ForegroundColor Green
} else {
    Write-Host "没有找到运行中的服务" -ForegroundColor Yellow
}
Write-Host ""
