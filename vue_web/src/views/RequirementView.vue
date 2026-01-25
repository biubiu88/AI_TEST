<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRequirementStore } from '@/stores/requirement'
import { useRouter } from 'vue-router'

const router = useRouter()
const store = useRequirementStore()

// 搜索参数
const searchForm = reactive({
  keyword: '',
  module: '',
  status: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建需求')
const isEdit = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  title: '',
  content: '',
  module: '',
  priority: 'medium',
  status: 'pending'
})

const formRules = {
  title: [{ required: true, message: '请输入需求标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入需求内容', trigger: 'blur' }]
}

// 状态选项
const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' }
]

const priorityOptions = [
  { label: '高', value: 'high' },
  { label: '中', value: 'medium' },
  { label: '低', value: 'low' }
]

// 加载数据
const loadData = async () => {
  await store.fetchRequirements(searchForm)
  await store.fetchModules()
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  loadData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.module = ''
  searchForm.status = ''
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

// 新建需求
const handleAdd = () => {
  dialogTitle.value = '新建需求'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑需求
const handleEdit = (row) => {
  dialogTitle.value = '编辑需求'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除需求
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除需求"${row.title}"吗？关联的测试用例也会被删除。`,
      '提示',
      { type: 'warning' }
    )
    await store.deleteRequirement(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 生成测试用例
const handleGenerate = (row) => {
  router.push({
    path: '/testing/generate',
    query: { requirementId: row.id }
  })
}

// 查看测试用例
const handleViewTestcases = (row) => {
  router.push({
    path: '/testing/testcases',
    query: { requirementId: row.id }
  })
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.title = ''
  formData.content = ''
  formData.module = ''
  formData.priority = 'medium'
  formData.status = 'pending'
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    if (isEdit.value) {
      await store.updateRequirement(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await store.createRequirement(formData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 获取状态标签类型
const getStatusType = (status) => {
  const types = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  const labels = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成'
  }
  return labels[status] || status
}

// 获取优先级标签类型
const getPriorityType = (priority) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

// 获取优先级标签
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
  <div class="requirement-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索标题或内容"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="全部" clearable>
            <el-option
              v-for="m in store.modules"
              :key="m"
              :label="m"
              :value="m"
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
          <span>需求列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建需求
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="store.requirements"
        v-loading="store.loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="title" label="需求标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="module" label="模块" width="120" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="testcase_count" label="用例数" width="80" />
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ row.created_at?.replace('T', ' ').slice(0, 19) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleGenerate(row)">生成用例</el-button>
            <el-button type="info" link @click="handleViewTestcases(row)">查看用例</el-button>
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
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入需求标题" />
        </el-form-item>
        <el-form-item label="模块" prop="module">
          <el-input v-model="formData.module" placeholder="请输入所属模块" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
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
          <el-col :span="12">
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
        <el-form-item label="内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="10"
            placeholder="请输入需求详细内容..."
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
.requirement-view {
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
</style>
