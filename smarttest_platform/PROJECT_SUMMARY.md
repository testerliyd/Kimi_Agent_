# SmartTest 智能化测试平台 - 项目总结

## 项目概述

SmartTest是一个基于Django开发的智能化测试平台，集成了测试管理、项目管理、接口自动化测试、性能测试、大模型API配置管理和飞书机器人通知等功能。

## 项目结构

```
smarttest_platform/
├── apps/                       # 应用模块（10个核心应用）
│   ├── users/                 # 用户管理
│   ├── projects/              # 项目管理
│   ├── testcases/             # 用例管理
│   ├── bugs/                  # Bug管理
│   ├── apitest/               # 接口自动化测试
│   ├── perftest/              # 性能测试
│   ├── llm/                   # 大模型配置
│   ├── feishu/                # 飞书集成
│   ├── reports/               # 报告管理
│   └── core/                  # 核心模块
├── smarttest/                 # Django项目配置
├── docs/                      # 文档目录
├── requirements.txt           # Python依赖
├── docker-compose.yml         # Docker配置
├── Dockerfile                 # Docker镜像
├── start.sh                   # 启动脚本
├── init_db.py                 # 数据库初始化
└── manage.py                  # Django管理脚本
```

## 功能模块

### 1. 用户管理模块
- 自定义用户模型
- JWT Token认证
- 角色权限管理（管理员、项目经理、测试工程师、开发工程师、访客）
- 用户导入/导出
- 登录日志

### 2. 项目管理模块
- 项目CRUD
- 项目成员管理
- 版本管理
- 里程碑管理
- 环境配置

### 3. 用例管理模块
- 测试用例CRUD
- 测试用例执行
- 测试套件
- 测试计划
- 用例统计

### 4. Bug管理模块
- Bug CRUD
- 状态流转（新建→确认→处理→解决→关闭）
- Bug分配/解决/关闭
- 评论和历史记录
- 飞书通知

### 5. 接口自动化测试模块
- API定义管理
- API测试用例
- 测试任务（异步执行）
- 测试结果记录
- 测试报告

### 6. 性能测试模块
- 测试场景管理
- 测试任务（异步执行）
- 性能指标采集
- 测试报告

### 7. 大模型配置模块
- 支持10+主流大模型提供商
  - OpenAI (GPT-4/GPT-3.5)
  - Anthropic Claude
  - 月之暗面Kimi
  - DeepSeek
  - 阿里通义千问
  - 百度文心一言
  - 智谱AI
  - Google Gemini
  - MiniMax
  - 零一万物
- AI对话功能
- AI生成测试用例

### 8. 飞书机器人集成模块
- 飞书应用配置
- 消息模板
- Bug通知
- 测试报告推送
- 群聊绑定

### 9. 报告管理模块
- 报告模板
- 报告生成（异步）
- 多格式支持（HTML/PDF/Excel/JSON）
- 在线预览和下载

### 10. 核心模块
- 基础模型（软删除、审计字段）
- 分页组件
- 异常处理
- 中间件（日志、性能监控）
- 审计日志
- 系统配置

## 技术栈

### 后端
- Django 4.2
- Django REST Framework
- Django REST Framework SimpleJWT
- Celery + Redis
- MySQL 8.0

### 第三方库
- requests - HTTP请求
- pandas - 数据处理
- openai - OpenAI API
- anthropic - Claude API
- PyJWT - JWT处理

### 部署
- Docker + Docker Compose
- Gunicorn
- Nginx

## 文档清单

1. **README.md** - 项目概述和快速开始
2. **docs/需求规格说明书.md** - 详细功能需求
3. **docs/使用说明书.md** - 用户操作指南
4. **docs/服务配置和启动说明.md** - 部署和运维指南

## 统计信息

- **Python文件**: 89个
- **总文件数**: 98个
- **代码行数**: 约15000+行
- **应用模块**: 10个
- **API端点**: 200+

## 启动方式

### 方式1: 使用启动脚本
```bash
bash start.sh
```

### 方式2: Docker Compose
```bash
docker-compose up -d
```

### 方式3: 手动启动
```bash
# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 初始化数据
python init_db.py

# 创建超级用户
python manage.py createsuperuser

# 启动服务
python manage.py runserver

# 启动Celery（新终端）
celery -A smarttest worker -l info
```

## 访问地址

- 首页: http://localhost:8000
- 管理后台: http://localhost:8000/admin/
- API文档: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## 主要API端点

### 认证
- `POST /api/auth/token/` - 获取Token
- `POST /api/auth/token/refresh/` - 刷新Token

### 用户
- `GET /api/users/users/` - 用户列表
- `GET /api/users/users/me/` - 当前用户

### 项目
- `GET /api/projects/` - 项目列表
- `POST /api/projects/` - 创建项目

### 用例
- `GET /api/testcases/cases/` - 用例列表
- `POST /api/testcases/cases/` - 创建用例
- `POST /api/testcases/cases/{id}/execute/` - 执行用例

### Bug
- `GET /api/bugs/` - Bug列表
- `POST /api/bugs/` - 创建Bug
- `POST /api/bugs/{id}/assign/` - 分配Bug

### 接口测试
- `GET /api/apitest/definitions/` - API定义
- `POST /api/apitest/jobs/{id}/execute/` - 执行测试

### 性能测试
- `GET /api/perftest/scenarios/` - 测试场景
- `POST /api/perftest/jobs/{id}/execute/` - 执行测试

### 大模型
- `GET /api/llm/providers/` - 提供商列表
- `GET /api/llm/configs/` - 配置列表
- `POST /api/llm/conversations/{id}/chat/` - 对话

### 飞书
- `GET /api/feishu/configs/` - 飞书配置
- `POST /api/feishu/webhook/send_message/` - 发送消息

## 注意事项

1. **环境变量**: 使用前请配置.env文件
2. **数据库**: 确保MySQL和Redis已启动
3. **Celery**: 异步任务需要启动Celery Worker
4. **飞书**: 配置飞书应用后才能使用通知功能
5. **大模型**: 配置API Key后才能使用AI功能

## 后续优化建议

1. 前端React界面开发
2. 测试覆盖率提升
3. 性能优化（数据库索引、缓存）
4. 更多CI/CD集成
5. 移动端适配
6. 更多大模型支持
7. 测试数据Mock功能

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/your-org/smarttest
- 问题反馈: https://github.com/your-org/smarttest/issues
