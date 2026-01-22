import { defineStore } from 'pinia'
import { ref } from 'vue'
import { testcaseApi, aiApi } from '@/api'

export const useTestcaseStore = defineStore('testcase', () => {
  const testcases = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentTestcase = ref(null)
  const stats = ref({
    total: 0,
    passed: 0,
    failed: 0,
    pending: 0,
    blocked: 0,
    ai_generated: 0,
    pass_rate: 0
  })

  // 获取测试用例列表
  const fetchTestcases = async (params = {}) => {
    loading.value = true
    try {
      const res = await testcaseApi.getList(params)
      testcases.value = res.data.list
      total.value = res.data.total
      return res.data
    } catch (error) {
      console.error('获取测试用例列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取测试用例详情
  const fetchTestcase = async (id) => {
    try {
      const res = await testcaseApi.getDetail(id)
      currentTestcase.value = res.data
      return res.data
    } catch (error) {
      console.error('获取测试用例详情失败:', error)
      throw error
    }
  }

  // 创建测试用例
  const createTestcase = async (data) => {
    try {
      const res = await testcaseApi.create(data)
      return res.data
    } catch (error) {
      console.error('创建测试用例失败:', error)
      throw error
    }
  }

  // 批量创建测试用例
  const createTestcasesBatch = async (data) => {
    try {
      const res = await testcaseApi.createBatch(data)
      return res.data
    } catch (error) {
      console.error('批量创建测试用例失败:', error)
      throw error
    }
  }

  // 更新测试用例
  const updateTestcase = async (id, data) => {
    try {
      const res = await testcaseApi.update(id, data)
      return res.data
    } catch (error) {
      console.error('更新测试用例失败:', error)
      throw error
    }
  }

  // 删除测试用例
  const deleteTestcase = async (id) => {
    try {
      await testcaseApi.delete(id)
    } catch (error) {
      console.error('删除测试用例失败:', error)
      throw error
    }
  }

  // 获取统计数据
  const fetchStats = async () => {
    try {
      const res = await testcaseApi.getStats()
      stats.value = res.data
      return res.data
    } catch (error) {
      console.error('获取统计数据失败:', error)
      throw error
    }
  }

  // AI 生成测试用例
  const generateTestcases = async (data) => {
    try {
      const res = await aiApi.generate(data)
      return res.data
    } catch (error) {
      console.error('AI生成测试用例失败:', error)
      throw error
    }
  }

  // AI 预览测试用例
  const previewTestcases = async (data) => {
    try {
      const res = await aiApi.preview(data)
      return res.data
    } catch (error) {
      console.error('AI预览测试用例失败:', error)
      throw error
    }
  }

  return {
    testcases,
    total,
    loading,
    currentTestcase,
    stats,
    fetchTestcases,
    fetchTestcase,
    createTestcase,
    createTestcasesBatch,
    updateTestcase,
    deleteTestcase,
    fetchStats,
    generateTestcases,
    previewTestcases
  }
})
