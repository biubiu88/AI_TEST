import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

// 白名单路由（不需要登录即可访问）
const whiteList = ['/login', '/register', '/reset-password']

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/requirements',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'requirements',
        name: 'Requirements',
        component: () => import('@/views/RequirementView.vue'),
        meta: { title: '需求管理' }
      },
      {
        path: 'testcases',
        name: 'TestCases',
        component: () => import('@/views/TestCaseView.vue'),
        meta: { title: '测试用例' }
      },
      {
        path: 'generate',
        name: 'Generate',
        component: () => import('@/views/GenerateView.vue'),
        meta: { title: '生成用例' }
      },
      {
        path: 'prompts',
        name: 'Prompts',
        component: () => import('@/views/PromptView.vue'),
        meta: { title: '提示词管理' }
      },
      {
        path: 'knowledges',
        name: 'Knowledges',
        component: () => import('@/views/KnowledgeView.vue'),
        meta: { title: '知识库管理' }
      }
    ]
  },
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由导航守卫
router.beforeEach((to, from, next) => {
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
      next()
    } else {
      // 未登录，重定向到登录页，并保存目标路径
      next(`/login?redirect=${to.path}`)
    }
  }
})

export default router
