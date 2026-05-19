#!/bin/bash
#=============================================================================
# 云手机测试平台 - 编译 / 运行 / 停止 管理脚本
# 支持 Linux 和 Windows (Git Bash / MSYS2 / Cygwin) 双平台
# 用法:
#   ./run.sh build             编译后端和前端
#   ./run.sh build-backend     仅编译后端
#   ./run.sh build-frontend    仅编译前端
#   ./run.sh start             启动所有服务
#   ./run.sh start-backend     仅启动后端
#   ./run.sh start-frontend    仅启动前端
#   ./run.sh stop              停止所有服务
#   ./run.sh stop-backend      仅停止后端
#   ./run.sh stop-frontend     仅停止前端
#   ./run.sh restart           重启所有服务
#   ./run.sh status            查看服务状态
#   ./run.sh logs              查看所有日志
#   ./run.sh logs-backend      查看后端日志
#   ./run.sh logs-frontend     查看前端日志
#=============================================================================

set -e

#=============================================================================
# 配置区（可按需修改）
#=============================================================================

# 项目根目录（脚本所在目录）
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 后端相关路径
BACKEND_DIR="$ROOT_DIR/backend-go"
BACKEND_MAIN="$BACKEND_DIR/cmd/server/main.go"
BACKEND_BIN="server"
BACKEND_LOG="$BACKEND_DIR/logs/backend.log"

# 前端相关路径
FRONTEND_DIR="$ROOT_DIR/frontend"
FRONTEND_LOG="$ROOT_DIR/logs/frontend.log"

# PID 文件存放目录（放在项目根目录，便于开发者直观了解，已加入 .gitignore）
PID_DIR="$ROOT_DIR/run"
BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"

# 后端服务端口（用于检查端口占用）
BACKEND_PORT=8011
# 前端服务端口
FRONTEND_PORT=5173

# 公共 IP 地址（默认为空，表示本地 localhost 模式）
# 通过 --public 或 --host=<IP> 参数设置，用于服务器部署时自动切换
PUBLIC_IP=""

# 颜色输出（检测是否支持）
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

#=============================================================================
# 辅助函数
#=============================================================================

# 打印带颜色的信息
log_info()    { echo -e "${GREEN}[信息]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[警告]${NC} $*"; }
log_error()   { echo -e "${RED}[错误]${NC} $*"; }
log_step()    { echo -e "${BLUE}[步骤]${NC} $*"; }

# 检测是否为 Windows 环境（Git Bash / MSYS2 / Cygwin）
is_windows() {
    case "$(uname -s)" in
        MINGW*|MSYS*|CYGWIN*) return 0 ;;
        *) return 1 ;;
    esac
}

# 获取适用于当前平台的后端可执行文件名
get_backend_bin() {
    if is_windows; then
        echo "${BACKEND_BIN}.exe"
    else
        echo "${BACKEND_BIN}"
    fi
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "未找到命令: $1，请先安装"
        exit 1
    fi
}

# 创建 PID 目录（如不存在）
ensure_pid_dir() {
    if [ ! -d "$PID_DIR" ]; then
        mkdir -p "$PID_DIR"
    fi
}

# 创建日志目录（如不存在）
ensure_log_dir() {
    local log_file="$1"
    local log_dir
    log_dir="$(dirname "$log_file")"
    if [ ! -d "$log_dir" ]; then
        mkdir -p "$log_dir"
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local name=$2
    if is_windows; then
        # Windows 下使用 netstat 检查端口
        if netstat -ano 2>/dev/null | grep -q ":$port "; then
            log_warn "$name 端口 $port 已被占用"
            return 0
        fi
    else
        # Linux 下使用 ss 或 /proc 检查端口
        if command -v ss &> /dev/null; then
            if ss -tlnp 2>/dev/null | grep -q ":$port "; then
                log_warn "$name 端口 $port 已被占用"
                return 0
            fi
        else
            if cat /proc/net/tcp 2>/dev/null | grep -q "$(printf '%04X' $port)"; then
                log_warn "$name 端口 $port 已被占用"
                return 0
            fi
        fi
    fi
    return 1
}

