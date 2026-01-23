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
    redirect: '/requirements',
    name: 'Root',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'requirements',
        name: 'Requirements',
        component: () => import('@/views/RequirementView.vue'),
        meta: { title: '需求管理', icon: 'Document' }
      },
      {
        path: 'testcases',
        name: 'TestCases',
        component: () => import('@/views/TestCaseView.vue'),
        meta: { title: '测试用例', icon: 'List' }
      },
      {
        path: 'generate',
        name: 'Generate',
        component: () => import('@/views/GenerateView.vue'),
        meta: { title: '生成用例', icon: 'MagicStick' }
      },
      {
        path: 'prompts',
        name: 'Prompts',
        component: () => import('@/views/PromptView.vue'),
        meta: { title: '提示词管理', icon: 'ChatDotRound' }
      },
      {
        path: 'knowledges',
        name: 'Knowledges',
        component: () => import('@/views/KnowledgeView.vue'),
        meta: { title: '知识库管理', icon: 'Collection' }
      },
      {
        path: 'llm-configs',
        name: 'LLMConfigs',
        component: () => import('@/views/LLMConfigView.vue'),
        meta: { title: '大模型配置', icon: 'Setting' }
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
      
      if (!permissionStore.routesAdded) {
        // 检查是否有菜单数据
        if (permissionStore.menus.length === 0) {
          // 使用默认路由
          defaultAsyncRoutes.forEach(route => {
            if (!router.hasRoute(route.name)) {
              router.addRoute(route)
            }
          })
          permissionStore.routesAdded = true
        } else {
          // 使用动态路由
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
