import { defineStore } from 'pinia'
import { ref } from 'vue'
import { reviewApi } from '@/api'

export const useReviewStore = defineStore('review', () => {
  const reviews = ref([])
  const total = ref(0)
  const loading = ref(false)
  const currentReview = ref(null)
  const stats = ref({
    total: 0,
    pending: 0,
    approved: 0,
    rejected: 0,
    need_revision: 0,
    avg_rating: 0,
    approval_rate: 0
  })
  
  const templates = ref([])
  const comments = ref([])
  
  // 获取评审列表
  const fetchReviews = async (params = {}) => {
    loading.value = true
    try {
      const res = await reviewApi.getList(params)
      reviews.value = res.data.list
      total.value = res.data.total
      return res.data
    } catch (error) {
      console.error('获取评审列表失败:', error)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 获取评审详情
  const fetchReview = async (id) => {
    try {
      const res = await reviewApi.getDetail(id)
      currentReview.value = res.data
      return res.data
    } catch (error) {
      console.error('获取评审详情失败:', error)
      throw error
    }
  }
  
  // 获取测试用例的评审
  const fetchTestcaseReviews = async (testcaseId) => {
    try {
      const res = await reviewApi.getTestcaseReviews(testcaseId)
      return res.data.list
    } catch (error) {
      console.error('获取测试用例评审失败:', error)
      throw error
    }
  }
  
  // 创建评审
  const createReview = async (data) => {
    try {
      const res = await reviewApi.create(data)
      return res.data
    } catch (error) {
      console.error('创建评审失败:', error)
      throw error
    }
  }
  
  // 批量创建评审
  const batchCreateReviews = async (data) => {
    try {
      const res = await reviewApi.batchCreate(data)
      return res.data
    } catch (error) {
      console.error('批量创建评审失败:', error)
      throw error
    }
  }
  
  // 更新评审
  const updateReview = async (id, data) => {
    try {
      const res = await reviewApi.update(id, data)
      return res.data
    } catch (error) {
      console.error('更新评审失败:', error)
      throw error
    }
  }
  
  // 删除评审
  const deleteReview = async (id) => {
    try {
      await reviewApi.delete(id)
    } catch (error) {
      console.error('删除评审失败:', error)
      throw error
    }
  }
  
  // 获取评审评论
  const fetchComments = async (reviewId) => {
    try {
      const res = await reviewApi.getComments(reviewId)
      comments.value = res
      return res
    } catch (error) {
      console.error('获取评审评论失败:', error)
      throw error
    }
  }
  
  // 添加评论
  const addComment = async (reviewId, data) => {
    try {
      const res = await reviewApi.addComment(reviewId, data)
      return res.data
    } catch (error) {
      console.error('添加评论失败:', error)
      throw error
    }
  }
  
  // 删除评论
  const deleteComment = async (commentId) => {
    try {
      await reviewApi.deleteComment(commentId)
    } catch (error) {
      console.error('删除评论失败:', error)
      throw error
    }
  }
  
  // 获取评审模板
  const fetchTemplates = async () => {
    try {
      const res = await reviewApi.getTemplates()
      templates.value = res
      return res
    } catch (error) {
      console.error('获取评审模板失败:', error)
      throw error
    }
  }
  
  // 获取评审统计
  const fetchStats = async () => {
    try {
      const res = await reviewApi.getStats()
      stats.value = res.data
      return res.data
    } catch (error) {
      console.error('获取评审统计失败:', error)
      throw error
    }
  }
  
  // AI评审测试用例
  const aiReviewTestcases = async (data) => {
    try {
      const res = await reviewApi.aiReview(data)
      return res.data
    } catch (error) {
      console.error('AI评审失败:', error)
      throw error
    }
  }
  
  // AI评审预览
  const aiReviewPreview = async (data) => {
    try {
      const res = await reviewApi.aiReviewPreview(data)
      return res.data
    } catch (error) {
      console.error('AI评审预览失败:', error)
      throw error
    }
  }
  
  return {
    reviews,
    total,
    loading,
    currentReview,
    stats,
    templates,
    comments,
    fetchReviews,
    fetchReview,
    fetchTestcaseReviews,
    createReview,
    batchCreateReviews,
    updateReview,
    deleteReview,
    fetchComments,
    addComment,
    deleteComment,
    fetchTemplates,
    fetchStats,
    aiReviewTestcases,
    aiReviewPreview
  }
})
