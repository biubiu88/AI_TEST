<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useTestcaseStore } from '@/stores/testcase'
import { useRequirementStore } from '@/stores/requirement'
import { testcaseApi } from '@/api'

const route = useRoute()
const router = useRouter()
const testcaseStore = useTestcaseStore()
const requirementStore = useRequirementStore()

// 搜索参数
const searchForm = reactive({
  keyword: '',
  requirement_id: route.query.requirementId ? Number(route.query.requirementId) : '',
  case_type: '',
  status: '',
  is_ai_generated: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建测试用例')
const isEdit = ref(false)
const formRef = ref(null)

// 详情对话框
const detailVisible = ref(false)
const currentDetail = ref(null)

// 导入对话框
const importVisible = ref(false)
const importLoading = ref(false)
const importFile = ref(null)
const uploadRef = ref(null)
const importResult = ref(null)

const formData = reactive({
  id: null,
  requirement_id: '',
  title: '',
  precondition: '',
  steps: '',
  expected_result: '',
  case_type: 'functional',
  priority: 'medium',
  status: 'pending'
})

const formRules = {
  requirement_id: [{ required: true, message: '请选择关联需求', trigger: 'change' }],
  title: [{ required: true, message: '请输入用例标题', trigger: 'blur' }],
  steps: [{ required: true, message: '请输入测试步骤', trigger: 'blur' }],
  expected_result: [{ required: true, message: '请输入预期结果', trigger: 'blur' }]
}

// 选项配置
const caseTypeOptions = [
  { label: '功能测试', value: 'functional' },
  { label: '边界测试', value: 'boundary' },
  { label: '异常测试', value: 'exception' },
  { label: '性能测试', value: 'performance' }
]

const statusOptions = [
  { label: '待执行', value: 'pending' },
  { label: '通过', value: 'passed' },
  { label: '失败', value: 'failed' },
  { label: '阻塞', value: 'blocked' }
]

const priorityOptions = [
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' }
]

const aiOptions = [
  { label: 'AI生成', value: 'true' },
  { label: '手动创建', value: 'false' }
]

// 加载数据
const loadData = async () => {
  await testcaseStore.fetchTestcases(searchForm)
  await testcaseStore.fetchStats()
  await requirementStore.fetchRequirements({ per_page: 1000 })
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  testcaseStore.fetchTestcases(searchForm)
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.requirement_id = ''
  searchForm.case_type = ''
  searchForm.status = ''
  searchForm.is_ai_generated = ''
  searchForm.page = 1
  testcaseStore.fetchTestcases(searchForm)
}

// 分页变化
const handlePageChange = (page) => {
  searchForm.page = page
  testcaseStore.fetchTestcases(searchForm)
}

// 每页条数变化
const handleSizeChange = (size) => {
  searchForm.per_page = size
  searchForm.page = 1
  testcaseStore.fetchTestcases(searchForm)
}

// 新建用例
const handleAdd = () => {
  dialogTitle.value = '新建测试用例'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑用例
const handleEdit = (row) => {
  dialogTitle.value = '编辑测试用例'
  isEdit.value = true
  Object.assign(formData, {
    id: row.id,
    requirement_id: row.requirement_id,
    title: row.title,
    precondition: row.precondition || '',
    steps: row.steps,
    expected_result: row.expected_result,
    case_type: row.case_type,
    priority: row.priority,
    status: row.status
  })
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}

// 删除用例
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除测试用例"${row.title}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await testcaseStore.deleteTestcase(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 更新状态
const handleStatusChange = async (row, status) => {
  try {
    await testcaseStore.updateTestcase(row.id, { status })
    ElMessage.success('状态更新成功')
    testcaseStore.fetchStats()
  } catch (e) {
    console.error(e)
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.requirement_id = searchForm.requirement_id || ''
  formData.title = ''
  formData.precondition = ''
  formData.steps = ''
  formData.expected_result = ''
  formData.case_type = 'functional'
  formData.priority = 'medium'
  formData.status = 'pending'
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await testcaseStore.updateTestcase(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await testcaseStore.createTestcase(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 跳转生成页面
const handleGoGenerate = () => {
  router.push('/testing/generate')
}

// 跳转AI评审页面
const handleGoAIReview = () => {
  router.push('/testing/reviews')
}

// 导出测试用例
const exportLoading = ref(false)
const handleExport = async () => {
  exportLoading.value = true
  try {
    const response = await testcaseApi.export(searchForm)
    // 创建下载链接
    const blob = new Blob([response], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `测试用例_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出失败')
  } finally {
    exportLoading.value = false
  }
}

// 下载导入模板
const handleDownloadTemplate = async () => {
  try {
    const response = await testcaseApi.downloadTemplate()
    const blob = new Blob([response], { 
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '测试用例导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (e) {
    console.error(e)
    ElMessage.error('模板下载失败')
  }
}

// 打开导入对话框
const handleOpenImport = () => {
  importFile.value = null
  importResult.value = null
  importVisible.value = true
}

// 文件选择变化
const handleFileChange = (file) => {
  importFile.value = file.raw
}

// 执行导入
const handleImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  importLoading.value = true
  try {
    const result = await testcaseApi.import(importFile.value)
    importResult.value = result.data
    ElMessage.success(result.message)
    loadData()
  } catch (e) {
    console.error(e)
  } finally {
    importLoading.value = false
  }
}

// 关闭导入对话框
const handleCloseImport = () => {
  importVisible.value = false
  importFile.value = null
  importResult.value = null
}

// 获取标签类型
const getCaseTypeLabel = (type) => {
  const labels = {
    functional: '功能',
    boundary: '边界',
    exception: '异常',
    performance: '性能'
  }
  return labels[type] || type
}

const getCaseTypeColor = (type) => {
  const colors = {
    functional: '#409eff',
    boundary: '#e6a23c',
    exception: '#f56c6c',
    performance: '#67c23a'
  }
  return colors[type] || '#909399'
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    passed: 'success',
    failed: 'danger',
    blocked: 'warning'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    pending: '待执行',
    passed: '通过',
    failed: '失败',
    blocked: '阻塞'
  }
  return labels[status] || status
}

const getPriorityType = (priority) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

const getPriorityLabel = (priority) => {
  const labels = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return labels[priority] || priority
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="testcase-view">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.total }}</div>
            <div class="stat-label">总用例数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-passed">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.passed }}</div>
            <div class="stat-label">已通过</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-failed">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.failed }}</div>
            <div class="stat-label">已失败</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-pending">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.pending }}</div>
            <div class="stat-label">待执行</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-ai">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.ai_generated }}</div>
            <div class="stat-label">AI生成</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="4">
        <el-card shadow="hover" class="stat-card stat-rate">
          <div class="stat-content">
            <div class="stat-number">{{ testcaseStore.stats.pass_rate }}%</div>
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
            placeholder="搜索标题或步骤"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="关联需求">
          <el-select v-model="searchForm.requirement_id" placeholder="全部" clearable filterable>
            <el-option
              v-for="req in requirementStore.requirements"
              :key="req.id"
              :label="req.title"
              :value="req.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.case_type" placeholder="全部" clearable>
            <el-option
              v-for="opt in caseTypeOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
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
        <el-form-item label="来源">
          <el-select v-model="searchForm.is_ai_generated" placeholder="全部" clearable>
            <el-option
              v-for="opt in aiOptions"
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
          <span>测试用例列表</span>
          <div class="header-actions">
            <el-button @click="handleDownloadTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="info" @click="handleOpenImport">
              <el-icon><Upload /></el-icon>
              导入用例
            </el-button>
            <el-button type="warning" :loading="exportLoading" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出用例
            </el-button>
            <el-button type="success" @click="handleGoGenerate">
              <el-icon><MagicStick /></el-icon>
              AI生成
            </el-button>
            <el-button type="primary" @click="handleGoAIReview">
              <el-icon><MagicStick /></el-icon>
              AI评审
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新建用例
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="testcaseStore.testcases"
        v-loading="testcaseStore.loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="用例标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="requirement_title" label="关联需求" width="150" show-overflow-tooltip />
        <el-table-column prop="case_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag 
              size="small" 
              :style="{ backgroundColor: getCaseTypeColor(row.case_type), color: '#fff', border: 'none' }"
            >
              {{ getCaseTypeLabel(row.case_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-dropdown trigger="click" @command="(cmd) => handleStatusChange(row, cmd)">
              <el-tag :type="getStatusType(row.status)" size="small" style="cursor: pointer">
                {{ getStatusLabel(row.status) }}
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-tag>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item
                    v-for="opt in statusOptions"
                    :key="opt.value"
                    :command="opt.value"
                    :disabled="opt.value === row.status"
                  >
                    {{ opt.label }}
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
        <el-table-column prop="is_ai_generated" label="来源" width="80">
          <template #default="{ row }">
            <el-tag v-if="row.is_ai_generated" type="success" size="small">AI</el-tag>
            <el-tag v-else type="info" size="small">手动</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ row.created_at?.replace('T', ' ').slice(0, 19) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">详情</el-button>
            <el-button type="warning" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.per_page"
          :page-sizes="[50, 100, 500, 1000]"
          :total="testcaseStore.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="750px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
      >
        <el-form-item label="关联需求" prop="requirement_id">
          <el-select 
            v-model="formData.requirement_id" 
            placeholder="请选择关联需求"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="req in requirementStore.requirements"
              :key="req.id"
              :label="req.title"
              :value="req.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="用例标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入用例标题" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="类型" prop="case_type">
              <el-select v-model="formData.case_type" style="width: 100%">
                <el-option
                  v-for="opt in caseTypeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option
                  v-for="opt in priorityOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option
                  v-for="opt in statusOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="前置条件" prop="precondition">
          <el-input
            v-model="formData.precondition"
            type="textarea"
            :rows="2"
            placeholder="请输入前置条件"
          />
        </el-form-item>
        <el-form-item label="测试步骤" prop="steps">
          <el-input
            v-model="formData.steps"
            type="textarea"
            :rows="4"
            placeholder="请输入测试步骤"
          />
        </el-form-item>
        <el-form-item label="预期结果" prop="expected_result">
          <el-input
            v-model="formData.expected_result"
            type="textarea"
            :rows="3"
            placeholder="请输入预期结果"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="测试用例详情"
      width="700px"
    >
      <el-descriptions v-if="currentDetail" :column="2" border>
        <el-descriptions-item label="用例ID">{{ currentDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="关联需求">{{ currentDetail.requirement_title }}</el-descriptions-item>
        <el-descriptions-item label="用例标题" :span="2">{{ currentDetail.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :style="{ backgroundColor: getCaseTypeColor(currentDetail.case_type), color: '#fff' }">
            {{ getCaseTypeLabel(currentDetail.case_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(currentDetail.priority)">
            {{ getPriorityLabel(currentDetail.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentDetail.status)">
            {{ getStatusLabel(currentDetail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="来源">
          <el-tag :type="currentDetail.is_ai_generated ? 'success' : 'info'">
            {{ currentDetail.is_ai_generated ? 'AI生成' : '手动创建' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="前置条件" :span="2">
          <pre class="detail-pre">{{ currentDetail.precondition || '无' }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="测试步骤" :span="2">
          <pre class="detail-pre">{{ currentDetail.steps }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果" :span="2">
          <pre class="detail-pre">{{ currentDetail.expected_result }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentDetail.created_at?.replace('T', ' ').slice(0, 19) }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ currentDetail.updated_at?.replace('T', ' ').slice(0, 19) }}
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleEdit(currentDetail); detailVisible = false">编辑</el-button>
      </template>
    </el-dialog>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importVisible"
      title="导入测试用例"
      width="550px"
      :close-on-click-modal="false"
      @close="handleCloseImport"
    >
      <div class="import-content">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 16px"
        >
          <template #title>
            请先<el-link type="primary" @click="handleDownloadTemplate">下载导入模板</el-link>，按照模板格式填写数据后再上传
          </template>
        </el-alert>
        
        <el-upload
          ref="uploadRef"
          class="import-upload"
          drag
          :auto-upload="false"
          :limit="1"
          accept=".xlsx,.xls"
          :on-change="handleFileChange"
          :on-exceed="() => ElMessage.warning('只能上传一个文件')"
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">只支持 .xlsx 或 .xls 格式的 Excel 文件</div>
          </template>
        </el-upload>
        
        <!-- 导入结果 -->
        <div v-if="importResult" class="import-result">
          <el-divider>导入结果</el-divider>
          <div class="result-summary">
            <el-tag type="success">成功: {{ importResult.success_count }} 条</el-tag>
            <el-tag v-if="importResult.errors?.length" type="danger" style="margin-left: 8px">
              失败: {{ importResult.errors.length }} 条
            </el-tag>
          </div>
          <div v-if="importResult.errors?.length" class="error-list">
            <div v-for="(error, index) in importResult.errors" :key="index" class="error-item">
              <el-icon color="#f56c6c"><WarningFilled /></el-icon>
              {{ error }}
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="handleCloseImport">关闭</el-button>
        <el-button type="primary" :loading="importLoading" @click="handleImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.testcase-view {
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

.stat-passed .stat-number { color: #67c23a; }
.stat-failed .stat-number { color: #f56c6c; }
.stat-pending .stat-number { color: #909399; }
.stat-ai .stat-number { color: #409eff; }
.stat-rate .stat-number { color: #e6a23c; }

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
}

.import-content {
  padding: 0 10px;
}

.import-upload {
  width: 100%;
}

.import-upload :deep(.el-upload-dragger) {
  width: 100%;
}

.import-result {
  margin-top: 16px;
}

.result-summary {
  margin-bottom: 12px;
}

.error-list {
  max-height: 200px;
  overflow-y: auto;
  background-color: #fef0f0;
  border-radius: 4px;
  padding: 12px;
}

.error-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 13px;
  color: #f56c6c;
}
</style>