# 强制释放指定端口（查找占用进程并杀死）
# 用于端口冲突时自动清理，避免启动失败
kill_port() {
    local port=$1
    local name=$2
    local pid=""

    if is_windows; then
        # Windows 下通过 netstat 查找占用端口的 PID
        pid=$(netstat -ano 2>/dev/null | grep ":$port " | awk '{print $NF}' | head -1)
    else
        # Linux 下通过 ss 或 fuser 查找 PID
        if command -v ss &> /dev/null; then
            pid=$(ss -tlnp 2>/dev/null | grep ":$port " | grep -oP 'pid=\K[0-9]+' | head -1)
        elif command -v fuser &> /dev/null; then
            pid=$(fuser "$port/tcp" 2>/dev/null | head -1)
        fi
    fi

    if [ -n "$pid" ]; then
        log_warn "端口 $port 被进程 PID=$pid 占用，正在释放..."
        kill "$pid" 2>/dev/null || true
        sleep 1
        if kill -0 "$pid" 2>/dev/null; then
            kill -9 "$pid" 2>/dev/null || true
            log_info "已强制终止进程 (PID: $pid)"
        else
            log_info "进程 (PID: $pid) 已终止，端口 $port 已释放"
        fi
        return 0
    fi
    return 1
}

# 读取 PID 文件并检查进程是否存在
# 输出: PID 数字（进程运行中）或空字符串（未运行）
# 注意: 始终返回 0，避免与 set -e 冲突
read_pid() {
    local pid_file="$1"
    if [ -f "$pid_file" ]; then
        local pid
        pid=$(cat "$pid_file" 2>/dev/null || true)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            echo "$pid"
        fi
    fi
}

# 检查后端配置文件是否存在
check_backend_env() {
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        log_warn "后端的 .env 配置文件不存在: $BACKEND_DIR/.env"
        log_info "请参考以下模板创建配置文件："
        echo ""
        echo "  cat > $BACKEND_DIR/.env << 'EOF'"
        echo "  # 服务配置"
        echo "  SERVER_PORT=${BACKEND_PORT}"
        echo ""
        echo "  # 数据库配置（根据实际数据库信息修改）"
        echo "  DB_HOST=localhost"
        echo "  DB_PORT=3306"
        echo "  DB_USER=root"
        echo "  DB_PASSWORD=1234"
        echo "  DB_NAME=testplatform"
        echo ""
        echo "  # JWT 配置（生产环境请更换为安全的随机字符串）"
        echo "  JWT_SECRET=your-secret-key"
        echo "  JWT_EXPIRATION=24h"
        echo "  EOF"
        echo ""
        return 1
    fi
}

# 自动检测服务器主 IP（排除 127.0.0.1 回环地址）
# 用于 --public 模式时自动获取本机 IP
detect_ip() {
    if is_windows; then
        # Windows 下通过 ipconfig 获取第一个非回环 IPv4 地址
        local ip
        ip=$(ipconfig 2>/dev/null | grep -i "IPv4" | awk '{print $NF}' | grep -v "127.0.0.1" | head -1)
        if [ -n "$ip" ]; then
            echo "$ip"
            return 0
        fi
    else
        # Linux 下优先使用 hostname -I（最可靠）
        if command -v hostname &> /dev/null; then
            local ip
            ip=$(hostname -I 2>/dev/null | awk '{print $1}')
            if [ -n "$ip" ] && [ "$ip" != "127.0.0.1" ]; then
                echo "$ip"
                return 0
            fi
        fi
        # 备选方案：通过 ip route 获取默认路由的源地址
        if command -v ip &> /dev/null; then
            local ip
            ip=$(ip route get 1 2>/dev/null | awk '{print $NF; exit}')
            if [ -n "$ip" ] && [ "$ip" != "127.0.0.1" ]; then
                echo "$ip"
                return 0
            fi
        fi
    fi
    return 1
}

#=============================================================================
# 编译函数
#=============================================================================

