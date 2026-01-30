# SmartTest 智能化测试平台

## 项目概述

SmartTest是一个基于Django开发的智能化测试平台，集成了测试管理、项目管理、接口自动化测试、性能测试、大模型API配置管理和飞书机器人通知等功能。

## 功能特性

### 核心功能
- **用户管理**: 支持多角色权限控制（管理员、项目经理、测试工程师、开发工程师、访客）
- **项目管理**: 项目创建、成员管理、版本管理、里程碑管理、环境配置
- **用例管理**: 测试用例的CRUD操作、测试套件、测试计划
- **Bug管理**: 缺陷跟踪、状态流转、评论和历史记录
- **接口自动化测试**: API定义、测试用例、测试任务、测试报告
- **性能测试**: 测试场景、测试任务、性能指标监控
- **大模型配置**: 支持OpenAI、Claude、Kimi、DeepSeek等主流大模型
- **飞书集成**: 机器人通知、测试报告推送、群聊绑定

### 技术栈
- **后端**: Django 4.2 + Django REST Framework
- **前端**: React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui
- **数据库**: SQLite(开发) / MySQL 8.0(生产) + Redis
- **异步任务**: Celery + Redis
- **认证**: JWT Token认证
- **文档**: Swagger/OpenAPI

## 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- MySQL 8.0+ (可选，默认使用SQLite)
- Redis 7.0+ (可选，默认使用内存缓存)

### 方式1: 一键启动（推荐）

```bash
cd smarttest_platform
bash start_all.sh
```

访问 http://127.0.0.1:8000 即可使用完整功能。

### 方式2: 分别启动前后端（开发模式）

#### 启动后端
```bash
cd smarttest_platform
bash start.sh
```

#### 启动前端（新终端）
```bash
cd app
bash start_dev.sh
```

访问 http://localhost:5173 使用前端开发服务器。

### 详细安装步骤

#### 1. 克隆项目
```bash
git clone <repository-url>
cd smarttest_platform
```

#### 2. 创建虚拟环境
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

#### 3. 安装后端依赖
```bash
pip install -r requirements.txt
```

#### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，配置数据库、Redis、飞书等参数
```

#### 5. 初始化数据库
```bash
python manage.py migrate
python init_db.py
```

#### 6. 创建超级用户
```bash
python manage.py createsuperuser
```

#### 7. 启动后端服务
```bash
# 方式1: 使用启动脚本
bash start.sh

# 方式2: 手动启动
python manage.py runserver 0.0.0.0:8000

# 启动Celery Worker（新终端）
celery -A smarttest worker -l info

# 启动Celery Beat（新终端，可选）
celery -A smarttest beat -l info
```

#### 8. 启动前端（可选）
```bash
cd app
npm install
npm run dev
```

### Docker部署

```bash
# 使用Docker Compose一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 使用说明

### 飞书机器人配置

平台支持两种方式配置飞书机器人：

#### 方式1: Webhook方式（推荐，简单快捷）
1. 在飞书群聊中添加自定义机器人
2. 获取Webhook地址和签名校验密钥
3. 在平台中创建飞书配置：
   - 配置名称: 任意名称
   - Webhook URL: 填入Webhook地址
   - Encrypt Key: 填入签名校验密钥（如果开启了签名校验）

