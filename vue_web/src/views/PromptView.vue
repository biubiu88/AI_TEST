<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePromptStore } from '@/stores/prompt'
import { UploadFilled, WarningFilled } from '@element-plus/icons-vue'

const store = usePromptStore()

// 搜索参数
const searchForm = reactive({
  keyword: '',
  category: '',
  is_active: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建提示词')
const isEdit = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  name: '',
  content: '',
  description: '',
  category: 'general',
  is_default: false,
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入提示词名称', trigger: 'blur' }],
  content: [{ required: true, message: '请输入提示词内容', trigger: 'blur' }]
}

// 分类选项
const categoryOptions = [
  { label: '通用', value: 'general' },
  { label: '功能测试', value: 'functional' },
  { label: '边界测试', value: 'boundary' },
  { label: '异常测试', value: 'exception' },
  { label: '性能测试', value: 'performance' }
]

// 加载数据
const loadData = async () => {
  await store.fetchPrompts(searchForm)
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  loadData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.category = ''
  searchForm.is_active = ''
  searchForm.page = 1
  loadData()
}

// 分页变化
const handlePageChange = (page) => {
  searchForm.page = page
  loadData()
}

// 每页条数变化
const handleSizeChange = (size) => {
  searchForm.per_page = size
  searchForm.page = 1
  loadData()
}

// 新建提示词
const handleAdd = () => {
  dialogTitle.value = '新建提示词'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑提示词
const handleEdit = (row) => {
  dialogTitle.value = '编辑提示词'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除提示词
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除提示词"${row.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await store.deletePrompt(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 设置默认提示词
const handleSetDefault = async (row) => {
  try {
    await store.setDefaultPrompt(row.id)
    ElMessage.success('设置成功')
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.content = ''
  formData.description = ''
  formData.category = 'general'
  formData.is_default = false
  formData.is_active = true
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await store.updatePrompt(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await store.createPrompt(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 获取分类标签
const getCategoryLabel = (category) => {
  const labels = {
    general: '通用',
    functional: '功能测试',
    boundary: '边界测试',
    exception: '异常测试',
    performance: '性能测试'
  }
  return labels[category] || category
}

// 获取分类标签类型
const getCategoryType = (category) => {
  const types = {
    general: '',
    functional: 'success',
    boundary: 'warning',
    exception: 'danger',
    performance: 'info'
  }
  return types[category] || ''
}

// 导入导出相关
const importVisible = ref(false)
const importLoading = ref(false)
const importFile = ref(null)
const uploadRef = ref(null)
const importResult = ref(null)

// 下载模板
const handleDownloadTemplate = async () => {
  try {
    const blob = await store.downloadTemplate()
    downloadFile(blob, '提示词导入模板.xlsx')
    ElMessage.success('模板下载成功')
  } catch (e) {
    ElMessage.error('下载模板失败')
  }
}

// 导出数据
const handleExport = async () => {
  try {
    const blob = await store.exportPrompts()
    downloadFile(blob, `提示词_${new Date().toISOString().slice(0, 10)}.xlsx`)
    ElMessage.success('导出成功')
  } catch (e) {
    ElMessage.error('导出失败')
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
    const result = await store.importPrompts(importFile.value)
    importResult.value = result.data || result
    ElMessage.success(result.message || '导入成功')
    loadData()
  } catch (e) {
    ElMessage.error('导入失败')
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

// 下载文件工具函数
const downloadFile = (blob, filename) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="prompt-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索名称或描述"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="全部" clearable>
            <el-option
              v-for="opt in categoryOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部" clearable>
            <el-option label="启用" value="true" />
            <el-option label="禁用" value="false" />
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

    <!-- 操作栏 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>提示词列表</span>
          <div class="header-actions">
            <el-button @click="handleDownloadTemplate">
              <el-icon><Download /></el-icon>
              下载模板
            </el-button>
            <el-button type="info" @click="handleOpenImport">
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新建提示词
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="store.prompts"
        v-loading="store.loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            <span>{{ row.name }}</span>
            <el-tag v-if="row.is_default" type="success" size="small" style="margin-left: 8px">默认</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ row.created_at?.replace('T', ' ').slice(0, 19) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button v-if="!row.is_default" type="success" link @click="handleSetDefault(row)">设为默认</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="searchForm.page"
          v-model:page-size="searchForm.per_page"
          :page-sizes="[50, 100, 500, 1000]"
          :total="store.total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <!-- 导入对话框 -->
    <el-dialog
      v-model="importVisible"
      title="导入提示词"
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
            <el-tag type="success">成功: {{ importResult.success_count || importResult.imported || 0 }} 条</el-tag>
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

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入提示词名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" placeholder="请输入提示词描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="formData.category" style="width: 100%">
                <el-option
                  v-for="opt in categoryOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="默认" prop="is_default">
              <el-switch v-model="formData.is_default" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="启用" prop="is_active">
              <el-switch v-model="formData.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="12"
            placeholder="请输入提示词内容，这将作为AI生成测试用例时的系统提示词..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.prompt-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  margin-bottom: 0;
}

.search-card :deep(.el-card__body) {
  padding-bottom: 2px;
}

.table-card {
  flex: 1;
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
