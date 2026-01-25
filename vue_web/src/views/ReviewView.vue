<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useReviewStore } from '@/stores/review'
import { useTestcaseStore } from '@/stores/testcase'
import { usePromptStore } from '@/stores/prompt'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useLLMConfigStore } from '@/stores/llmConfig'
import { reviewApi } from '@/api'

const route = useRoute()
const router = useRouter()
const reviewStore = useReviewStore()
const testcaseStore = useTestcaseStore()
const promptStore = usePromptStore()
const knowledgeStore = useKnowledgeStore()
const llmConfigStore = useLLMConfigStore()

// 搜索参数
const searchForm = reactive({
  keyword: '',
  testcase_id: route.query.testcaseId ? Number(route.query.testcaseId) : '',
  status: '',
  page: 1,
  per_page: 20
})

// 评审对话框
const reviewDialogVisible = ref(false)
const reviewDialogTitle = ref('')
const reviewFormRef = ref(null)
const reviewForm = reactive({
  id: null,
  testcase_id: '',
  status: 'pending',
  overall_rating: 3,
  comments: '',
  improvement_suggestions: '',
  clarity_score: 3,
  completeness_score: 3,
  feasibility_score: 3,
  coverage_score: 3
})

const reviewFormRules = {
  status: [{ required: true, message: '请选择评审状态', trigger: 'change' }],
  comments: [{ required: true, message: '请输入评审意见', trigger: 'blur' }]
}

// 详情对话框
const detailVisible = ref(false)
const currentDetail = ref(null)

// 评论相关
const commentDialogVisible = ref(false)
const commentList = ref([])
const newComment = ref('')

// 选项配置
const statusOptions = [
  { label: '待评审', value: 'pending' },
  { label: '通过', value: 'approved' },
  { label: '拒绝', value: 'rejected' },
  { label: '需要修改', value: 'need_revision' }
]

const ratingOptions = [
  { label: '1分', value: 1 },
  { label: '2分', value: 2 },
  { label: '3分', value: 3 },
  { label: '4分', value: 4 },
  { label: '5分', value: 5 }
]

// 加载数据
const loadData = async () => {
  await reviewStore.fetchReviews(searchForm)
  await reviewStore.fetchStats()
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  reviewStore.fetchReviews(searchForm)
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.testcase_id = ''
  searchForm.status = ''
  searchForm.page = 1
  reviewStore.fetchReviews(searchForm)
}

// 分页变化
const handlePageChange = (page) => {
  searchForm.page = page
  reviewStore.fetchReviews(searchForm)
}

// 每页条数变化
const handleSizeChange = (size) => {
  searchForm.per_page = size
  searchForm.page = 1
  reviewStore.fetchReviews(searchForm)
}

// 编辑评审
const handleEditReview = (row) => {
  reviewDialogTitle.value = '编辑评审'
  Object.assign(reviewForm, {
    id: row.id,
    testcase_id: row.testcase_id,
    status: row.status,
    overall_rating: row.overall_rating || 3,
    comments: row.comments || '',
    improvement_suggestions: row.improvement_suggestions || '',
    clarity_score: row.clarity_score || 3,
    completeness_score: row.completeness_score || 3,
    feasibility_score: row.feasibility_score || 3,
    coverage_score: row.coverage_score || 3
  })
  reviewDialogVisible.value = true
}

// 查看详情
const handleViewDetail = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}

