import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeApi } from '@/api'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const knowledges = ref([])
  const allKnowledges = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentKnowledge = ref(null)

  // 获取知识库列表（分页）
  const fetchKnowledges = async (params = {}) => {
    loading.value = true
    try {
      const res = await knowledgeApi.getList(params)
      knowledges.value = res.data.list
      total.value = res.data.total
      return res.data
    } catch (error) {
      console.error('获取知识库列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 获取所有启用的知识库（用于下拉选择）
  const fetchAllKnowledges = async () => {
    try {
      const res = await knowledgeApi.getAll()
      allKnowledges.value = res.data
      return res.data
    } catch (error) {
      console.error('获取知识库列表失败:', error)
      throw error
    }
  }

  // 获取知识库详情
  const fetchKnowledge = async (id) => {
    try {
      const res = await knowledgeApi.getDetail(id)
      currentKnowledge.value = res.data
      return res.data
    } catch (error) {
      console.error('获取知识库详情失败:', error)
      throw error
    }
  }

  // 创建知识库
  const createKnowledge = async (data) => {
    try {
      const res = await knowledgeApi.create(data)
      return res.data
    } catch (error) {
      console.error('创建知识库失败:', error)
      throw error
    }
  }

  // 更新知识库
  const updateKnowledge = async (id, data) => {
    try {
      const res = await knowledgeApi.update(id, data)
      return res.data
    } catch (error) {
      console.error('更新知识库失败:', error)
      throw error
    }
  }

  // 删除知识库
  const deleteKnowledge = async (id) => {
    try {
      await knowledgeApi.delete(id)
    } catch (error) {
      console.error('删除知识库失败:', error)
      throw error
    }
  }

  // 批量获取知识库内容
  const fetchKnowledgesBatch = async (ids) => {
    try {
      const res = await knowledgeApi.getBatch(ids)
      return res.data
    } catch (error) {
      console.error('批量获取知识库失败:', error)
      throw error
    }
  }

  return {
    knowledges,
    allKnowledges,
    total,
    loading,
    currentKnowledge,
    fetchKnowledges,
    fetchAllKnowledges,
    fetchKnowledge,
    createKnowledge,
    updateKnowledge,
    deleteKnowledge,
    fetchKnowledgesBatch
  }
})
