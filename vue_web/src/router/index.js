import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

// 白名单路由（不需要登录即可访问）
const whiteList = ['/login', '/register', '/reset-password', '/404']

// 静态路由（不需要权限控制）
export const constantRoutes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: () => import('@/views/ResetPasswordView.vue'),
    meta: { title: '重置密码' }
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/404View.vue'),
    meta: { title: '页面不存在' }
  }
]

// 默认动态路由（当后端没有配置菜单时使用）
export const defaultAsyncRoutes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    name: 'Root',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Home',
        component: () => import('@/views/DashboardView.vue'),
        meta: { title: '首页', icon: 'DataBoard' }
      },
      {
        path: 'ai-assistant',
        name: 'AIAssistant',
        component: () => import('@/views/AIAssistantView.vue'),
        meta: { title: 'AI助手', icon: 'ChatLineRound' }
      }
    ]
  },
  {
    path: '/testing',
    component: Layout,
    redirect: '/testing/testcases',
    name: 'Testing',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'testcases',
        name: 'TestCases',
        component: () => import('@/views/TestCaseView.vue'),
        meta: { title: '用例管理', icon: 'List' }
      },
      {
        path: 'generate',
        name: 'Generate',
        component: () => import('@/views/GenerateView.vue'),
        meta: { title: '生成用例', icon: 'MagicStick' }
      },
      {
        path: 'requirements',
        name: 'Requirements',
        component: () => import('@/views/RequirementView.vue'),
        meta: { title: '需求管理', icon: 'Document' }
      }
    ]
  },
  {
    path: '/knowledge',
    component: Layout,
    redirect: '/knowledge/knowledges',
    name: 'Knowledge',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'knowledges',
        name: 'Knowledges',
        component: () => import('@/views/KnowledgeView.vue'),
        meta: { title: '知识库管理', icon: 'Reading' }
      },
      {
        path: 'prompts',
        name: 'Prompts',
        component: () => import('@/views/PromptView.vue'),
        meta: { title: '提示词管理', icon: 'ChatDotRound' }
      }
    ]
  },
  {
    path: '/system',
    component: Layout,
    redirect: '/system/users',
    name: 'System',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UserView.vue'),
        meta: { title: '用户管理', icon: 'User' }
      },
      {
        path: 'roles',
        name: 'Roles',
        component: () => import('@/views/RoleView.vue'),
        meta: { title: '角色管理', icon: 'UserFilled' }
      },
      {
        path: 'menus',
        name: 'Menus',
        component: () => import('@/views/MenuView.vue'),
        meta: { title: '菜单管理', icon: 'Menu' }
      },
      {
        path: 'llm-configs',
        name: 'LLMConfigs',
        component: () => import('@/views/LLMConfigView.vue'),
        meta: { title: '大模型配置', icon: 'Connection' }
      },
      {
        path: 'mcp-configs',
        name: 'MCPConfigs',
        component: () => import('@/views/MCPConfigView.vue'),
        meta: { title: 'MCP配置', icon: 'Connection' }
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('@/views/LogView.vue'),
        meta: { title: '日志与审计', icon: 'DocumentCopy' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes: constantRoutes
})

// 路由导航守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title || '测试用例生成器'} - TestCase Generator`
  
  // 获取token
  const token = localStorage.getItem('accessToken')
  
  // 检查是否在白名单中
  if (whiteList.includes(to.path)) {
    // 已登录用户访问登录页，重定向到首页
    if (token && to.path === '/login') {
      next('/')
    } else {
      next()
    }
  } else {
    // 需要登录的页面
    if (token) {
      // 动态加载路由
      const { usePermissionStore } = await import('@/stores/permission')
      const permissionStore = usePermissionStore()
      
      // 检查是否是页面刷新（from.name为null表示是刷新）
      const isPageRefresh = from.name === null
      
      if (isPageRefresh || !permissionStore.routesAdded) {
        // 页面刷新时，重新获取最新的菜单和权限
        if (isPageRefresh) {
          try {
            await permissionStore.fetchPermissions()
            // 重新添加动态路由
            permissionStore.resetRoutes()
          } catch (error) {
            console.error('刷新权限失败:', error)
          }
        }
        
        // 总是添加默认路由
        defaultAsyncRoutes.forEach(route => {
          if (!router.hasRoute(route.name)) {
            router.addRoute(route)
          }
        })
        permissionStore.routesAdded = true

        // 如果有菜单数据，也添加动态路由
        if (permissionStore.menus.length > 0) {
          await permissionStore.addDynamicRoutes()
        }

        // 重新导航到目标页面
        next({ ...to, replace: true })
        return
      }
      next()
    } else {
      // 未登录，重定向到登录页，并保存目标路径
      next(`/login?redirect=${to.path}`)
    }
  }
})

// 重置路由
export function resetRouter() {
  const { usePermissionStore } = require('@/stores/permission')
  const permissionStore = usePermissionStore()
  permissionStore.resetRoutes()
  
  // 移除默认动态路由
  defaultAsyncRoutes.forEach(route => {
    if (route.name && router.hasRoute(route.name)) {
      router.removeRoute(route.name)
    }
  })
}

export default router
