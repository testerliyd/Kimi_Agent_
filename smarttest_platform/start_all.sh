#!/bin/bash
# SmartTest 智能化测试平台完整启动脚本
# 同时启动Django后端和React前端

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}  SmartTest 智能化测试平台启动脚本${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python环境
echo -e "${YELLOW}[1/7] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误: 未找到Python3，请先安装Python3.11或更高版本${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}Python版本: $PYTHON_VERSION${NC}"

# 检查Node.js环境
echo ""
echo -e "${YELLOW}[2/7] 检查Node.js环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到Node.js，请先安装Node.js 18或更高版本${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}Node.js版本: $NODE_VERSION${NC}"

# 检查虚拟环境
echo ""
echo -e "${YELLOW}[3/7] 检查虚拟环境...${NC}"
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装后端依赖
echo ""
echo -e "${YELLOW}[4/7] 安装后端依赖...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}后端依赖安装完成${NC}"

# 检查环境变量文件
echo ""
echo -e "${YELLOW}[5/7] 检查环境变量...${NC}"
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，使用.env.example作为模板"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "请编辑.env文件配置您的环境变量"
    fi
fi

# 数据库迁移
echo ""
echo -e "${YELLOW}[6/7] 执行数据库迁移...${NC}"
python manage.py migrate
echo -e "${GREEN}数据库迁移完成${NC}"

# 创建超级用户（如果不存在）
echo ""
echo -e "${YELLOW}[7/7] 检查超级用户...${NC}"
echo "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0) if User.objects.filter(is_superuser=True).exists() else print('需要创建超级用户')" | python manage.py shell 2>/dev/null || {
    echo -e "${YELLOW}创建超级用户...${NC}"
    python manage.py createsuperuser
}

echo ""
echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}  启动服务...${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 收集静态文件
echo "收集静态文件..."
python manage.py collectstatic --noinput 2>/dev/null || true

# 启动Django服务（后台）
echo -e "${GREEN}启动Django后端服务...${NC}"
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!
echo -e "${GREEN}Django服务PID: $DJANGO_PID${NC}"

# 等待Django启动
sleep 3

# 检查Django是否成功启动
if ! kill -0 $DJANGO_PID 2>/dev/null; then
    echo -e "${RED}Django服务启动失败${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SmartTest 平台启动成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}访问地址:${NC}"
echo -e "  ${GREEN}前端界面: http://127.0.0.1:8000${NC}"
echo -e "  ${GREEN}管理后台: http://127.0.0.1:8000/admin${NC}"
echo -e "  ${GREEN}API文档:  http://127.0.0.1:8000/swagger/${NC}"
echo ""
echo -e "${YELLOW}默认账号:${NC}"
echo -e "  用户名: admin"
echo -e "  密码: admin123"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 捕获Ctrl+C信号
trap 'echo -e "\n${RED}正在停止服务...${NC}"; kill $DJANGO_PID 2>/dev/null; exit 0' INT

# 等待Django进程
wait $DJANGO_PID
