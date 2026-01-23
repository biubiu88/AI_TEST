<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLLMConfigStore } from '@/stores/llmConfig'

const llmConfigStore = useLLMConfigStore()

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增配置')
const editingId = ref(null)

// 表单
const formRef = ref(null)
const form = reactive({
  name: '',
  provider: 'openai',
  api_base: '',
  api_key: '',
  model: '',
  description: '',
  is_default: false,
  is_active: true
})

// 表单规则
const rules = {
  name: [{ required: true, message: '请输入配置名称', trigger: 'blur' }],
  provider: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  api_base: [{ required: true, message: '请输入API地址', trigger: 'blur' }],
  api_key: [{ required: true, message: '请输入API密钥', trigger: 'blur' }]
}

// 测试状态
const testing = ref(false)
const testResult = ref(null)

// 计算属性
const providerOptions = computed(() => {
  return Object.entries(llmConfigStore.providers).map(([key, value]) => ({
    value: key,
    label: value.name,
    api_base: value.api_base,
    description: value.description
  }))
})

const currentProvider = computed(() => {
  return llmConfigStore.providers[form.provider] || {}
})

// 监听供应商变化，自动填充API地址
watch(() => form.provider, (newProvider) => {
  const provider = llmConfigStore.providers[newProvider]
  if (provider && provider.api_base && !editingId.value) {
    form.api_base = provider.api_base
  }
  // 清空模型选择
  form.model = ''
  llmConfigStore.availableModels = []
})

// 初始化
onMounted(async () => {
  await llmConfigStore.fetchProviders()
  await loadConfigs()
})

// 加载配置列表
const loadConfigs = async () => {
  await llmConfigStore.fetchConfigs(pagination)
}

// 分页变化
const handlePageChange = (page) => {
  pagination.page = page
  loadConfigs()
}

// 新增配置
const handleAdd = () => {
  editingId.value = null
  dialogTitle.value = '新增配置'
  resetForm()
  dialogVisible.value = true
}

// 编辑配置
const handleEdit = async (row) => {
  editingId.value = row.id
  dialogTitle.value = '编辑配置'
  
  Object.assign(form, {
    name: row.name,
    provider: row.provider,
    api_base: row.api_base,
    api_key: '', // 不回显密钥
    model: row.model || '',
    description: row.description || '',
    is_default: row.is_default,
    is_active: row.is_active
  })
  
  testResult.value = null
  dialogVisible.value = true
}

// 删除配置
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除配置 "${row.name}" 吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await llmConfigStore.deleteConfig(row.id)
    ElMessage.success('删除成功')
    loadConfigs()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 设置默认
const handleSetDefault = async (row) => {
  try {
    await llmConfigStore.setDefaultConfig(row.id)
    ElMessage.success('设置成功')
    loadConfigs()
  } catch (e) {
    console.error(e)
  }
}

// 重置表单
const resetForm = () => {
  Object.assign(form, {
    name: '',
    provider: 'openai',
    api_base: llmConfigStore.providers['openai']?.api_base || '',
    api_key: '',
    model: '',
    description: '',
    is_default: false,
    is_active: true
  })
  testResult.value = null
  llmConfigStore.availableModels = []
  formRef.value?.clearValidate()
}

// 获取模型列表
const handleFetchModels = async () => {
  if (!form.api_base || !form.api_key) {
    ElMessage.warning('请先填写API地址和密钥')
    return
  }
  
  try {
    await llmConfigStore.fetchAvailableModels(form.api_base, form.api_key)
    ElMessage.success(`获取到 ${llmConfigStore.availableModels.length} 个模型`)
  } catch (e) {
    ElMessage.error('获取模型列表失败，请检查API地址和密钥')
  }
}

