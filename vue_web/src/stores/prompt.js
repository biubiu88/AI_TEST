import { defineStore } from 'pinia'
import { ref } from 'vue'
import { promptApi } from '@/api'

export const usePromptStore = defineStore('prompt', () => {
  const prompts = ref([])
  const allPrompts = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentPrompt = ref(null)

  // 获取提示词列表（分页）
  const fetchPrompts = async (params = {}) => {
    loading.value = true
    try {
      const res = await promptApi.getList(params)
      prompts.value = res.data.list
      total.value = res.data.total
      return res.data
    } catch (error) {
      console.error('获取提示词列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取所有启用的提示词（用于下拉选择）
  const fetchAllPrompts = async () => {
    try {
      const res = await promptApi.getAll()
      allPrompts.value = res.data
      return res.data
    } catch (error) {
      console.error('获取提示词列表失败:', error)
      throw error
    }
  }

  // 获取提示词详情
  const fetchPrompt = async (id) => {
    try {
      const res = await promptApi.getDetail(id)
      currentPrompt.value = res.data
      return res.data
    } catch (error) {
      console.error('获取提示词详情失败:', error)
      throw error
    }
  }

  // 创建提示词
  const createPrompt = async (data) => {
    try {
      const res = await promptApi.create(data)
      return res.data
    } catch (error) {
      console.error('创建提示词失败:', error)
      throw error
    }
  }

  // 更新提示词
  const updatePrompt = async (id, data) => {
    try {
      const res = await promptApi.update(id, data)
      return res.data
    } catch (error) {
      console.error('更新提示词失败:', error)
      throw error
    }
  }

  // 删除提示词
  const deletePrompt = async (id) => {
    try {
      await promptApi.delete(id)
    } catch (error) {
      console.error('删除提示词失败:', error)
      throw error
    }
  }

  // 设置默认提示词
  const setDefaultPrompt = async (id) => {
    try {
      const res = await promptApi.setDefault(id)
      return res.data
    } catch (error) {
      console.error('设置默认提示词失败:', error)
      throw error
    }
  }

  return {
    prompts,
    allPrompts,
    total,
    loading,
    currentPrompt,
    fetchPrompts,
    fetchAllPrompts,
    fetchPrompt,
    createPrompt,
    updatePrompt,
    deletePrompt,
    setDefaultPrompt
  }
})
