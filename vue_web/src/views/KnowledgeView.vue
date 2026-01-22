<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useKnowledgeStore } from '@/stores/knowledge'

const store = useKnowledgeStore()

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
const dialogTitle = ref('新建知识库')
const isEdit = ref(false)
const formRef = ref(null)

// 预览对话框
const previewVisible = ref(false)
const previewContent = ref('')
const previewTitle = ref('')

const formData = reactive({
  id: null,
  name: '',
  content: '',
  description: '',
  category: 'general',
  file_type: 'text',
  is_active: true
})

const formRules = {
  name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }],
  content: [{ required: true, message: '请输入知识库内容', trigger: 'blur' }]
}

// 分类选项
const categoryOptions = [
  { label: '通用', value: 'general' },
  { label: '领域知识', value: 'domain' },
  { label: 'API文档', value: 'api' },
  { label: 'UI规范', value: 'ui' },
  { label: '数据库', value: 'database' }
]

// 文件类型选项
const fileTypeOptions = [
  { label: '纯文本', value: 'text' },
  { label: 'Markdown', value: 'markdown' },
  { label: 'JSON', value: 'json' }
]

// 加载数据
const loadData = async () => {
  await store.fetchKnowledges(searchForm)
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

// 新建知识库
const handleAdd = () => {
  dialogTitle.value = '新建知识库'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑知识库
const handleEdit = (row) => {
  dialogTitle.value = '编辑知识库'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 预览知识库
const handlePreview = (row) => {
  previewTitle.value = row.name
  previewContent.value = row.content
  previewVisible.value = true
}

// 删除知识库
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除知识库"${row.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await store.deleteKnowledge(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.content = ''
  formData.description = ''
  formData.category = 'general'
  formData.file_type = 'text'
  formData.is_active = true
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await store.updateKnowledge(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await store.createKnowledge(formData)
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
    domain: '领域知识',
    api: 'API文档',
    ui: 'UI规范',
    database: '数据库'
  }
  return labels[category] || category
}

// 获取分类标签类型
const getCategoryType = (category) => {
  const types = {
    general: '',
    domain: 'success',
    api: 'warning',
    ui: 'info',
    database: 'danger'
  }
  return types[category] || ''
}

// 获取文件类型标签
const getFileTypeLabel = (type) => {
  const labels = {
    text: '纯文本',
    markdown: 'Markdown',
    json: 'JSON'
  }
  return labels[type] || type
}

// 计算内容长度
const getContentLength = (content) => {
  if (!content) return '0 字'
  const len = content.length
  if (len > 1000) {
    return `${(len / 1000).toFixed(1)}K 字`
  }
  return `${len} 字`
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="knowledge-view">
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
          <span>知识库列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建知识库
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="store.knowledges"
        v-loading="store.loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag :type="getCategoryType(row.category)" size="small">
              {{ getCategoryLabel(row.category) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_type" label="类型" width="90">
          <template #default="{ row }">
            {{ getFileTypeLabel(row.file_type) }}
          </template>
        </el-table-column>
        <el-table-column label="内容长度" width="100">
          <template #default="{ row }">
            {{ getContentLength(row.content) }}
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
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="info" link @click="handlePreview(row)">预览</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
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

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入知识库名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" placeholder="请输入知识库描述" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
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
          <el-col :span="8">
            <el-form-item label="类型" prop="file_type">
              <el-select v-model="formData.file_type" style="width: 100%">
                <el-option
                  v-for="opt in fileTypeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="启用" prop="is_active">
              <el-switch v-model="formData.is_active" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="15"
            placeholder="请输入知识库内容，这些内容会作为参考知识提供给AI生成测试用例..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      :title="previewTitle"
      width="700px"
    >
      <div class="preview-content">
        {{ previewContent }}
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.knowledge-view {
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

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.6;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