# 编译后端
build_backend() {
    log_step "===== 开始编译后端 ====="

    # 进入后端目录
    cd "$BACKEND_DIR"

    # 检查 Go 环境
    check_command "go"

    local bin_name
    bin_name=$(get_backend_bin)

    log_info "目标平台: $(uname -s)"
    log_info "输出文件: $BACKEND_DIR/$bin_name"

    # 编译后端
    # CGO_ENABLED=0 禁用 CGO，保证静态编译，跨平台兼容性更好
    # -ldflags="-w -s" 去掉调试信息和符号表，减小二进制体积
    if [ "$1" = "release" ]; then
        # 正式编译（带优化）
        log_info "编译模式: release（优化体积）"
        CGO_ENABLED=0 go build -a -installsuffix cgo -ldflags="-w -s" -o "$bin_name" ./cmd/server
    else
        # 开发编译（保留调试信息）
        log_info "编译模式: debug（保留调试信息）"
        CGO_ENABLED=0 go build -o "$bin_name" ./cmd/server
    fi

    log_info "后端编译成功: $BACKEND_DIR/$bin_name"

    # 返回项目根目录
    cd "$ROOT_DIR"
}

# 编译前端（安装依赖）
build_frontend() {
    log_step "===== 开始构建前端 ====="

    # 进入前端目录
    cd "$FRONTEND_DIR"

    # 检查 Node.js 和 npm 环境
    check_command "node"
    check_command "npm"

    log_info "Node.js 版本: $(node -v)"
    log_info "npm 版本: $(npm -v)"

    # 检查 node_modules 是否存在，不存在则安装依赖
    if [ ! -d "node_modules" ]; then
        log_info "检测到 node_modules 不存在，正在安装依赖..."
        npm install
        log_info "依赖安装完成"
    else
        log_info "node_modules 已存在，跳过安装"
        log_info "如需强制重新安装，请执行: cd frontend && rm -rf node_modules && npm install"
    fi

    log_info "前端构建准备完成"

    # 返回项目根目录
    cd "$ROOT_DIR"
}

# 编译全部
build_all() {
    log_step "========== 开始编译全部组件 =========="
    build_backend "$1"
    build_frontend
    log_step "========== 全部编译完成 =========="
}

#=============================================================================
# 启动函数
#=============================================================================

# 启动后端服务
start_backend() {
    log_step "===== 启动后端服务 ====="

    # 检查 PID，防止重复启动
    local existing_pid
    existing_pid=$(read_pid "$BACKEND_PID_FILE")
    if [ -n "$existing_pid" ]; then
        log_warn "后端服务已在运行中 (PID: $existing_pid)"
        log_info "如需重启，请执行: $0 restart-backend"
        return 0
    fi

    # 检查端口是否被占用，如果被占用则自动释放
    if check_port "$BACKEND_PORT" "后端"; then
        log_info "尝试自动释放端口 $BACKEND_PORT..."
        kill_port "$BACKEND_PORT" "后端" || true
        sleep 1
    fi

    # 检查后端配置文件
    check_backend_env

    # 检查后端二进制文件是否存在
    local bin_name
    bin_name=$(get_backend_bin)
    if [ ! -f "$BACKEND_DIR/$bin_name" ]; then
        log_warn "后端可执行文件不存在，正在自动编译..."
        build_backend
    fi

    # 确保日志目录存在
    ensure_log_dir "$BACKEND_LOG"

    # 进入后端目录并启动服务
    cd "$BACKEND_DIR"

    log_info "启动后端服务 (端口: $BACKEND_PORT)..."
    log_info "日志文件: $BACKEND_LOG"

    # 使用 nohup 后台启动，输出重定向到日志文件
    # 2>&1 将标准错误也重定向到日志
    nohup "./$bin_name" >> "$BACKEND_LOG" 2>&1 &
    local pid=$!

    # 保存 PID 到文件
    ensure_pid_dir
    echo "$pid" > "$BACKEND_PID_FILE"

    log_info "后端服务已启动 (PID: $pid)"

    # 等一小会检查进程是否存活
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
        log_info "后端服务启动成功 (PID: $pid)"
    else
        log_error "后端服务启动失败，请查看日志: $BACKEND_LOG"
        # 清理 PID 文件
        rm -f "$BACKEND_PID_FILE"
        cd "$ROOT_DIR"
        return 1
    fi

    # 返回项目根目录
    cd "$ROOT_DIR"
}

