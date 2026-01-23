import { usePermissionStore } from '@/stores/permission'

/**
 * 权限指令
 * 使用方式：v-permission="'permission:code'" 或 v-permission="['permission:code1', 'permission:code2']"
 */
export const permission = {
  mounted(el, binding) {
    const permissionStore = usePermissionStore()
    const { value } = binding

    if (value) {
      const permissions = permissionStore.permissions
      let hasPermission = false

      if (Array.isArray(value)) {
        // 数组形式：拥有其中任一权限即可
        hasPermission = value.some(p => permissions.includes(p))
      } else {
        // 字符串形式
        hasPermission = permissions.includes(value)
      }

      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  }
}

/**
 * 角色指令
 * 使用方式：v-role="'admin'" 或 v-role="['admin', 'editor']"
 */
export const role = {
  mounted(el, binding) {
    const { value } = binding
    const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
    const roles = userInfo.roles || []

    if (value) {
      let hasRole = false

      if (Array.isArray(value)) {
        hasRole = value.some(r => roles.includes(r))
      } else {
        hasRole = roles.includes(value)
      }

      if (!hasRole) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  }
}

/**
 * 检查权限的函数（用于逻辑判断）
 * @param {string|string[]} permission - 权限编码
 * @param {boolean} all - 是否需要所有权限，默认false
 */
export function hasPermission(permission, all = false) {
  const permissionStore = usePermissionStore()
  const permissions = permissionStore.permissions

  if (!permission) return true

  if (Array.isArray(permission)) {
    if (all) {
      return permission.every(p => permissions.includes(p))
    }
    return permission.some(p => permissions.includes(p))
  }

  return permissions.includes(permission)
}

/**
 * 检查角色的函数
 * @param {string|string[]} role - 角色编码
 * @param {boolean} all - 是否需要所有角色，默认false
 */
export function hasRole(role, all = false) {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  const roles = userInfo.roles || []

  if (!role) return true

  if (Array.isArray(role)) {
    if (all) {
      return role.every(r => roles.includes(r))
    }
    return role.some(r => roles.includes(r))
  }

  return roles.includes(role)
}

/**
 * 注册权限相关指令
 */
export function setupPermissionDirectives(app) {
  app.directive('permission', permission)
  app.directive('role', role)
}

export default {
  install(app) {
    setupPermissionDirectives(app)
  }
}