// 提交评审
const handleSubmitReview = async () => {
  try {
    await reviewFormRef.value.validate()
    
    const data = {
      status: reviewForm.status,
      overall_rating: reviewForm.overall_rating,
      comments: reviewForm.comments,
      improvement_suggestions: reviewForm.improvement_suggestions,
      clarity_score: reviewForm.clarity_score,
      completeness_score: reviewForm.completeness_score,
      feasibility_score: reviewForm.feasibility_score,
      coverage_score: reviewForm.coverage_score
    }
    
    if (reviewForm.id) {
      await reviewStore.updateReview(reviewForm.id, data)
      ElMessage.success('评审更新成功')
    } else {
      if (!reviewForm.testcase_id) {
        ElMessage.warning('请选择测试用例')
        return
      }
      await reviewStore.createReview({
        testcase_id: reviewForm.testcase_id,
        ...data
      })
      ElMessage.success('评审创建成功')
    }
    
    reviewDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 删除评审
const handleDeleteReview = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除这条评审记录吗？`,
      '提示',
      { type: 'warning' }
    )
    await reviewStore.deleteReview(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 打开评论对话框
const handleOpenComments = async (row) => {
  try {
    const comments = await reviewStore.fetchComments(row.id)
    commentList.value = comments
    currentDetail.value = row
    commentDialogVisible.value = true
  } catch (e) {
    console.error(e)
  }
}

// 添加评论
const handleAddComment = async () => {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  try {
    await reviewStore.addComment(currentDetail.value.id, {
      content: newComment.value
    })
    ElMessage.success('评论添加成功')
    newComment.value = ''
    // 刷新评论列表
    const comments = await reviewStore.fetchComments(currentDetail.value.id)
    commentList.value = comments
  } catch (e) {
    console.error(e)
  }
}

// 删除评论
const handleDeleteComment = async (commentId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？', '提示', { type: 'warning' })
    await reviewStore.deleteComment(commentId)
    ElMessage.success('删除成功')
    // 刷新评论列表
    const comments = await reviewStore.fetchComments(currentDetail.value.id)
    commentList.value = comments
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 重置评审表单
const resetReviewForm = () => {
  reviewForm.id = null
  reviewForm.testcase_id = ''
  reviewForm.status = 'pending'
  reviewForm.overall_rating = 3
  reviewForm.comments = ''
  reviewForm.improvement_suggestions = ''
  reviewForm.clarity_score = 3
  reviewForm.completeness_score = 3
  reviewForm.feasibility_score = 3
  reviewForm.coverage_score = 3
  reviewFormRef.value?.resetFields()
}

// 获取状态标签
const getStatusType = (status) => {
  const types = {
    pending: 'info',
    approved: 'success',
    rejected: 'danger',
    need_revision: 'warning'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '待评审',
    approved: '通过',
    rejected: '拒绝',
    need_revision: '需要修改'
  }
  return labels[status] || status
}

// 计算平均分
const getAvgScore = (row) => {
  const scores = [
    row.clarity_score,
    row.completeness_score,
    row.feasibility_score,
    row.coverage_score
  ].filter(s => s !== null && s !== undefined)
  
  if (scores.length === 0) return '-'
  return (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
}

// ========== AI评审相关 ==========

// AI评审对话框
const aiReviewDialogVisible = ref(false)
const aiReviewForm = reactive({
  selected_testcase_ids: [],
  llm_config_id: '',
  prompt_id: '',
  knowledge_ids: []
})

// AI评审预览结果
const aiReviewPreviewVisible = ref(false)
const aiReviewPreviewData = ref([])
const aiReviewLoading = ref(false)

// 新增变量
const allTestcases = ref([])
const testcaseLoading = ref(false)
const testcaseSearchKeyword = ref('')

// 打开AI评审对话框
const handleOpenAIReview = () => {
  aiReviewDialogVisible.value = true
  // 重置状态
  aiReviewForm.selected_testcase_ids = []
  testcaseSearchKeyword.value = ''
  // 加载配置数据和测试用例
  loadAIReviewConfig()
  loadAllTestcases()
}

// 加载所有测试用例
const loadAllTestcases = async () => {
  testcaseLoading.value = true
  try {
    const result = await testcaseStore.fetchTestcases({
      page: 1,
      per_page: 1000
    })
    allTestcases.value = result.list || []
  } catch (e) {
    console.error('加载测试用例失败:', e)
    ElMessage.error('加载测试用例失败')
  } finally {
    testcaseLoading.value = false
  }
}

// 搜索测试用例
const handleSearchTestcases = async () => {
  if (!testcaseSearchKeyword.value.trim()) {
    loadAllTestcases()
    return
  }
  
  testcaseLoading.value = true
  try {
    const result = await testcaseStore.fetchTestcases({
      keyword: testcaseSearchKeyword.value,
      page: 1,
      per_page: 100
    })
    allTestcases.value = result.list || []
  } catch (e) {
    console.error('搜索测试用例失败:', e)
  } finally {
    testcaseLoading.value = false
  }
}

// 全选/取消全选
const handleSelectAllTestcases = () => {
  if (aiReviewForm.selected_testcase_ids.length === allTestcases.value.length) {
    aiReviewForm.selected_testcase_ids = []
  } else {
    aiReviewForm.selected_testcase_ids = allTestcases.value.map(tc => tc.id)
  }
}

// 检查是否选中
const isTestcaseSelected = (testcaseId) => {
  return aiReviewForm.selected_testcase_ids.includes(testcaseId)
}

// 切换选中状态
const handleToggleTestcase = (testcaseId) => {
  const index = aiReviewForm.selected_testcase_ids.indexOf(testcaseId)
  if (index > -1) {
    aiReviewForm.selected_testcase_ids.splice(index, 1)
  } else {
    aiReviewForm.selected_testcase_ids.push(testcaseId)
  }
}

// 加载AI评审配置
const loadAIReviewConfig = async () => {
  await promptStore.fetchAllPrompts()
  await knowledgeStore.fetchAllKnowledges()
  await llmConfigStore.fetchAllConfigs()
  
  // 设置默认提示词
  const defaultPrompt = promptStore.allPrompts.find(p => p.is_default)
  if (defaultPrompt) {
    aiReviewForm.prompt_id = defaultPrompt.id
  }
  
  // 设置默认大模型配置
  const defaultLLMConfig = llmConfigStore.allConfigs.find(c => c.is_default)
  if (defaultLLMConfig) {
    aiReviewForm.llm_config_id = defaultLLMConfig.id
  }
}

// AI评审预览
const handleAIReviewPreview = async () => {
  if (aiReviewForm.selected_testcase_ids.length === 0) {
    ElMessage.warning('请先选择要评审的测试用例')
    return
  }
  
  aiReviewLoading.value = true
  try {
    const data = {
      testcase_ids: aiReviewForm.selected_testcase_ids,
      llm_config_id: aiReviewForm.llm_config_id,
      prompt_id: aiReviewForm.prompt_id,
      knowledge_ids: aiReviewForm.knowledge_ids
    }
    
    const result = await reviewStore.aiReviewPreview(data)
    aiReviewPreviewData.value = result.reviews
    aiReviewPreviewVisible.value = true
    ElMessage.success('AI评审预览完成')
  } catch (e) {
    console.error(e)
  } finally {
    aiReviewLoading.value = false
  }
}

// AI评审并保存
const handleAIReviewSave = async () => {
  if (aiReviewForm.selected_testcase_ids.length === 0) {
    ElMessage.warning('请先选择要评审的测试用例')
    return
  }
  
  aiReviewLoading.value = true
  try {
    const data = {
      testcase_ids: aiReviewForm.selected_testcase_ids,
      llm_config_id: aiReviewForm.llm_config_id,
      prompt_id: aiReviewForm.prompt_id,
      knowledge_ids: aiReviewForm.knowledge_ids
    }
    
    const result = await reviewStore.aiReviewTestcases(data)
    ElMessage.success(result.message || `AI评审完成，共评审 ${result.count} 条用例`)
    
    // 关闭对话框并刷新数据
    aiReviewDialogVisible.value = false
    aiReviewPreviewVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    aiReviewLoading.value = false
  }
}

// 跳转到用例管理页面
const handleGoToTestcases = () => {
  router.push('/testing/testcases')
}

// 辅助函数 - 获取用例类型标签
const getCaseTypeLabel = (type) => {
  const labels = {
    functional: '功能测试',
    ui: '界面测试',
    api: '接口测试',
    performance: '性能测试',
    security: '安全测试',
    regression: '回归测试'
  }
  return labels[type] || type
}

// 辅助函数 - 获取用例类型颜色
const getCaseTypeColor = (type) => {
  const colors = {
    functional: 'primary',
    ui: 'success',
    api: 'warning',
    performance: 'danger',
    security: 'info',
    regression: ''
  }
  return colors[type] || ''
}

// 辅助函数 - 获取优先级标签
const getPriorityLabel = (priority) => {
  const labels = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '紧急'
  }
  return labels[priority] || priority
}

// 辅助函数 - 获取优先级类型
const getPriorityType = (priority) => {
  const types = {
    low: 'info',
    medium: '',
    high: 'warning',
    critical: 'danger'
  }
  return types[priority] || ''
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="review-view">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.total }}</div>
            <div class="stat-label">总评审数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-pending">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.pending }}</div>
            <div class="stat-label">待评审</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-approved">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.approved }}</div>
            <div class="stat-label">已通过</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-rejected">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.rejected }}</div>
            <div class="stat-label">已拒绝</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-rating">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.avg_rating }}</div>
            <div class="stat-label">平均评分</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-rate">
          <div class="stat-content">
            <div class="stat-number">{{ reviewStore.stats.approval_rate }}%</div>
            <div class="stat-label">通过率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用例标题"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>评审列表</span>
          <div class="header-actions">
            <el-button type="success" @click="handleOpenAIReview">
              <el-icon><MagicStick /></el-icon>
              AI评审
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="reviewStore.reviews"
        v-loading="reviewStore.loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="testcase_title" label="测试用例" min-width="200" show-overflow-tooltip />
        <el-table-column prop="reviewer_name" label="评审人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overall_rating" label="整体评分" width="100">
          <template #default="{ row }">
            <el-rate v-model="row.overall_rating" disabled show-score />
          </template>
        </el-table-column>
        <el-table-column label="详细评分" width="120">
          <template #default="{ row }">
            <span class="avg-score">{{ getAvgScore(row) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="comments" label="评审意见" min-width="200" show-overflow-tooltip />
        <el-table-column prop="reviewed_at" label="评审时间" width="170">
          <template #default="{ row }">
            {{ row.reviewed_at?.replace('T', ' ').slice(0, 19) || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)">详情</el-button>
            <el-button type="success" link @click="handleOpenComments(row)">评论</el-button>
            <el-button type="warning" link @click="handleEditReview(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDeleteReview(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.per_page"
          :page-sizes="[20, 50, 100, 200]"
          :total="reviewStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑评审对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewDialogTitle"
      width="800px"
      destroy-on-close
    >
      <el-form
        ref="reviewFormRef"
        :model="reviewForm"
        :rules="reviewFormRules"
        label-width="100px"
      >
        <el-form-item v-if="!reviewForm.id" label="测试用例" prop="testcase_id">
          <el-select
            v-model="reviewForm.testcase_id"
            placeholder="请选择测试用例"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="tc in testcaseStore.testcases"
              :key="tc.id"
              :label="tc.title"
              :value="tc.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="评审状态" prop="status">
          <el-select v-model="reviewForm.status" style="width: 100%">
            <el-option
              v-for="opt in statusOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="整体评分">
          <el-rate v-model="reviewForm.overall_rating" show-score />
        </el-form-item>
        
        <el-divider>详细评分</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="清晰度">
              <el-rate v-model="reviewForm.clarity_score" show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="完整性">
              <el-rate v-model="reviewForm.completeness_score" show-score />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="可执行性">
              <el-rate v-model="reviewForm.feasibility_score" show-score />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="覆盖度">
              <el-rate v-model="reviewForm.coverage_score" show-score />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider>评审意见</el-divider>
        
        <el-form-item label="评审意见" prop="comments">
          <el-input
            v-model="reviewForm.comments"
            type="textarea"
            :rows="4"
            placeholder="请输入评审意见"
          />
        </el-form-item>
        
        <el-form-item label="改进建议">
          <el-input
            v-model="reviewForm.improvement_suggestions"
            type="textarea"
            :rows="3"
            placeholder="请输入改进建议（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReview">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="评审详情"
      width="700px"
    >
      <el-descriptions v-if="currentDetail" :column="2" border>
        <el-descriptions-item label="评审ID">{{ currentDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="测试用例">{{ currentDetail.testcase_title }}</el-descriptions-item>
        <el-descriptions-item label="评审人">{{ currentDetail.reviewer_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDetail.status)">
            {{ getStatusLabel(currentDetail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="整体评分">
          <el-rate v-model="currentDetail.overall_rating" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="平均评分">
          <span class="avg-score">{{ getAvgScore(currentDetail) }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="清晰度">
          <el-rate v-model="currentDetail.clarity_score" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="完整性">
          <el-rate v-model="currentDetail.completeness_score" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="可执行性">
          <el-rate v-model="currentDetail.feasibility_score" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="覆盖度">
          <el-rate v-model="currentDetail.coverage_score" disabled show-score />
        </el-descriptions-item>
        <el-descriptions-item label="评审意见" :span="2">
          <pre class="detail-pre">{{ currentDetail.comments || '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="改进建议" :span="2">
          <pre class="detail-pre">{{ currentDetail.improvement_suggestions || '-' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentDetail.created_at?.replace('T', ' ').slice(0, 19) }}
        </el-descriptions-item>
        <el-descriptions-item label="评审时间">
          {{ currentDetail.reviewed_at?.replace('T', ' ').slice(0, 19) || '-' }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEditReview(currentDetail); detailVisible = false">编辑</el-button>
      </template>
    </el-dialog>

    <!-- 评论对话框 -->
    <el-dialog
      v-model="commentDialogVisible"
      title="评审评论"
      width="600px"
    >
      <div class="comment-list">
        <div v-for="comment in commentList" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <span class="comment-user">{{ comment.user_name }}</span>
            <span class="comment-time">{{ comment.created_at?.replace('T', ' ').slice(0, 19) }}</span>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-actions">
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDeleteComment(comment.id)"
            >
              删除
            </el-button>
          </div>
        </div>
        
        <div v-if="commentList.length === 0" class="empty-comments">
          <el-empty description="暂无评论" />
        </div>
      </div>
      
      <el-divider />
      
      <div class="comment-input">
        <el-input
          v-model="newComment"
          type="textarea"
          :rows="3"
          placeholder="请输入评论内容"
        />
        <div class="comment-actions">
          <el-button type="primary" @click="handleAddComment">发送</el-button>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="commentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- AI评审对话框 -->
    <el-dialog
      v-model="aiReviewDialogVisible"
      title="AI智能评审"
      width="900px"
      destroy-on-close
    >
      <el-form label-position="top">
        <!-- 测试用例选择区域 -->
        <el-divider content-position="left">
          <el-icon><List /></el-icon>
          选择测试用例
          <span style="margin-left: 10px; color: #909399; font-size: 13px;">
            已选择 {{ aiReviewForm.selected_testcase_ids.length }} / {{ allTestcases.length }} 条
          </span>
          <el-button
            type="primary"
            link
            size="small"
            style="margin-left: 10px"
            @click="handleSelectAllTestcases"
          >
            {{ aiReviewForm.selected_testcase_ids.length === allTestcases.length ? '取消全选' : '全选' }}
          </el-button>
        </el-divider>

        <!-- 搜索框 -->
        <el-input
          v-model="testcaseSearchKeyword"
          placeholder="搜索测试用例标题"
          clearable
          @input="handleSearchTestcases"
          style="margin-bottom: 16px"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <!-- 测试用例列表 -->
        <div class="testcase-list">
          <el-empty
            v-if="allTestcases.length === 0 && !testcaseLoading"
            description="暂无测试用例"
          />
          
          <div v-if="allTestcases.length > 0" class="testcase-grid">
            <div
              v-for="tc in allTestcases"
              :key="tc.id"
              class="testcase-item"
              :class="{ selected: isTestcaseSelected(tc.id) }"
              @click="handleToggleTestcase(tc.id)"
            >
              <div class="testcase-checkbox">
                <el-checkbox
                  :model-value="isTestcaseSelected(tc.id)"
                  @click.stop
                  @change="handleToggleTestcase(tc.id)"
                />
              </div>
              
              <div class="testcase-content">
                <div class="testcase-title">{{ tc.title }}</div>
                <div class="testcase-meta">
                  <el-tag size="small" :type="getCaseTypeColor(tc.case_type)">
                    {{ getCaseTypeLabel(tc.case_type) }}
                  </el-tag>
                  <el-tag size="small" :type="getPriorityType(tc.priority)">
                    {{ getPriorityLabel(tc.priority) }}
                  </el-tag>
                  <span class="testcase-steps">
                    步骤: {{ tc.steps?.substring(0, 50) }}{{ tc.steps?.length > 50 ? '...' : '' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- AI配置区域 -->
        <el-divider content-position="left">
          <el-icon><Setting /></el-icon>
          AI配置
        </el-divider>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="大模型配置">
              <el-select
                v-model="aiReviewForm.llm_config_id"
                placeholder="选择大模型配置"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="config in llmConfigStore.allConfigs"
                  :key="config.id"
                  :label="config.name"
                  :value="config.id"
                >
                  <div class="llm-config-option">
                    <span>{{ config.name }}</span>
                    <div class="option-tags">
                      <el-tag v-if="config.is_default" type="success" size="small">默认</el-tag>
                      <el-tag type="info" size="small">{{ config.model || config.provider }}</el-tag>
                    </div>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          
          <el-col :span="12">
            <el-form-item label="提示词">
              <el-select
                v-model="aiReviewForm.prompt_id"
                placeholder="选择提示词（可选）"
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="prompt in promptStore.allPrompts"
                  :key="prompt.id"
                  :label="prompt.name"
                  :value="prompt.id"
                >
                  <div class="prompt-option">
                    <span>{{ prompt.name }}</span>
                    <el-tag v-if="prompt.is_default" type="success" size="small">默认</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="知识库">
          <el-select
            v-model="aiReviewForm.knowledge_ids"
            placeholder="选择知识库（可多选，可选）"
            multiple
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="knowledge in knowledgeStore.allKnowledges"
              :key="knowledge.id"
              :label="knowledge.name"
              :value="knowledge.id"
            >
              <div class="knowledge-option">
                <span>{{ knowledge.name }}</span>
                <el-tag type="info" size="small">{{ knowledge.category }}</el-tag>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="aiReviewDialogVisible = false">取消</el-button>
        <el-button @click="handleAIReviewPreview" :loading="aiReviewLoading" :disabled="aiReviewForm.selected_testcase_ids.length === 0">
          <el-icon><View /></el-icon>
          预览评审
        </el-button>
        <el-button type="success" @click="handleAIReviewSave" :loading="aiReviewLoading" :disabled="aiReviewForm.selected_testcase_ids.length === 0">
          <el-icon><MagicStick /></el-icon>
          开始评审
        </el-button>
      </template>
    </el-dialog>

    <!-- AI评审预览对话框 -->
    <el-dialog
      v-model="aiReviewPreviewVisible"
      title="AI评审预览"
      width="900px"
      destroy-on-close
    >
      <div class="ai-review-preview">
        <div v-if="aiReviewPreviewData.length === 0" class="empty-preview">
          <el-empty description="暂无预览数据" />
        </div>

        <div v-for="(review, index) in aiReviewPreviewData" :key="index" class="review-preview-item">
          <div class="review-header">
            <span class="review-title">{{ review.testcase_title }}</span>
            <el-tag :type="getStatusType(review.status)" size="small">
              {{ getStatusLabel(review.status) }}
            </el-tag>
          </div>

          <div class="review-scores">
            <div class="score-item">
              <span class="score-label">整体评分:</span>
              <el-rate v-model="review.overall_rating" disabled show-score />
            </div>
            <div class="score-details">
              <span class="score-detail">清晰度: {{ review.clarity_score }}</span>
              <span class="score-detail">完整性: {{ review.completeness_score }}</span>
              <span class="score-detail">可执行性: {{ review.feasibility_score }}</span>
              <span class="score-detail">覆盖度: {{ review.coverage_score }}</span>
            </div>
          </div>

          <div class="review-content">
            <div class="review-section">
              <label>评审意见:</label>
              <p>{{ review.comments }}</p>
            </div>
            <div v-if="review.improvement_suggestions" class="review-section">
              <label>改进建议:</label>
              <p>{{ review.improvement_suggestions }}</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="aiReviewPreviewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleAIReviewSave" :loading="aiReviewLoading">
          <el-icon><Check /></el-icon>
          确认保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.review-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  text-align: center;
}

.stat-card :deep(.el-card__body) {
  padding: 16px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-pending .stat-number { color: #909399; }
.stat-approved .stat-number { color: #67c23a; }
.stat-rejected .stat-number { color: #f56c6c; }
.stat-rating .stat-number { color: #e6a23c; }
.stat-rate .stat-number { color: #409eff; }

.search-card :deep(.el-card__body) {
  padding-bottom: 2px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.detail-pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: 13px;
}

.avg-score {
  font-weight: 600;
  color: #409eff;
}

.comment-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.comment-item {
  padding: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.comment-user {
  font-weight: 500;
  color: #303133;
}

.comment-time {
  font-size: 12px;
  color: #909399;
}

.comment-content {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
}

.comment-actions {
  display: flex;
  justify-content: flex-end;
}

.empty-comments {
  padding: 40px 0;
}

.comment-input .comment-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

/* AI评审相关样式 */
.llm-config-option,
.prompt-option,
.knowledge-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.option-tags {
  display: flex;
  gap: 4px;
}

.ai-review-preview {
  max-height: 600px;
  overflow-y: auto;
}

.empty-preview {
  padding: 60px 0;
}

.review-preview-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 16px;
  background-color: #fafafa;
}

.review-preview-item:last-child {
  margin-bottom: 0;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.review-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.review-scores {
  margin-bottom: 12px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.score-label {
  font-weight: 500;
  color: #606266;
}

.score-details {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.score-detail {
  font-size: 13px;
  color: #909399;
}

.review-content {
  padding-left: 8px;
}

.review-section {
  margin-bottom: 12px;
}

.review-section:last-child {
  margin-bottom: 0;
}

.review-section label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
  display: block;
  margin-bottom: 4px;
}

.review-section p {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 测试用例列表样式 */
.testcase-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background-color: #fafafa;
}

.testcase-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 12px;
}

.testcase-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.testcase-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
}

.testcase-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.testcase-checkbox {
  padding-top: 2px;
}

.testcase-content {
  flex: 1;
  min-width: 0;
}

.testcase-title {
  font-weight: 500;
  font-size: 14px;
  color: #303133;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.testcase-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.testcase-steps {
  font-size: 12px;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
}
</style>
