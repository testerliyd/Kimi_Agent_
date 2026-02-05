# SmartTest 智能测试平台 - 部署指南

## 📋 项目概述

SmartTest 是一个智能化测试平台，整合了：
- 甘特图项目管理（参考禅道）
- AI 大模型辅助测试用例生成和执行
- 完整的测试生命周期管理
- 自动化测试和性能测试

## 🚀 快速部署

### 一键部署脚本

```bash
# 给脚本添加执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

### 手动部署步骤

#### 1. 后端部署

```bash
# 进入后端目录
cd smarttest_platform

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行部署校验
python scripts/verify_deployment.py

# 执行数据库迁移
python manage.py migrate

# 初始化数据库
python scripts/init_database.py

# 启动服务
python manage.py runserver 0.0.0.0:8000
```

#### 2. 前端部署

```bash
# 进入前端目录
cd app

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

## 🔧 功能清单

### ✅ 已完成的功能

#### 1. 甘特图功能
- **文件**: `app/src/components/GanttChart.tsx`
- **功能**:
  - 日/周/月三种视图模式
  - 任务进度可视化
  - 状态颜色区分（待开始/进行中/已完成/已延期）
  - 今天标记线
  - 任务详情展示

#### 2. AI 大模型配置开关
- **文件**: `app/src/components/LLMConfigSwitch.tsx`
- **功能**:
  - 启用/禁用 AI 辅助
  - 多提供商支持（OpenAI/Anthropic/Azure/Ollama）
  - 模型选择
  - 温度参数调节
  - Token 数量限制
  - RAG 知识库增强开关

#### 3. 测试用例管理增强
- **文件**: `app/src/pages/TestCaseManagement.tsx`
- **新增功能**:
  - AI 生成测试用例弹窗
  - 甘特图视图
  - 大模型配置集成
  - 支持从需求文档/原型生成用例

#### 4. 数据库初始化脚本
- **文件**: `smarttest_platform/scripts/init_database.py`
- **功能**:
  - 数据库连接检查
  - 表结构校验
  - 超级用户创建
  - 角色/权限初始化
  - 示例项目创建
  - 大模型提供商初始化
  - 系统配置初始化
  - 数据完整性验证

#### 5. 部署校验脚本
- **文件**: `smarttest_platform/scripts/verify_deployment.py`
- **功能**:
  - Python 版本检查
  - 依赖包检查
  - 数据库文件检查
  - 数据库表检查
  - 超级用户检查
  - Django 配置检查
  - 静态文件检查
  - 前端构建检查
  - 端口可用性检查
  - Django 系统检查

## 🔌 接口对照表

### 核心接口

| 模块 | 前端路径 | 后端路由 | 状态 |
|------|---------|---------|------|
| 用户认证 | /users/auth/login/ | /api/users/auth/login/ | ✅ |
| 用户管理 | /users/ | /api/users/ | ✅ |
| 角色管理 | /users/roles/ | /api/users/roles/ | ✅ |
| 权限管理 | /users/permissions/ | /api/users/permissions/ | ✅ |
| 项目管理 | /projects/ | /api/projects/ | ✅ |
| 测试用例 | /testcases/cases/ | /api/testcases/cases/ | ✅ |
| 测试套件 | /testcases/suites/ | /api/testcases/suites/ | ✅ |
| 测试计划 | /testcases/plans/ | /api/testcases/plans/ | ✅ |
| Bug管理 | /bugs/ | /api/bugs/ | ✅ |
| 接口测试 | /apitest/definitions/ | /api/apitest/definitions/ | ✅ |
| 性能测试 | /perftest/scenarios/ | /api/perftest/scenarios/ | ✅ |
| 大模型配置 | /llm/configs/ | /api/llm/configs/ | ✅ |
| 飞书配置 | /feishu/configs/ | /api/feishu/configs/ | ✅ |
| 系统配置 | /core/system-configs/ | /api/core/system-configs/ | ✅ |
| 仪表盘 | /core/dashboard/ | /api/core/dashboard/ | ✅ |
| 通知 | /core/notifications/ | /api/core/notifications/ | ✅ |

## 🗄️ 数据库表结构

### 核心表

```
users_user              - 用户表
users_role              - 角色表
users_permission        - 权限表
projects_project        - 项目表
testcases_testcase      - 测试用例表
testcases_testsuite     - 测试套件表
testcases_testplan      - 测试计划表
testcases_testcasetag   - 用例标签表
testcases_testcasecategory - 用例分类表
bugs_bug                - Bug表
bugs_bugtag             - Bug标签表
bugs_bugcategory        - Bug分类表
llm_llmconfig           - 大模型配置表
llm_llmprovider         - 大模型提供商表
feishu_feishuconfig     - 飞书配置表
core_systemconfig       - 系统配置表
core_notification       - 通知表
```

## 🎨 UI 颜色配置

### 主题色
- **主色**: 青色 (#22d3ee)
- **次要色**: 蓝色 (#3b82f6)
- **强调色**: 紫色 (#a855f7)
- **成功色**: 绿色 (#22c55e)
- **警告色**: 橙色 (#f59e0b)
- **危险色**: 红色 (#ef4444)

### 区域颜色区分
- `.section-primary` - 青色主题区域
- `.section-secondary` - 紫色主题区域
- `.section-success` - 绿色主题区域
- `.section-warning` - 橙色主题区域
- `.section-danger` - 红色主题区域

## 📝 默认账号

```
用户名: admin
密码: admin123
邮箱: admin@smarttest.com
```

## 🔗 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:5173 | 开发环境 |
| 后端API | http://localhost:8000/api/ | RESTful API |
| API文档 | http://localhost:8000/swagger/ | Swagger UI |
| 管理后台 | http://localhost:8000/admin/ | Django Admin |

## 🧪 测试验证

### 运行测试

```bash
# 后端测试
cd smarttest_platform
python manage.py test

# 部署校验
python scripts/verify_deployment.py

# 数据库初始化
python scripts/init_database.py
```

### 接口测试

```bash
# 测试登录接口
curl -X POST http://localhost:8000/api/users/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 🐛 常见问题

### 1. 数据库迁移失败

```bash
# 删除数据库重新迁移
rm db.sqlite3
python manage.py migrate
python scripts/init_database.py
```

### 2. 前端接口404

检查后端服务是否启动，并确认 `VITE_API_BASE_URL` 配置正确。

### 3. 权限不足

确保已创建超级用户并正确登录。

## 📚 相关文档

- [API_INTERFACE_MAPPING.md](API_INTERFACE_MAPPING.md) - 完整接口对照表
- [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) - 测试报告
- [TEST_CASES.md](TEST_CASES.md) - 测试用例文档

## 📞 技术支持

如有问题，请联系：support@smarttest.com
