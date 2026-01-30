#!/bin/bash
# SmartTest 智能化测试平台启动脚本

set -e

echo "======================================"
echo "  SmartTest 智能化测试平台启动脚本"
echo "======================================"
echo ""

# 检查Python环境
echo "[1/6] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3.11或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 检查虚拟环境
echo ""
echo "[2/6] 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo ""
echo "[3/6] 安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 检查环境变量文件
echo ""
echo "[4/6] 检查环境变量..."
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，使用.env.example作为模板"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "请编辑.env文件配置您的环境变量"
    fi
fi

# 数据库迁移
echo ""
echo "[5/6] 执行数据库迁移..."
python manage.py migrate

# 创建超级用户（如果不存在）
echo ""
echo "[6/6] 检查超级用户..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0) if User.objects.filter(is_superuser=True).exists() else print('需要创建超级用户')" | python manage.py shell 2>/dev/null || {
    echo "创建超级用户..."
    python manage.py createsuperuser
}

echo ""
echo "======================================"
echo "  启动服务..."
echo "======================================"
echo ""
echo "Django服务: http://127.0.0.1:8000"
echo "管理后台: http://127.0.0.1:8000/admin"
echo "API文档: http://127.0.0.1:8000/swagger/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动Django服务
python manage.py runserver 0.0.0.0:8000