#### 方式2: 飞书应用方式（功能更完整）
1. 在[飞书开放平台](https://open.feishu.cn/)创建应用
2. 获取App ID和App Secret
3. 在平台中创建飞书配置：
   - 配置名称: 任意名称
   - App ID: 填入App ID
   - App Secret: 填入App Secret

### API文档
启动服务后访问:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

### 管理后台
- 地址: http://localhost:8000/admin/
- 使用创建的超级用户登录

### 主要API端点

#### 用户管理
- `POST /api/auth/token/` - 获取JWT Token
- `GET /api/users/users/` - 用户列表
- `GET /api/users/users/me/` - 当前用户信息

#### 项目管理
- `GET /api/projects/` - 项目列表
- `POST /api/projects/` - 创建项目
- `GET /api/projects/{id}/` - 项目详情

#### 用例管理
- `GET /api/testcases/cases/` - 测试用例列表
- `POST /api/testcases/cases/` - 创建测试用例
- `POST /api/testcases/cases/{id}/execute/` - 执行测试用例

#### Bug管理
- `GET /api/bugs/` - Bug列表
- `POST /api/bugs/` - 创建Bug
- `POST /api/bugs/{id}/assign/` - 分配Bug
- `POST /api/bugs/{id}/resolve/` - 解决Bug

#### 接口测试
- `GET /api/apitest/definitions/` - API定义列表
- `GET /api/apitest/cases/` - API测试用例
- `POST /api/apitest/jobs/{id}/execute/` - 执行API测试

#### 性能测试
- `GET /api/perftest/scenarios/` - 测试场景
- `POST /api/perftest/jobs/{id}/execute/` - 执行性能测试

#### 大模型配置
- `GET /api/llm/providers/` - 大模型提供商
- `GET /api/llm/configs/` - 配置列表
- `POST /api/llm/conversations/{id}/chat/` - 对话

#### 飞书集成
- `GET /api/feishu/configs/` - 飞书配置
- `POST /api/feishu/webhook/send_message/` - 发送消息

## 配置文件说明

### 环境变量 (.env)

```bash
# Django配置
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=smarttest
DB_USER=root
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_URL=redis://localhost:6379/1

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0

# 飞书配置
FEISHU_APP_ID=your-app-id
FEISHU_APP_SECRET=your-app-secret

# 大模型API配置
OPENAI_API_KEY=your-openai-key
MOONSHOT_API_KEY=your-moonshot-key
DEEPSEEK_API_KEY=your-deepseek-key
# ... 其他大模型配置
```

## 目录结构

```
smarttest_platform/            # 后端项目
├── apps/                      # 应用目录
│   ├── users/                # 用户管理
│   ├── projects/             # 项目管理
│   ├── testcases/            # 用例管理
│   ├── bugs/                 # Bug管理
│   ├── apitest/              # 接口测试
│   ├── perftest/             # 性能测试
│   ├── llm/                  # 大模型配置
│   ├── feishu/               # 飞书集成
│   ├── reports/              # 报告管理
│   └── core/                 # 核心模块
├── smarttest/                # 项目配置
│   ├── settings.py          # 设置
│   ├── urls.py              # URL路由
│   ├── wsgi.py              # WSGI配置
│   ├── asgi.py              # ASGI配置
│   └── celery.py            # Celery配置
├── frontend/                 # 前端构建产物
├── manage.py                 # Django管理脚本
├── requirements.txt          # 依赖
├── docker-compose.yml        # Docker配置
├── Dockerfile                # Docker镜像
├── start.sh                  # 后端启动脚本
├── start_all.sh              # 完整启动脚本
└── init_db.py                # 数据库初始化

app/                          # 前端项目
├── src/
│   ├── components/          # 组件
│   │   └── layout/         # 布局组件
│   ├── pages/              # 页面
│   ├── services/           # API服务
│   ├── contexts/           # React Context
│   ├── types/              # TypeScript类型
│   └── lib/                # 工具函数
├── public/                 # 静态资源
├── index.html
├── package.json
├── vite.config.ts
├── tailwind.config.js
└── start_dev.sh            # 前端开发启动脚本
```

## 开发指南

### 添加新应用
```bash
python manage.py startapp myapp
# 在apps目录下创建新应用
```

### 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 创建超级用户
```bash
python manage.py createsuperuser
```

### 运行测试
```bash
python manage.py test
```

## 常见问题

### 1. 数据库连接失败
- 检查MySQL服务是否启动
- 检查.env中的数据库配置
- 确认数据库用户权限

### 2. Redis连接失败
- 检查Redis服务是否启动
- 检查.env中的Redis配置

### 3. Celery任务不执行
- 检查Celery Worker是否启动
- 检查Redis连接
- 查看Celery日志

### 4. 飞书通知失败
- 检查飞书应用配置
- 确认App ID和App Secret正确
- 检查网络连接

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页: https://github.com/your-org/smarttest
- 问题反馈: https://github.com/your-org/smarttest/issues
