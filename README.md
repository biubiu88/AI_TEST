# AI 测试用例生成器

一个基于 AI 的测试用例自动生成系统，支持根据需求文档智能生成高质量测试用例。

## 技术架构

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue.js | 3.5.x | 渐进式 JavaScript 框架 |
| Vue Router | 4.6.x | 官方路由管理器，支持动态路由 |
| Pinia | 3.0.x | 新一代状态管理库 |
| Element Plus | 2.13.x | Vue 3 UI 组件库 |
| Axios | 1.13.x | HTTP 请求库 |
| Vite | 7.3.x | 下一代前端构建工具 |
| Sass | 1.97.x | CSS 预处理器 |

#### 前端特性
- **动态路由**: 支持基于用户权限的动态路由加载
- **权限控制**: 
  - `v-permission` 指令：按权限控制按钮显示
  - `v-role` 指令：按角色控制元素显示
  - `hasPermission()` / `hasRole()` 函数：逻辑判断
- **状态管理**: 使用 Pinia 管理用户、权限、菜单等状态
- **主题配置**: 支持自定义主题配色

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| Flask | 3.0.x | 轻量级 Web 框架 |
| Flask-SQLAlchemy | 3.1.x | ORM 数据库操作 |
| Flask-JWT-Extended | 4.6.x | JWT 认证 |
| Flask-CORS | 4.0.x | 跨域支持 |
| MySQL | 8.0+ | 关系型数据库 |
| OpenAI SDK | 1.10+ | AI 模型调用 |

#### 后端特性
- **RBAC 权限模型**: 基于角色的访问控制
- **JWT 认证**: 无状态 Token 认证
- **RESTful API**: 标准化接口设计
- **多 LLM 支持**: 支持 OpenAI、通义千问、智谱、Moonshot、DeepSeek 等

## 项目结构

```
ai_test/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── routes/         # API 路由
│   │   │   ├── auth.py     # 认证接口
│   │   │   ├── permission.py # 权限管理接口
│   │   │   ├── requirement.py
│   │   │   ├── testcase.py
│   │   │   ├── prompt.py
│   │   │   ├── knowledge.py
│   │   │   └── llm_config.py
│   │   ├── services/       # 业务服务
│   │   ├── models.py       # 数据模型
│   │   └── __init__.py     # 应用工厂
│   ├── .env                # 环境配置
│   ├── config.py           # 应用配置
│   ├── init_db.sql         # 数据库初始化
│   ├── requirements.txt    # Python 依赖
│   └── run.py              # 启动入口
│
└── vue_web/                # 前端项目
    ├── src/
    │   ├── api/            # API 接口
    │   ├── components/     # 公共组件
    │   ├── layout/         # 布局组件
    │   ├── router/         # 路由配置
    │   ├── stores/         # 状态管理
    │   │   ├── permission.js # 权限状态
    │   │   └── user.js     # 用户状态
    │   ├── utils/          # 工具函数
    │   │   └── permission.js # 权限指令
    │   └── views/          # 页面视图
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 环境要求

- Node.js >= 20.19.0 或 >= 22.12.0
- Python >= 3.11
- MySQL >= 8.0

### 后端启动

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows 激活
venv\Scripts\activate

# Linux/Mac 激活
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
# 复制 .env.example 为 .env 并修改配置
cp .env.example .env

# 5. 初始化数据库
# 在 MySQL 中执行 init_db.sql
mysql -u root -p < init_db.sql

# 6. 启动服务
python run.py
```

后端默认运行在 http://localhost:5000

### 前端启动

```bash
# 1. 进入前端目录
cd vue_web

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev

# 4. 构建生产版本
npm run build
```

前端默认运行在 http://localhost:5173

### Windows 快捷启动

```batch
# 后端启动
cd backend
run.bat

# 前端启动
cd vue_web
run.bat
```

## 权限系统说明

### 权限模型

系统采用 RBAC（基于角色的访问控制）模型：

- **用户 (User)**: 系统使用者
- **角色 (Role)**: 权限集合，如管理员、普通用户
- **权限 (Permission)**: 具体操作权限，如 `testcase:create`
- **菜单 (Menu)**: 前端路由菜单

### 默认角色

| 角色 | 编码 | 说明 |
|------|------|------|
| 超级管理员 | admin | 拥有所有权限 |
| 普通用户 | user | 基本功能权限 |

### 权限使用示例

```vue
<!-- 按钮权限控制 -->
<el-button v-permission="'testcase:create'">新增用例</el-button>

<!-- 多权限（任一满足） -->
<el-button v-permission="['testcase:edit', 'testcase:delete']">操作</el-button>

<!-- 角色控制 -->
<el-button v-role="'admin'">管理员功能</el-button>

<!-- 脚本中判断 -->
<script setup>
import { hasPermission, hasRole } from '@/utils/permission'

const canEdit = hasPermission('testcase:edit')
const isAdmin = hasRole('admin')
</script>
```

## API 接口

### 基础信息

- 基础路径: `http://localhost:5000/api`
- 认证方式: Bearer Token
- 响应格式: JSON

### 主要接口

| 模块 | 路径前缀 | 说明 |
|------|----------|------|
| 认证 | /api/auth | 登录、注册、Token刷新 |
| 权限 | /api/permission | 角色、权限、菜单管理 |
| 需求 | /api/requirements | 需求文档 CRUD |
| 用例 | /api/testcases | 测试用例 CRUD |
| AI | /api/ai | AI 生成用例 |
| 提示词 | /api/prompts | 提示词管理 |
| 知识库 | /api/knowledges | 知识库管理 |
| 模型配置 | /api/llm-configs | 大模型配置 |

## 环境配置

### 后端环境变量 (.env)

```env
# Flask 配置
FLASK_ENV=development
SECRET_KEY=your-secret-key

# 数据库配置
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/testcase_generator

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret
```

### 前端配置 (vite.config.js)

API 代理配置已内置，开发环境自动代理到后端服务。

## 许可证

MIT License
