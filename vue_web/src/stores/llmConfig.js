import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { llmConfigApi } from '@/api'

export const useLLMConfigStore = defineStore('llmConfig', () => {
  // 状态
  const configs = ref([])
  const allConfigs = ref([])
  const providers = ref({})
  const total = ref(0)
  const loading = ref(false)
  const currentConfig = ref(null)
  const availableModels = ref([])
  const modelsLoading = ref(false)

  // 计算属性
  const defaultConfig = computed(() => {
    return allConfigs.value.find(c => c.is_default) || null
  })

  // 获取配置列表（分页）
  const fetchConfigs = async (params = {}) => {
    loading.value = true
    try {
      const response = await llmConfigApi.getList(params)
      configs.value = response.data.items
      total.value = response.data.total
      return response.data
    } finally {
      loading.value = false
    }
  }

  // 获取所有启用的配置
  const fetchAllConfigs = async () => {
    try {
      const response = await llmConfigApi.getAll()
      allConfigs.value = response.data
      return response.data
    } catch (e) {
      console.error('获取大模型配置列表失败', e)
      return []
    }
  }

  // 获取供应商列表
  const fetchProviders = async () => {
    try {
      const response = await llmConfigApi.getProviders()
      providers.value = response.data
      return response.data
    } catch (e) {
      console.error('获取供应商列表失败', e)
      return {}
    }
  }

  // 获取单个配置详情
  const fetchConfig = async (id) => {
    try {
      const response = await llmConfigApi.getDetail(id)
      currentConfig.value = response.data
      return response.data
    } catch (e) {
      console.error('获取配置详情失败', e)
      throw e
    }
  }

  // 创建配置
  const createConfig = async (data) => {
    try {
      const response = await llmConfigApi.create(data)
      await fetchConfigs()
      await fetchAllConfigs()
      return response.data
    } catch (e) {
      console.error('创建配置失败', e)
      throw e
    }
  }

  // 更新配置
  const updateConfig = async (id, data) => {
    try {
      const response = await llmConfigApi.update(id, data)
      await fetchConfigs()
      await fetchAllConfigs()
      return response.data
    } catch (e) {
      console.error('更新配置失败', e)
      throw e
    }
  }

  // 删除配置
  const deleteConfig = async (id) => {
    try {
      await llmConfigApi.delete(id)
      await fetchConfigs()
      await fetchAllConfigs()
    } catch (e) {
      console.error('删除配置失败', e)
      throw e
    }
  }

  // 设置默认配置
  const setDefaultConfig = async (id) => {
    try {
      const response = await llmConfigApi.setDefault(id)
      await fetchConfigs()
      await fetchAllConfigs()
      return response.data
    } catch (e) {
      console.error('设置默认配置失败', e)
      throw e
    }
  }

  // 获取可用模型列表
  const fetchAvailableModels = async (apiBase, apiKey) => {
    modelsLoading.value = true
    availableModels.value = []
    try {
      const response = await llmConfigApi.fetchModels({ api_base: apiBase, api_key: apiKey })
      availableModels.value = response.data
      return response.data
    } catch (e) {
      console.error('获取模型列表失败', e)
      throw e
    } finally {
      modelsLoading.value = false
    }
  }

  // 测试配置
  const testConfig = async (data) => {
    try {
      const response = await llmConfigApi.testConfig(data)
      return response.data
    } catch (e) {
      console.error('测试配置失败', e)
      throw e
    }
  }

  return {
    // 状态
    configs,
    allConfigs,
    providers,
    total,
    loading,
    currentConfig,
    availableModels,
    modelsLoading,
    // 计算属性
    defaultConfig,
    // 方法
    fetchConfigs,
    fetchAllConfigs,
    fetchProviders,
    fetchConfig,
    createConfig,
    updateConfig,
    deleteConfig,
    setDefaultConfig,
    fetchAvailableModels,
    testConfig
  }
})
