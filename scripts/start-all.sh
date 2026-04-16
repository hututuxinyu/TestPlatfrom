#!/bin/bash
# 云手机测试平台 - 一键启动脚本
# 用途：同时启动后端和前端服务

set -e

echo "========================================"
echo "  云手机测试平台 - 一键启动"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查后端虚拟环境
if [ ! -d "backend/.venv" ]; then
    echo "错误: 后端虚拟环境不存在，请先运行 setup-local.sh"
    exit 1
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "错误: 前端依赖未安装，请先运行 setup-local.sh"
    exit 1
fi

# 检查数据库是否初始化
if [ ! -f "backend/data/local.db" ]; then
    echo "数据库未初始化，正在初始化..."
    cd backend
    .venv/Scripts/python -m app.init_db
    cd ..
    echo "数据库初始化完成"
    echo ""
fi

echo "正在启动服务..."
echo ""

# 创建日志目录
mkdir -p logs

# 启动后端服务
echo "[1/2] 启动后端服务 (http://localhost:8000)"
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "后端服务 PID: $BACKEND_PID"

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 启动前端服务
echo "[2/2] 启动前端服务 (http://localhost:5173)"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "前端服务 PID: $FRONTEND_PID"

# 保存 PID 到文件
echo $BACKEND_PID > logs/backend.pid
echo $FRONTEND_PID > logs/frontend.pid

echo ""
echo "========================================"
echo "  服务启动完成！"
echo "========================================"
echo ""
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "默认账号: admin / admin123"
echo ""
echo "日志文件:"
echo "  后端: logs/backend.log"
echo "  前端: logs/frontend.log"
echo ""
echo "停止服务: ./scripts/stop-all.sh"
echo ""

# 等待 3 秒后尝试打开浏览器
sleep 3
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5173 2>/dev/null &
elif command -v open > /dev/null; then
    open http://localhost:5173 2>/dev/null &
elif command -v start > /dev/null; then
    start http://localhost:5173 2>/dev/null &
fi

echo "提示: 服务已在后台运行"
echo "查看日志: tail -f logs/backend.log 或 tail -f logs/frontend.log"
echo ""
