# SmartTest 前端项目

基于 React + TypeScript + Vite + Tailwind CSS + shadcn/ui 构建的智能化测试平台前端。

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite 6
- **样式**: Tailwind CSS 4
- **UI组件**: shadcn/ui
- **路由**: React Router 7
- **图标**: Lucide React
- **HTTP客户端**: Fetch API

## 功能特性

### 已实现页面

1. **登录页** - JWT认证登录
2. **仪表盘** - 系统概览、统计数据、最近活动
3. **用户管理** - 用户CRUD、角色分配
4. **角色管理** - 角色权限配置
5. **大模型配置** - 支持OpenAI、Claude、Kimi、DeepSeek等
6. **数据库配置** - 数据库连接管理、初始化
7. **Redis配置** - Redis连接管理
8. **系统配置** - 系统参数设置

### UI设计特点

- 深色科技主题
- 霓虹发光效果
- 玻璃态卡片设计
- 流畅动画过渡
- 响应式布局

## 快速开始

### 环境要求
- Node.js 18+
- npm 9+

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
# 或
bash start_dev.sh
```

访问 http://localhost:5173

### 构建生产版本
```bash
npm run build
```

构建产物位于 `dist/` 目录。

### 代码检查
```bash
npm run lint
```

## 项目结构

```
src/
├── components/          # 组件
│   └── layout/         # 布局组件
│       ├── Header.tsx  # 顶部导航
│       ├── Layout.tsx  # 主布局
│       └── Sidebar.tsx # 侧边栏
├── contexts/           # React Context
│   └── AuthContext.tsx # 认证上下文
├── lib/                # 工具函数
│   └── utils.ts        # 通用工具
├── pages/              # 页面
│   ├── Login.tsx       # 登录页
│   ├── Dashboard.tsx   # 仪表盘
│   ├── UserManagement.tsx    # 用户管理
│   ├── RoleManagement.tsx    # 角色管理
│   ├── LLMConfig.tsx         # 大模型配置
│   ├── DatabaseConfig.tsx    # 数据库配置
│   ├── RedisConfig.tsx       # Redis配置
│   └── SystemConfig.tsx      # 系统配置
├── services/           # API服务
│   └── api.ts          # API封装
├── types/              # TypeScript类型
│   └── index.ts        # 类型定义
├── App.tsx             # 主应用组件
└── main.tsx            # 入口文件
```

## API配置

前端通过环境变量配置后端API地址：

```bash
# .env 文件
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 后端联调

1. 启动Django后端（端口8000）
2. 启动前端开发服务器（端口5173）
3. CORS已配置，前端可直接访问后端API

## 默认账号

- 用户名: admin
- 密码: admin123

## 注意事项

1. 确保后端服务已启动且CORS配置正确
2. 首次使用需要创建超级用户
3. 前端开发服务器代理已配置，API请求会自动转发到后端
