import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 创建 axios 实例
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  timeout: 600000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加token到请求头
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 如果是 blob 类型响应（文件下载），直接返回数据
    if (response.config.responseType === 'blob') {
      return response.data
    }
    
    const { data } = response
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message))
    }
    return data
  },
  (error) => {
    const status = error.response?.status
    const message = error.response?.data?.message || error.message || '网络错误'
    
    // 处理401未授权
    if (status === 401) {
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('userInfo')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

// 认证相关 API
export const authApi = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data),
  changePassword: (data) => api.post('/auth/change-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  refreshToken: () => api.post('/auth/refresh'),
  // 获取用户菜单
  getUserMenus: () => api.get('/permission/user/menus'),
  // 获取用户权限
  getUserPermissions: () => api.get('/permission/user/permissions')
}

// 需求相关 API
export const requirementApi = {
  getList: (params) => api.get('/requirements', { params }),
  getDetail: (id) => api.get(`/requirements/${id}`),
  create: (data) => api.post('/requirements', data),
  update: (id, data) => api.put(`/requirements/${id}`, data),
  delete: (id) => api.delete(`/requirements/${id}`),
  getModules: () => api.get('/requirements/modules')
}

// 测试用例相关 API
export const testcaseApi = {
  getList: (params) => api.get('/testcases', { params }),
  getDetail: (id) => api.get(`/testcases/${id}`),
  create: (data) => api.post('/testcases', data),
  createBatch: (data) => api.post('/testcases/batch', data),
  update: (id, data) => api.put(`/testcases/${id}`, data),
  delete: (id) => api.delete(`/testcases/${id}`),
  getStats: () => api.get('/testcases/stats'),
  // 导出测试用例
  export: (params) => api.get('/testcases/export', { 
    params, 
    responseType: 'blob',
    transformResponse: [(data) => data] // 不进行 JSON 解析
  }),
  // 下载导入模板
  downloadTemplate: () => api.get('/testcases/template', { 
    responseType: 'blob',
    transformResponse: [(data) => data]
  }),
  // 导入测试用例
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/testcases/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// AI 相关 API
export const aiApi = {
  generate: (data) => api.post('/ai/generate', data),
  preview: (data) => api.post('/ai/preview', data)
}

// 提示词相关 API
export const promptApi = {
  getList: (params) => api.get('/prompts', { params }),
  getAll: () => api.get('/prompts/all'),
  getDetail: (id) => api.get(`/prompts/${id}`),
  create: (data) => api.post('/prompts', data),
  update: (id, data) => api.put(`/prompts/${id}`, data),
  delete: (id) => api.delete(`/prompts/${id}`),
  setDefault: (id) => api.put(`/prompts/${id}/default`),
  // 导入导出
  export: (ids) => api.get('/prompts/export', { 
    params: ids ? { ids: ids.join(',') } : {},
    responseType: 'blob'
  }),
  downloadTemplate: () => api.get('/prompts/template', { responseType: 'blob' }),
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/prompts/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 知识库相关 API
export const knowledgeApi = {
  getList: (params) => api.get('/knowledges', { params }),
  getAll: () => api.get('/knowledges/all'),
  getDetail: (id) => api.get(`/knowledges/${id}`),
  create: (data) => api.post('/knowledges', data),
  update: (id, data) => api.put(`/knowledges/${id}`, data),
  delete: (id) => api.delete(`/knowledges/${id}`),
  getBatch: (ids) => api.get('/knowledges/batch', { params: { ids: ids.join(',') } }),
  // 导入导出
  export: (ids) => api.get('/knowledges/export', { 
    params: ids ? { ids: ids.join(',') } : {},
    responseType: 'blob'
  }),
  downloadTemplate: () => api.get('/knowledges/template', { responseType: 'blob' }),
  import: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/knowledges/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 大模型配置相关 API
export const llmConfigApi = {
  getList: (params) => api.get('/llm-configs', { params }),
  getAll: () => api.get('/llm-configs/all'),
  getDetail: (id) => api.get(`/llm-configs/${id}`),
  create: (data) => api.post('/llm-configs', data),
  update: (id, data) => api.put(`/llm-configs/${id}`, data),
  delete: (id) => api.delete(`/llm-configs/${id}`),
  setDefault: (id) => api.put(`/llm-configs/${id}/default`),
  getProviders: () => api.get('/llm-configs/providers'),
  fetchModels: (data) => api.post('/llm-configs/models', data),
  testConfig: (data) => api.post('/llm-configs/test', data)
}

// 权限管理相关 API
export const permissionApi = {
  // 角色管理
  getRoles: (params) => api.get('/permission/roles', { params }),
  getAllRoles: () => api.get('/permission/roles/all'),
  getRole: (id) => api.get(`/permission/roles/${id}`),
  createRole: (data) => api.post('/permission/roles', data),
  updateRole: (id, data) => api.put(`/permission/roles/${id}`, data),
  deleteRole: (id) => api.delete(`/permission/roles/${id}`),
  
  // 权限管理
  getPermissions: (params) => api.get('/permission/permissions', { params }),
  getAllPermissions: () => api.get('/permission/permissions/all'),
  createPermission: (data) => api.post('/permission/permissions', data),
  updatePermission: (id, data) => api.put(`/permission/permissions/${id}`, data),
  deletePermission: (id) => api.delete(`/permission/permissions/${id}`),
  
  // 菜单管理
  getMenus: () => api.get('/permission/menus'),
  getAllMenus: () => api.get('/permission/menus/all'),
  getMenu: (id) => api.get(`/permission/menus/${id}`),
  createMenu: (data) => api.post('/permission/menus', data),
  updateMenu: (id, data) => api.put(`/permission/menus/${id}`, data),
  deleteMenu: (id) => api.delete(`/permission/menus/${id}`),
  
  // 用户角色管理
  getUserRoles: (userId) => api.get(`/permission/users/${userId}/roles`),
  setUserRoles: (userId, roleIds) => api.put(`/permission/users/${userId}/roles`, { roleIds })
}

// 用户管理相关 API
export const userApi = {
  getList: (params) => api.get('/users', { params }),
  getDetail: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  resetPassword: (id, password) => api.post(`/users/${id}/reset-password`, { password })
}

// 日志审计相关 API
export const logApi = {
  getList: (params) => api.get('/logs', { params }),
  getDetail: (id) => api.get(`/logs/${id}`),
  getStatistics: () => api.get('/logs/statistics'),
  export: (params) => api.get('/logs/export', { params })
}

// MCP配置相关 API
export const mcpApi = {
  getList: (params) => api.get('/mcp-configs', { params }),
  getAll: () => api.get('/mcp-configs/all'),
  getDetail: (id) => api.get(`/mcp-configs/${id}`),
  create: (data) => api.post('/mcp-configs', data),
  update: (id, data) => api.put(`/mcp-configs/${id}`, data),
  delete: (id) => api.delete(`/mcp-configs/${id}`),
  test: (id) => api.post(`/mcp-configs/${id}/test`)
}

// AI助手相关 API
export const aiAssistantApi = {
  // 会话管理
  getSessions: (params) => api.get('/ai-assistant/sessions', { params }),
  createSession: (data) => api.post('/ai-assistant/sessions', data),
  getSession: (id) => api.get(`/ai-assistant/sessions/${id}`),
  updateSession: (id, data) => api.put(`/ai-assistant/sessions/${id}`, data),
  deleteSession: (id) => api.delete(`/ai-assistant/sessions/${id}`),
  
  // 消息管理
  getMessages: (sessionId) => api.get(`/ai-assistant/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, data) => api.post(`/ai-assistant/sessions/${sessionId}/messages`, data),
  deleteMessage: (sessionId, messageId) => api.delete(`/ai-assistant/sessions/${sessionId}/messages/${messageId}`),
  
  // 配置选项
  getKnowledgeBases: () => api.get('/ai-assistant/knowledge'),
  getPrompts: () => api.get('/ai-assistant/prompts'),
  getMcpConfigs: () => api.get('/ai-assistant/mcp-configs'),
  getModels: () => api.get('/ai-assistant/models')
}

// 用例评审相关 API
export const reviewApi = {
  // 评审管理
  getList: (params) => api.get('/reviews/list', { params }),
  getDetail: (id) => api.get(`/reviews/${id}`),
  getTestcaseReviews: (testcaseId) => api.get(`/reviews/testcase/${testcaseId}`),
  create: (data) => api.post('/reviews', data),
  update: (id, data) => api.put(`/reviews/${id}`, data),
  delete: (id) => api.delete(`/reviews/${id}`),
  batchCreate: (data) => api.post('/reviews/batch', data),
  
  // AI评审
  aiReview: (data) => api.post('/reviews/ai-review', data),
  aiReviewPreview: (data) => api.post('/reviews/ai-review-preview', data),
  
  // 评审评论
  getComments: (reviewId) => api.get(`/reviews/${reviewId}/comments`),
  addComment: (reviewId, data) => api.post(`/reviews/${reviewId}/comments`, data),
  deleteComment: (commentId) => api.delete(`/reviews/comments/${commentId}`),
  
  // 评审模板
  getTemplates: () => api.get('/reviews/templates'),
  getTemplate: (id) => api.get(`/reviews/templates/${id}`),
  createTemplate: (data) => api.post('/reviews/templates', data),
  updateTemplate: (id, data) => api.put(`/reviews/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/reviews/templates/${id}`),
  
  // 统计
  getStats: () => api.get('/reviews/stats')
}

export default api
