#!/bin/bash
# 云手机测试平台 - 停止服务脚本

echo "========================================"
echo "  停止所有服务"
echo "========================================"
echo ""

# 检查 PID 文件是否存在
if [ ! -f "logs/backend.pid" ] && [ ! -f "logs/frontend.pid" ]; then
    echo "未找到运行中的服务"
    exit 0
fi

# 停止后端服务
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "停止后端服务 (PID: $BACKEND_PID)"
        kill $BACKEND_PID 2>/dev/null || true
        rm logs/backend.pid
    else
        echo "后端服务未运行"
        rm logs/backend.pid 2>/dev/null || true
    fi
fi

# 停止前端服务
if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "停止前端服务 (PID: $FRONTEND_PID)"
        kill $FRONTEND_PID 2>/dev/null || true
        rm logs/frontend.pid
    else
        echo "前端服务未运行"
        rm logs/frontend.pid 2>/dev/null || true
    fi
fi

# 额外清理：查找并停止可能的残留进程
echo ""
echo "清理残留进程..."

# 停止 uvicorn 进程
pkill -f "uvicorn app.main:app" 2>/dev/null || true

# 停止 vite 进程
pkill -f "vite" 2>/dev/null || true

echo ""
echo "所有服务已停止"
echo ""
