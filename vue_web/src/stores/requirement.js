import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { requirementApi } from '@/api'

export const useRequirementStore = defineStore('requirement', () => {
  const requirements = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentRequirement = ref(null)
  const modules = ref([])

  // 获取需求列表
  const fetchRequirements = async (params = {}) => {
    loading.value = true
    try {
      const res = await requirementApi.getList(params)
      requirements.value = res.data.list
      total.value = res.data.total
      return res.data
    } catch (error) {
      console.error('获取需求列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取需求详情
  const fetchRequirement = async (id) => {
    try {
      const res = await requirementApi.getDetail(id)
      currentRequirement.value = res.data
      return res.data
    } catch (error) {
      console.error('获取需求详情失败:', error)
      throw error
    }
  }

  // 创建需求
  const createRequirement = async (data) => {
    try {
      const res = await requirementApi.create(data)
      return res.data
    } catch (error) {
      console.error('创建需求失败:', error)
      throw error
    }
  }

  // 更新需求
  const updateRequirement = async (id, data) => {
    try {
      const res = await requirementApi.update(id, data)
      return res.data
    } catch (error) {
      console.error('更新需求失败:', error)
      throw error
    }
  }

  // 删除需求
  const deleteRequirement = async (id) => {
    try {
      await requirementApi.delete(id)
    } catch (error) {
      console.error('删除需求失败:', error)
      throw error
    }
  }

  // 获取模块列表
  const fetchModules = async () => {
    try {
      const res = await requirementApi.getModules()
      modules.value = res.data
      return res.data
    } catch (error) {
      console.error('获取模块列表失败:', error)
      throw error
    }
  }

  return {
    requirements,
    total,
    loading,
    currentRequirement,
    modules,
    fetchRequirements,
    fetchRequirement,
    createRequirement,
    updateRequirement,
    deleteRequirement,
    fetchModules
  }
})
