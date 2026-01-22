import { defineStore } from 'pinia'
import { authApi } from '@/api'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('accessToken') || '',
    refreshToken: localStorage.getItem('refreshToken') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    isLoggedIn: !!localStorage.getItem('accessToken')
  }),

  getters: {
    getUserInfo: (state) => state.userInfo,
    getToken: (state) => state.token,
    isAuthenticated: (state) => state.isLoggedIn && !!state.token
  },

  actions: {
    // 登录
    async login(loginData) {
      try {
        const res = await authApi.login(loginData)
        const { accessToken, refreshToken, user } = res.data
        
        this.token = accessToken
        this.refreshToken = refreshToken
        this.userInfo = user
        this.isLoggedIn = true
        
        localStorage.setItem('accessToken', accessToken)
        localStorage.setItem('refreshToken', refreshToken)
        localStorage.setItem('userInfo', JSON.stringify(user))
        localStorage.setItem('userName', user.nickname || user.username)
        
        return res
      } catch (error) {
        throw error
      }
    },

    // 注册
    async register(registerData) {
      try {
        const res = await authApi.register(registerData)
        return res
      } catch (error) {
        throw error
      }
    },

    // 登出
    async logout() {
      try {
        await authApi.logout()
      } catch (error) {
        // 忽略登出错误
      } finally {
        this.clearAuth()
      }
    },

    // 清除认证信息
    clearAuth() {
      this.token = ''
      this.refreshToken = ''
      this.userInfo = null
      this.isLoggedIn = false
      
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('userName')
    },

    // 获取用户信息
    async fetchUserInfo() {
      try {
        const res = await authApi.getProfile()
        this.userInfo = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
        localStorage.setItem('userName', res.data.nickname || res.data.username)
        return res.data
      } catch (error) {
        this.clearAuth()
        throw error
      }
    },

    // 修改密码
    async changePassword(data) {
      try {
        const res = await authApi.changePassword(data)
        return res
      } catch (error) {
        throw error
      }
    },

    // 重置密码
    async resetPassword(data) {
      try {
        const res = await authApi.resetPassword(data)
        return res
      } catch (error) {
        throw error
      }
    }
  }
})
