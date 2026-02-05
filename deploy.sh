#!/bin/bash
# SmartTest 一键部署脚本
# 用于自动化部署后端和前端服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/smarttest_platform"
FRONTEND_DIR="$SCRIPT_DIR/app"

echo "========================================"
echo "  SmartTest 智能测试平台 - 部署脚本"
echo "========================================"
echo ""

# 检查目录是否存在
if [ ! -d "$BACKEND_DIR" ]; then
    print_error "后端目录不存在: $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

# ==================== 后端部署 ====================
echo ""
echo "========================================"
print_info "开始部署后端服务"
echo "========================================"

cd "$BACKEND_DIR"

# 检查 Python 版本
print_info "检查 Python 版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python 版本: $PYTHON_VERSION"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    print_info "创建虚拟环境..."
    python3 -m venv venv
    print_success "虚拟环境创建完成"
fi

# 激活虚拟环境
print_info "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
print_info "安装后端依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
print_success "依赖安装完成"

# 运行部署校验
print_info "运行部署校验..."
python scripts/verify_deployment.py
if [ $? -ne 0 ]; then
    print_warning "部署校验发现问题，尝试修复..."
fi

# 执行数据库迁移
print_info "执行数据库迁移..."
python manage.py migrate --noinput
print_success "数据库迁移完成"

# 初始化数据库
print_info "初始化数据库数据..."
python scripts/init_database.py
if [ $? -ne 0 ]; then
    print_warning "数据库初始化部分失败，但将继续部署"
fi

# 收集静态文件
print_info "收集静态文件..."
python manage.py collectstatic --noinput 2>/dev/null || true

# 创建超级用户（如果不存在）
print_info "检查超级用户..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smarttest.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@smarttest.com', 'admin123')
    print('超级用户创建成功: admin/admin123')
else:
    print('超级用户已存在')
"

print_success "后端部署完成"

# ==================== 前端部署 ====================
echo ""
echo "========================================"
print_info "开始部署前端服务"
echo "========================================"

cd "$FRONTEND_DIR"

# 检查 Node.js 版本
print_info "检查 Node.js 版本..."
NODE_VERSION=$(node --version 2>/dev1 | head -1)
print_success "Node.js 版本: $NODE_VERSION"

# 安装依赖
print_info "安装前端依赖..."
npm install -q
print_success "依赖安装完成"

# 构建前端
print_info "构建前端项目..."
npm run build
print_success "前端构建完成"

echo ""
print_success "========================================"
print_success "  SmartTest 部署完成！"
print_success "========================================"
echo ""
echo "访问地址:"
echo "  前端页面: http://localhost:5173"
echo "  后端API:  http://localhost:8000/api/"
echo "  API文档:  http://localhost:8000/swagger/"
echo "  管理后台: http://localhost:8000/admin/"
echo ""
echo "默认账号:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "启动命令:"
echo "  后端: cd smarttest_platform && source venv/bin/activate && python manage.py runserver"
echo "  前端: cd app && npm run dev"
echo ""

# 询问是否立即启动
read -p "是否立即启动服务? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    print_info "启动后端服务..."
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 在后台启动后端
    python manage.py runserver 0.0.0.0:8000 &
    BACKEND_PID=$!
    print_success "后端服务已启动 (PID: $BACKEND_PID)"
    
    # 启动前端
    print_info "启动前端服务..."
    cd "$FRONTEND_DIR"
    npm run dev &
    FRONTEND_PID=$!
    print_success "前端服务已启动 (PID: $FRONTEND_PID)"
    
    echo ""
    echo "按 Ctrl+C 停止服务"
    wait
fi
