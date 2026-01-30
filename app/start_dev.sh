#!/bin/bash
# SmartTest 前端开发启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${GREEN}  SmartTest 前端开发服务器${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}错误: 未找到Node.js${NC}"
    exit 1
fi

echo -e "${GREEN}Node.js版本: $(node --version)${NC}"
echo ""

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安装依赖...${NC}"
    npm install
fi

echo -e "${GREEN}启动开发服务器...${NC}"
echo -e "${BLUE}前端地址: http://localhost:5173${NC}"
echo -e "${BLUE}后端API: http://localhost:8000/api/v1${NC}"
echo ""

npm run dev
