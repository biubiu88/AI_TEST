import { defineStore } from 'pinia'
import { authApi } from '@/api'
import router from '@/router'

// 视图组件映射
const viewComponents = {
  'Layout': () => import('@/layout/index.vue'),
  'Home': () => import('@/views/DashboardView.vue'),
  'RequirementView': () => import('@/views/RequirementView.vue'),
  'TestCaseView': () => import('@/views/TestCaseView.vue'),
  'GenerateView': () => import('@/views/GenerateView.vue'),
  'PromptView': () => import('@/views/PromptView.vue'),
  'KnowledgeView': () => import('@/views/KnowledgeView.vue'),
  'LLMConfigView': () => import('@/views/LLMConfigView.vue'),
  'MCPConfigView': () => import('@/views/MCPConfigView.vue'),
  'AIAssistantView': () => import('@/views/AIAssistantView.vue'),
  'MenuView': () => import('@/views/MenuView.vue'),
  'UserView': () => import('@/views/UserView.vue'),
  'RoleView': () => import('@/views/RoleView.vue'),
  'LogView': () => import('@/views/LogView.vue'),
}

export const usePermissionStore = defineStore('permission', {
  state: () => ({
    // 用户权限列表
    permissions: JSON.parse(localStorage.getItem('permissions') || '[]'),
    // 用户菜单（树形结构）
    menus: JSON.parse(localStorage.getItem('menus') || '[]'),
    // 动态路由是否已添加
    routesAdded: false,
    // 动态路由列表
    dynamicRoutes: []
  }),

  getters: {
    // 获取权限列表
    getPermissions: (state) => state.permissions,
    // 获取菜单列表
    getMenus: (state) => state.menus,
    // 判断是否有某个权限
    hasPermission: (state) => (permission) => {
      if (!permission) return true
      return state.permissions.includes(permission)
    },
    // 判断是否有某些权限中的任意一个
    hasAnyPermission: (state) => (permissions) => {
      if (!permissions || permissions.length === 0) return true
      return permissions.some(p => state.permissions.includes(p))
    },
    // 判断是否有所有权限
    hasAllPermissions: (state) => (permissions) => {
      if (!permissions || permissions.length === 0) return true
      return permissions.every(p => state.permissions.includes(p))
    }
  },

  actions: {
    // 设置权限
    setPermissions(permissions) {
      this.permissions = permissions || []
      localStorage.setItem('permissions', JSON.stringify(this.permissions))
    },

    // 设置菜单
    setMenus(menus) {
      this.menus = menus || []
      localStorage.setItem('menus', JSON.stringify(this.menus))
    },

    // 清除权限信息
    clearPermissions() {
      this.permissions = []
      this.menus = []
      this.routesAdded = false
      this.dynamicRoutes = []
      localStorage.removeItem('permissions')
      localStorage.removeItem('menus')
    },

    // 将菜单转换为路由
    generateRoutes(menus) {
      const routes = []
      
      const processMenu = (menu, parentPath = '') => {
        if (menu.type === 'button') return null
        
        const route = {
          path: menu.path,
          name: menu.name,
          meta: {
            title: menu.meta?.title || menu.name,
            icon: menu.meta?.icon,
            hidden: menu.meta?.hidden || false,
            keepAlive: menu.meta?.keepAlive || false,
            permission: menu.meta?.permission
          }
        }

        // 处理组件
        if (menu.component) {
          if (menu.component === 'Layout') {
            route.component = viewComponents['Layout']
          } else {
            // 动态导入组件
            const componentName = menu.component.replace(/^.*\//, '').replace('.vue', '')
            if (viewComponents[componentName]) {
              route.component = viewComponents[componentName]
            } else {
              // 尝试动态导入
              route.component = () => import(`@/views/${menu.component}.vue`)
            }
          }
        }

        // 处理重定向
        if (menu.redirect) {
          route.redirect = menu.redirect
        }

        // 处理子菜单
        if (menu.children && menu.children.length > 0) {
          route.children = menu.children
            .map(child => processMenu(child, menu.path))
            .filter(Boolean)
        }

        return route
      }

      menus.forEach(menu => {
        const route = processMenu(menu)
        if (route) {
          routes.push(route)
        }
      })

      return routes
    },

    // 添加动态路由
    async addDynamicRoutes() {
      if (this.routesAdded) return

      const routes = this.generateRoutes(this.menus)
      this.dynamicRoutes = routes

      // 添加动态路由到router
      routes.forEach(route => {
        // 如果是顶级路由且有children，需要特殊处理
        if (!router.hasRoute(route.name)) {
          router.addRoute(route)
        }
      })

      // 添加404路由（放在最后）
      if (!router.hasRoute('NotFound')) {
        router.addRoute({
          path: '/:pathMatch(.*)*',
          name: 'NotFound',
          redirect: '/404'
        })
      }

      this.routesAdded = true
    },

    // 重置路由
    resetRoutes() {
      // 移除动态添加的路由
      this.dynamicRoutes.forEach(route => {
        if (route.name && router.hasRoute(route.name)) {
          router.removeRoute(route.name)
        }
      })
      this.routesAdded = false
      this.dynamicRoutes = []
    },

    // 从服务器获取用户菜单和权限
    async fetchPermissions() {
      try {
        const [menuRes, permRes] = await Promise.all([
          authApi.getUserMenus(),
          authApi.getUserPermissions()
        ])
        
        this.setMenus(menuRes.data)
        this.setPermissions(permRes.data)
        
        return { menus: menuRes.data, permissions: permRes.data }
      } catch (error) {
        console.error('获取权限信息失败:', error)
        throw error
      }
    }
  }
})
