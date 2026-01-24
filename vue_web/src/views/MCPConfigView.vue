<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { mcpApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  keyword: '',
  status: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建MCP配置')
const isEdit = ref(false)
const formRef = ref(null)

// 测试对话框
const testDialogVisible = ref(false)
const testResult = ref(null)
const testingConfig = ref(null)

const formData = reactive({
  id: null,
  name: '',
  server_url: '',
  server_name: '',
  description: '',
  timeout: 30,
  max_retries: 3,
  status: 1,
  is_default: false,
  extra_params: ''
})

const formRules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  server_url: [{ required: true, message: '请输入服务器地址', trigger: 'blur' }],
  server_name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }]
}

// 状态选项
const statusOptions = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 }
]

// MCP配置列表
const mcpList = ref([])
const total = ref(0)
const loading = ref(false)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await mcpApi.getList(searchForm)
    mcpList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('获取MCP配置列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  searchForm.page = 1
  loadData()
}

// 重置搜索
const handleReset = () => {
  searchForm.keyword = ''
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

// 新建配置
const handleAdd = () => {
  dialogTitle.value = '新建MCP配置'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑配置
const handleEdit = (row) => {
  dialogTitle.value = '编辑MCP配置'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除配置
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除MCP配置"${row.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await mcpApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 设置默认配置
const handleSetDefault = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要将"${row.name}"设置为默认配置吗？`,
      '提示',
      { type: 'warning' }
    )
    await mcpApi.update(row.id, { is_default: true })
    ElMessage.success('设置成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 测试连接
const handleTest = async (row) => {
  testingConfig.value = row
  testResult.value = null
  testDialogVisible.value = true
  
  try {
    const res = await mcpApi.test(row.id)
    testResult.value = {
      success: true,
      ...res.data
    }
  } catch (error) {
    testResult.value = {
      success: false,
      error: error.message || '连接失败'
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.server_url = ''
  formData.server_name = ''
  formData.description = ''
  formData.timeout = 30
  formData.max_retries = 3
  formData.status = 1
  formData.is_default = false
  formData.extra_params = ''
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const submitData = {
      name: formData.name,
      server_url: formData.server_url,
      server_name: formData.server_name,
      description: formData.description,
      timeout: formData.timeout,
      max_retries: formData.max_retries,
      status: formData.status,
      is_default: formData.is_default,
      extra_params: formData.extra_params
    }
    
    if (isEdit.value) {
      await mcpApi.update(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await mcpApi.create(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 获取状态标签
const getStatusLabel = (status) => {
  return status === 1 ? '启用' : '禁用'
}

// 获取状态标签样式
const getStatusType = (status) => {
  return status === 1 ? 'success' : 'info'
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="mcp-config-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索配置名称或描述"
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

    <!-- 操作栏 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>MCP配置列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建配置
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="mcpList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="配置名称" min-width="150" />
        <el-table-column prop="server_name" label="服务器名称" width="120" />
        <el-table-column prop="server_url" label="服务器地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="timeout" label="超时" width="80" align="center">
          <template #default="{ row }">
            {{ row.timeout }}s
          </template>
        </el-table-column>
        <el-table-column prop="max_retries" label="重试" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_default" label="默认" width="80" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_default" type="warning" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleTest(row)">测试</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button 
              type="success" 
              link 
              @click="handleSetDefault(row)"
              v-if="!row.is_default"
            >
              设为默认
            </el-button>
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
          :total="total"
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
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配置名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入配置名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="服务器名称" prop="server_name">
              <el-input v-model="formData.server_name" placeholder="例如: filesystem" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="服务器地址" prop="server_url">
          <el-input v-model="formData.server_url" placeholder="例如: http://localhost:3000" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="超时时间" prop="timeout">
              <el-input-number v-model="formData.timeout" :min="1" :max="300" style="width: 100%">
                <template #append>秒</template>
              </el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最大重试" prop="max_retries">
              <el-input-number v-model="formData.max_retries" :min="0" :max="10" style="width: 100%" />
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

        <el-form-item label="额外参数" prop="extra_params">
          <el-input
            v-model="formData.extra_params"
            type="textarea"
            :rows="3"
            placeholder='JSON格式，例如: {"allowed_paths": ["/tmp"]}'
          />
        </el-form-item>

        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 测试连接对话框 -->
    <el-dialog
      v-model="testDialogVisible"
      title="测试MCP连接"
      width="500px"
      destroy-on-close
    >
      <div v-if="testingConfig" class="test-info">
        <p><strong>配置名称：</strong>{{ testingConfig.name }}</p>
        <p><strong>服务器名称：</strong>{{ testingConfig.server_name }}</p>
        <p><strong>服务器地址：</strong>{{ testingConfig.server_url }}</p>
      </div>
      
      <div v-if="testResult" class="test-result">
        <el-result
          :icon="testResult.success ? 'success' : 'error'"
          :title="testResult.success ? '连接成功' : '连接失败'"
          :sub-title="testResult.success ? `响应时间: ${testResult.response_time}` : testResult.error"
        />
      </div>
      
      <template #footer>
        <el-button @click="testDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.mcp-config-view {
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

.test-info {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.test-info p {
  margin: 5px 0;
}

.test-result {
  margin-top: 20px;
}
</style>