// 测试连接
const handleTest = async () => {
  if (!form.api_base || !form.api_key) {
    ElMessage.warning('请先填写API地址和密钥')
    return
  }
  
  testing.value = true
  testResult.value = null
  
  try {
    const result = await llmConfigStore.testConfig({
      api_base: form.api_base,
      api_key: form.api_key,
      model: form.model
    })
    testResult.value = {
      success: true,
      model: result.model,
      usage: result.usage
    }
    ElMessage.success('连接测试成功')
  } catch (e) {
    testResult.value = {
      success: false,
      error: e.message || '连接失败'
    }
    ElMessage.error('连接测试失败')
  } finally {
    testing.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const data = { ...form }
    
    // 编辑时如果没有填写新密钥，删除该字段
    if (editingId.value && !data.api_key) {
      delete data.api_key
    }
    
    if (editingId.value) {
      await llmConfigStore.updateConfig(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await llmConfigStore.createConfig(data)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadConfigs()
  } catch (e) {
    console.error(e)
  }
}

// 获取供应商标签颜色
const getProviderColor = (provider) => {
  const colors = {
    openai: '#74aa9c',
    azure: '#0078d4',
    anthropic: '#d4a574',
    qwen: '#ff6a00',
    zhipu: '#4f46e5',
    moonshot: '#6366f1',
    deepseek: '#3b82f6',
    doubao: '#10b981',
    baichuan: '#ec4899',
    minimax: '#8b5cf6',
    ollama: '#64748b',
    custom: '#6b7280'
  }
  return colors[provider] || '#6b7280'
}

// 获取供应商名称
const getProviderName = (provider) => {
  return llmConfigStore.providers[provider]?.name || provider
}
</script>

<template>
  <div class="llm-config-view">
    <!-- 顶部操作栏 -->
    <el-card class="header-card">
      <div class="header-content">
        <div class="header-info">
          <h3>大模型配置</h3>
          <p>管理AI大模型的API配置，支持OpenAI、Claude、通义千问、智谱等主流大模型</p>
        </div>
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增配置
        </el-button>
      </div>
    </el-card>

    <!-- 配置列表 -->
    <el-card class="list-card">
      <el-table
        :data="llmConfigStore.configs"
        v-loading="llmConfigStore.loading"
        stripe
      >
        <el-table-column label="配置名称" min-width="150">
          <template #default="{ row }">
            <div class="config-name">
              <span>{{ row.name }}</span>
              <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="供应商" width="140">
          <template #default="{ row }">
            <el-tag 
              :style="{ backgroundColor: getProviderColor(row.provider), color: '#fff', border: 'none' }"
            >
              {{ getProviderName(row.provider) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="模型" prop="model" min-width="180">
          <template #default="{ row }">
            <span>{{ row.model || '-' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="API地址" prop="api_base" min-width="250" show-overflow-tooltip />
        
        <el-table-column label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
              {{ row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="!row.is_default"
              type="primary"
              link
              size="small"
              @click="handleSetDefault(row)"
            >
              设为默认
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          :page-size="pagination.per_page"
          :total="llmConfigStore.total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="配置名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入配置名称，如：GPT-4配置" />
        </el-form-item>

        <el-form-item label="供应商" prop="provider">
          <el-select v-model="form.provider" placeholder="请选择供应商" style="width: 100%">
            <el-option
              v-for="item in providerOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            >
              <div class="provider-option">
                <span>{{ item.label }}</span>
                <span class="provider-desc">{{ item.description }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item label="API地址" prop="api_base">
          <el-input v-model="form.api_base" placeholder="请输入API基础地址">
            <template #append>
              <el-tooltip content="不同供应商的API地址不同，请参考官方文档">
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            :placeholder="editingId ? '留空则保持原密钥不变' : '请输入API密钥'"
          />
        </el-form-item>

        <el-form-item label="模型">
          <div class="model-select">
            <el-select
              v-model="form.model"
              placeholder="选择或输入模型名称"
              filterable
              allow-create
              clearable
              style="flex: 1"
              :loading="llmConfigStore.modelsLoading"
            >
              <el-option
                v-for="model in llmConfigStore.availableModels"
                :key="model.id"
                :label="model.name"
                :value="model.id"
              />
            </el-select>
            <el-button
              type="primary"
              :loading="llmConfigStore.modelsLoading"
              @click="handleFetchModels"
            >
              获取模型
            </el-button>
          </div>
          <div class="form-tip">点击"获取模型"按钮从API获取可用模型列表，或直接输入模型名称</div>
        </el-form-item>

        <el-form-item label="描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="配置描述（可选）"
          />
        </el-form-item>

        <el-form-item label="设置">
          <el-checkbox v-model="form.is_default">设为默认配置</el-checkbox>
          <el-checkbox v-model="form.is_active">启用</el-checkbox>
        </el-form-item>

        <!-- 测试连接 -->
        <el-form-item label="测试连接">
          <div class="test-section">
            <el-button :loading="testing" @click="handleTest">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <div v-if="testResult" class="test-result">
              <el-alert
                :title="testResult.success ? '连接成功' : '连接失败'"
                :type="testResult.success ? 'success' : 'error'"
                :closable="false"
                show-icon
              >
                <template v-if="testResult.success">
                  <p>模型: {{ testResult.model }}</p>
                  <p>Token消耗: {{ testResult.usage?.prompt_tokens + testResult.usage?.completion_tokens }}</p>
                </template>
                <template v-else>
                  <p>{{ testResult.error }}</p>
                </template>
              </el-alert>
            </div>
          </div>
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
.llm-config-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-card :deep(.el-card__body) {
  padding: 20px 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #fff;
}

.header-info p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.header-content .el-button {
  background-color: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.5);
  color: #fff;
}

.header-content .el-button:hover {
  background-color: rgba(255, 255, 255, 0.3);
}

.list-card {
  flex: 1;
}

.config-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.provider-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.provider-desc {
  font-size: 12px;
  color: #909399;
}

.model-select {
  display: flex;
  gap: 8px;
  width: 100%;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.test-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

.test-result {
  width: 100%;
}

.test-result p {
  margin: 4px 0;
}
</style>