# 启动前端服务
start_frontend() {
    log_step "===== 启动前端服务 ====="

    # 检查 PID，防止重复启动
    local existing_pid
    existing_pid=$(read_pid "$FRONTEND_PID_FILE")
    if [ -n "$existing_pid" ]; then
        log_warn "前端服务已在运行中 (PID: $existing_pid)"
        log_info "如需重启，请执行: $0 restart-frontend"
        return 0
    fi

    # 检查端口是否被占用，如果被占用则自动释放
    if check_port "$FRONTEND_PORT" "前端"; then
        log_info "尝试自动释放端口 $FRONTEND_PORT..."
        kill_port "$FRONTEND_PORT" "前端" || true
        sleep 1
    fi

    # 检查 node_modules 是否存在
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
        log_warn "node_modules 不存在，正在自动安装依赖..."
        build_frontend
    fi

    # 确保日志目录存在
    ensure_log_dir "$FRONTEND_LOG"

    # 进入前端目录并启动服务
    cd "$FRONTEND_DIR"

    log_info "启动前端开发服务器 (端口: $FRONTEND_PORT)..."
    log_info "日志文件: $FRONTEND_LOG"

    # 如果设置了 PUBLIC_IP（--public 模式），注入 VITE_API_BASE_URL 环境变量
    # 这样前端 axios 会请求 http://<服务器IP>:8011 而非 localhost
    if [ -n "$PUBLIC_IP" ]; then
        export VITE_API_BASE_URL="http://${PUBLIC_IP}:${BACKEND_PORT}"
        log_info "前端 API 地址已切换为: $VITE_API_BASE_URL"
    fi

    # 使用 npm run dev 启动 Vite 开发服务器
    # 通过 --port 明确指定端口（与 vite.config.ts 中的 strictPort 配合）
    nohup npm run dev -- --port "$FRONTEND_PORT" >> "$FRONTEND_LOG" 2>&1 &
    local pid=$!

    # 保存 PID 到文件
    ensure_pid_dir
    echo "$pid" > "$FRONTEND_PID_FILE"

    log_info "前端服务已启动 (PID: $pid)"

    # 等一小会检查进程是否存活
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        log_info "前端服务启动成功 (PID: $pid)"
    else
        log_error "前端服务启动失败，请查看日志: $FRONTEND_LOG"
        rm -f "$FRONTEND_PID_FILE"
        cd "$ROOT_DIR"
        return 1
    fi

    # 返回项目根目录
    cd "$ROOT_DIR"
}

# 启动全部服务
start_all() {
    log_step "========== 启动所有服务 =========="
    start_backend
    start_frontend
    log_step "========== 所有服务启动完成 =========="
    echo ""
    if [ -n "$PUBLIC_IP" ]; then
        # 公共模式：打印服务器 IP 地址，方便其他机器访问
        log_info "前端地址: http://${PUBLIC_IP}:${FRONTEND_PORT}"
        log_info "后端地址: http://${PUBLIC_IP}:${BACKEND_PORT}"
        log_info "（其他设备可通过上述地址在浏览器中访问）"
    else
        # 本地模式：打印 localhost 地址
        log_info "前端地址: http://localhost:${FRONTEND_PORT}"
        log_info "后端地址: http://localhost:${BACKEND_PORT}"
    fi
    log_info "默认账号: admin / admin123"
    echo ""
    log_info "查看运行状态: $0 status"
    log_info "查看后端日志: $0 logs-backend"
    log_info "查看前端日志: $0 logs-frontend"
}

#=============================================================================
# 停止函数
#=============================================================================

# 停止指定服务（通过 PID 文件）
stop_service() {
    local pid_file="$1"
    local service_name="$2"

    local pid
    pid=$(read_pid "$pid_file")
    if [ -z "$pid" ]; then
        log_warn "$service_name 未在运行"
        rm -f "$pid_file"
        return 0
    fi

    log_info "正在停止 $service_name (PID: $pid)..."

    # 先尝试优雅停止（SIGTERM）
    kill "$pid" 2>/dev/null || true

    # 等待最多 5 秒，让进程自行退出
    local wait_time=0
    while [ $wait_time -lt 5 ]; do
        if ! kill -0 "$pid" 2>/dev/null; then
            log_info "$service_name 已停止"
            rm -f "$pid_file"
            return 0
        fi
        sleep 1
        wait_time=$((wait_time + 1))
    done

    # 如果 5 秒后仍未退出，强制杀死（SIGKILL）
    log_warn "$service_name 未响应 SIGTERM，正在强制停止..."
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$pid_file"
    log_info "$service_name 已强制停止"
}

