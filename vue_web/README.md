# TestCase AI 前端

AI驱动的测试用例生成平台前端项目。

## 技术栈

- **框架**: Vue 3 (Composition API + setup语法糖)
- **构建工具**: Vite
- **UI组件库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP客户端**: Axios
- **样式**: SCSS

## 功能模块

### 用户认证
- 用户登录（支持用户名/邮箱登录）
- 用户注册
- 重置密码
- 修改密码
- JWT Token认证

### 业务功能
- **需求管理**: 需求的增删改查、模块分类、状态管理
- **测试用例**: 用例的增删改查、关联需求、状态跟踪
- **生成用例**: AI智能生成测试用例

### 系统功能
- 左侧菜单导航
- 顶部导航栏
- 面包屑导航
- 主题设置（主题色、深色模式、布局配置）
- 全屏显示
- 水印设置

## 项目结构

```
src/
├── api/                # API接口
│   └── index.js        # Axios配置和API方法
├── components/         # 公共组件
│   └── ThemeSettings/  # 主题设置组件
├── layout/             # 布局组件
│   ├── Header/         # 顶部导航
│   ├── Logo/           # Logo组件
│   ├── Menu/           # 侧边菜单
│   └── index.vue       # 主布局
├── router/             # 路由配置
│   └── index.js        # 路由和导航守卫
├── stores/             # Pinia状态管理
│   ├── app.js          # 应用状态
│   ├── themeConfig.js  # 主题配置
│   ├── user.js         # 用户状态
│   ├── requirement.js  # 需求状态
│   └── testcase.js     # 用例状态
├── utils/              # 工具函数
│   ├── theme.js        # 主题工具
│   └── watermark.js    # 水印工具
├── views/              # 页面视图
│   ├── LoginView.vue         # 登录页
│   ├── RegisterView.vue      # 注册页
│   ├── ResetPasswordView.vue # 重置密码页
│   ├── RequirementView.vue   # 需求管理
│   ├── TestCaseView.vue      # 测试用例
│   └── GenerateView.vue      # 生成用例
├── App.vue             # 根组件
└── main.js             # 入口文件
```

## 快速开始

### 环境要求

- Node.js >= 20.19.0 或 >= 22.12.0
- npm >= 10.0.0

### 安装依赖

```bash
npm install
```

### 开发运行

```bash
npm run dev
```

默认访问地址: http://localhost:5173
用户名: testuser
邮箱: test@example.com
密码: 123456

### 生产构建

```bash
npm run build
```

## 后端配置

默认后端API地址为 `http://localhost:5000/api`，如需修改请编辑 `src/api/index.js` 文件。

## 开发说明

### IDE推荐

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

### 浏览器插件

- Chrome/Edge: [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
- Firefox: [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)

## 更多配置

查看 [Vite配置文档](https://vite.dev/config/)