# 停止后端
stop_backend() {
    stop_service "$BACKEND_PID_FILE" "后端服务"
}

# 停止前端
stop_frontend() {
    stop_service "$FRONTEND_PID_FILE" "前端服务"
}

# 停止全部服务
stop_all() {
    log_step "========== 停止所有服务 =========="
    stop_backend
    stop_frontend
    log_step "========== 所有服务已停止 =========="
}

#=============================================================================
# 状态 / 日志 函数
#=============================================================================

# 查看服务状态
show_status() {
    log_step "===== 服务运行状态 ====="

    local backend_pid
    local frontend_pid
    backend_pid=$(read_pid "$BACKEND_PID_FILE")
    frontend_pid=$(read_pid "$FRONTEND_PID_FILE")

    # 后端状态
    if [ -n "$backend_pid" ]; then
        # 获取进程详细信息
        if is_windows; then
            log_info "后端服务: ${GREEN}运行中${NC} (PID: $backend_pid)"
        else
            local backend_mem
            backend_mem=$(ps -o rss= -p "$backend_pid" 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
            local backend_uptime
            backend_uptime=$(ps -o etime= -p "$backend_pid" 2>/dev/null)
            log_info "后端服务: ${GREEN}运行中${NC} (PID: $backend_pid, 内存: ${backend_mem:-N/A}, 运行时间: ${backend_uptime:-N/A})"
        fi
        log_info "  接口地址: http://localhost:${BACKEND_PORT}"
    else
        log_info "后端服务: ${RED}已停止${NC}"
    fi

    # 前端状态
    if [ -n "$frontend_pid" ]; then
        if is_windows; then
            log_info "前端服务: ${GREEN}运行中${NC} (PID: $frontend_pid)"
        else
            local frontend_mem
            frontend_mem=$(ps -o rss= -p "$frontend_pid" 2>/dev/null | awk '{printf "%.1f MB", $1/1024}')
            local frontend_uptime
            frontend_uptime=$(ps -o etime= -p "$frontend_pid" 2>/dev/null)
            log_info "前端服务: ${GREEN}运行中${NC} (PID: $frontend_pid, 内存: ${frontend_mem:-N/A}, 运行时间: ${frontend_uptime:-N/A})"
        fi
        log_info "  访问地址: http://localhost:${FRONTEND_PORT}"
    else
        log_info "前端服务: ${RED}已停止${NC}"
    fi
}

# 查看日志
show_logs() {
    local log_file="$1"
    local service_name="$2"

    if [ ! -f "$log_file" ]; then
        log_warn "$service_name 日志文件不存在: $log_file"
        return 1
    fi

    log_info "正在查看 $service_name 日志 (文件: $log_file)"
    log_info "按 Ctrl+C 退出日志查看"
    echo ""

    # 使用 tail -f 实时查看日志
    # 在 Windows 下如果 tail 不可用，使用 cat 代替
    if command -v tail &> /dev/null; then
        tail -f "$log_file"
    else
        cat "$log_file"
    fi
}

#=============================================================================
# 入口：参数解析
#=============================================================================

main() {
    local cmd="${1:-help}"
    local subcmd=""
    shift 2>/dev/null || true

    # 解析 --public 和 --host=<IP> 公共参数
    # 这些参数可以出现在任何位置，如: ./run.sh start --public
    PUBLIC_IP=""
    local remaining_args=()
    for arg in "$@"; do
        case "$arg" in
            --public)
                # 自动检测服务器 IP
                local ip
                ip=$(detect_ip) || true
                if [ -z "$ip" ]; then
                    log_error "无法自动检测服务器 IP，请使用 --host=<IP> 手动指定"
                    exit 1
                fi
                PUBLIC_IP="$ip"
                log_info "检测到服务器 IP: $PUBLIC_IP"
                ;;
            --host=*)
                # 手动指定服务器 IP
                PUBLIC_IP="${arg#--host=}"
                log_info "使用指定的服务器 IP: $PUBLIC_IP"
                ;;
            *)
                remaining_args+=("$arg")
                ;;
        esac
    done

    # 剩余的第一个参数作为 subcmd（如 build 的 release 参数）
    subcmd="${remaining_args[0]:-}"

    case "$cmd" in
        # 编译相关
        build)
            build_all "$subcmd"
            ;;
        build-backend)
            build_backend "$subcmd"
            ;;
        build-frontend)
            build_frontend
            ;;

        # 启动相关
        start)
            start_all
            ;;
        start-backend)
            start_backend
            ;;
        start-frontend)
            start_frontend
            ;;

        # 停止相关
        stop)
            stop_all
            ;;
        stop-backend)
            stop_backend
            ;;
        stop-frontend)
            stop_frontend
            ;;

        # 重启相关
        restart)
            stop_all
            echo ""
            start_all
            ;;
        restart-backend)
            stop_backend
            echo ""
            start_backend
            ;;
        restart-frontend)
            stop_frontend
            echo ""
            start_frontend
            ;;

        # 状态查看
        status)
            show_status
            ;;

        # 日志查看
        logs)
            log_info "同时查看所有日志请分别执行:"
            log_info "  $0 logs-backend"
            log_info "  $0 logs-frontend"
            ;;
        logs-backend)
            show_logs "$BACKEND_LOG" "后端"
            ;;
        logs-frontend)
            show_logs "$FRONTEND_LOG" "前端"
            ;;

        # 帮助
        help|--help|-h)
            echo "=============================================================================="
            echo "  云手机测试平台 - 编译 / 运行 / 停止 管理脚本"
            echo "  支持 Linux 和 Windows (Git Bash / MSYS2 / Cygwin)"
            echo "=============================================================================="
            echo ""
            echo "用法: $0 <命令> [选项]"
            echo ""
            echo "编译命令:"
            echo "  build [release]         编译后端和前端（加 release 参数优化体积）"
            echo "  build-backend [release] 仅编译后端"
            echo "  build-frontend          仅安装前端依赖"
            echo ""
            echo "启动命令（可附加 --public 或 --host=<IP>）:"
            echo "  start [选项]             启动所有服务"
            echo "  start-backend [选项]     仅启动后端"
            echo "  start-frontend [选项]    仅启动前端"
            echo ""
            echo "  选项说明:"
            echo "    --public             自动检测本机 IP，前端 API 地址切换为服务器 IP"
            echo "    --host=<IP>          手动指定服务器 IP（如 --host=192.168.1.100）"
            echo "                          其他设备可通过 http://<IP>:5173 访问前端"
            echo ""
            echo "停止命令:"
            echo "  stop                  停止所有服务"
            echo "  stop-backend          仅停止后端"
            echo "  stop-frontend         仅停止前端"
            echo ""
            echo "重启命令:"
            echo "  restart [选项]          重启所有服务（支持 --public / --host=）"
            echo "  restart-backend        重启后端"
            echo "  restart-frontend       重启前端"
            echo ""
            echo "其他命令:"
            echo "  status                查看服务运行状态"
            echo "  logs                  查看日志提示"
            echo "  logs-backend          查看后端实时日志"
            echo "  logs-frontend         查看前端实时日志"
            echo "  help                  显示本帮助信息"
            echo ""
            echo "访问地址:"
            echo "  前端: http://localhost:${FRONTEND_PORT}"
            echo "  后端: http://localhost:${BACKEND_PORT}"
            echo "  默认账号: admin / admin123"
            echo ""
            echo "示例:"
            echo "  # 本地运行（默认）"
            echo "  ./run.sh start"
            echo ""
            echo "  # 服务器运行，自动检测 IP"
            echo "  ./run.sh start --public"
            echo ""
            echo "  # 服务器运行，手动指定 IP"
            echo "  ./run.sh start --host=192.168.1.100"
            echo ""
            ;;

        *)
            log_error "未知命令: $cmd"
            echo "可用命令: build | start | stop | restart | status | logs | help"
            echo "查看详细帮助: $0 help"
            exit 1
            ;;
    esac
}

#=============================================================================
# 执行入口
#=============================================================================
main "$@"
