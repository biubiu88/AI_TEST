<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useRequirementStore } from '@/stores/requirement'
import { useTestcaseStore } from '@/stores/testcase'
import { usePromptStore } from '@/stores/prompt'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useLLMConfigStore } from '@/stores/llmConfig'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const requirementStore = useRequirementStore()
const testcaseStore = useTestcaseStore()
const promptStore = usePromptStore()
const knowledgeStore = useKnowledgeStore()
const llmConfigStore = useLLMConfigStore()

// 需求输入方式: select-选择需求, text-文本输入, upload-上传文档
const requirementInputType = ref('select')

// 生成配置
const generateForm = reactive({
  requirement_id: route.query.requirementId ? Number(route.query.requirementId) : '',
  requirement_text: '',
  requirement_title: '',
  include_boundary: true,
  include_exception: true,
  include_performance: false,
  count: 10,
  prompt_id: '',
  knowledge_ids: [],
  llm_config_id: ''
})

// 上传的文件
const uploadedFile = ref(null)
const uploadLoading = ref(false)
const parsedContent = ref('')

// 选中的需求详情
const selectedRequirement = ref(null)

// 预览的测试用例
const previewCases = ref([])
const previewLoading = ref(false)
const generateLoading = ref(false)

// 选中要保存的用例
const selectedCases = ref([])

// 加载需求列表
onMounted(async () => {
  await requirementStore.fetchRequirements({ per_page: 1000 })
  await promptStore.fetchAllPrompts()
  await knowledgeStore.fetchAllKnowledges()
  await llmConfigStore.fetchAllConfigs()
  
  // 如果有预选的需求，加载详情
  if (generateForm.requirement_id) {
    loadRequirementDetail(generateForm.requirement_id)
  }
  
  // 设置默认提示词
  const defaultPrompt = promptStore.allPrompts.find(p => p.is_default)
  if (defaultPrompt) {
    generateForm.prompt_id = defaultPrompt.id
  }
  
  // 设置默认大模型配置
  const defaultLLMConfig = llmConfigStore.allConfigs.find(c => c.is_default)
  if (defaultLLMConfig) {
    generateForm.llm_config_id = defaultLLMConfig.id
  }
})

// 监听需求选择变化
watch(() => generateForm.requirement_id, (newId) => {
  if (newId) {
    loadRequirementDetail(newId)
  } else {
    selectedRequirement.value = null
  }
  // 清空预览
  previewCases.value = []
  selectedCases.value = []
})

// 监听输入方式变化，清空相关数据
watch(requirementInputType, () => {
  previewCases.value = []
  selectedCases.value = []
  selectedRequirement.value = null
  parsedContent.value = ''
  uploadedFile.value = null
})

// 加载需求详情
const loadRequirementDetail = async (id) => {
  try {
    const data = await requirementStore.fetchRequirement(id)
    selectedRequirement.value = data
  } catch (e) {
    console.error(e)
  }
}

// 检查是否可以生成
const canGenerate = () => {
  if (requirementInputType.value === 'select') {
    if (!generateForm.requirement_id) {
      ElMessage.warning('请先选择需求')
      return false
    }
  } else if (requirementInputType.value === 'text') {
    if (!generateForm.requirement_text.trim()) {
      ElMessage.warning('请输入需求内容')
      return false
    }
  } else if (requirementInputType.value === 'upload') {
    if (!parsedContent.value) {
      ElMessage.warning('请先上传并解析文档')
      return false
    }
  }
  return true
}

// 获取生成请求数据
const getGenerateData = () => {
  const baseData = {
    include_boundary: generateForm.include_boundary,
    include_exception: generateForm.include_exception,
    include_performance: generateForm.include_performance,
    count: generateForm.count,
    prompt_id: generateForm.prompt_id,
    knowledge_ids: generateForm.knowledge_ids,
    llm_config_id: generateForm.llm_config_id
  }
  
  if (requirementInputType.value === 'select') {
    return {
      ...baseData,
      requirement_id: generateForm.requirement_id
    }
  } else if (requirementInputType.value === 'text') {
    return {
      ...baseData,
      requirement_content: generateForm.requirement_text,
      requirement_title: generateForm.requirement_title || '手动输入需求'
    }
  } else {
    return {
      ...baseData,
      requirement_content: parsedContent.value,
      requirement_title: uploadedFile.value?.name || '上传文档需求'
    }
  }
}

// 预览生成的测试用例
const handlePreview = async () => {
  if (!canGenerate()) return
  
  previewLoading.value = true
  previewCases.value = []
  selectedCases.value = []
  
  try {
    const data = await testcaseStore.previewTestcases(getGenerateData())
    previewCases.value = data
    // 默认全选
    selectedCases.value = data.map((_, index) => index)
    ElMessage.success(`成功生成 ${data.length} 条测试用例预览`)
  } catch (e) {
    console.error(e)
  } finally {
    previewLoading.value = false
  }
}

// 保存选中的测试用例
const handleSave = async () => {
  if (selectedCases.value.length === 0) {
    ElMessage.warning('请至少选择一条测试用例')
    return
  }
  
  generateLoading.value = true
  
  try {
    const testcases = selectedCases.value.map(index => ({
      ...previewCases.value[index],
      requirement_id: requirementInputType.value === 'select' ? generateForm.requirement_id : null,
      is_ai_generated: true
    }))
    
    await testcaseStore.createTestcasesBatch({ testcases })
    ElMessage.success(`成功保存 ${testcases.length} 条测试用例`)
    
    // 跳转到测试用例列表
    if (requirementInputType.value === 'select' && generateForm.requirement_id) {
      router.push({
        path: '/testcases',
        query: { requirementId: generateForm.requirement_id }
      })
    } else {
      router.push('/testcases')
    }
  } catch (e) {
    console.error(e)
  } finally {
    generateLoading.value = false
  }
}

// 直接生成并保存
const handleGenerateAndSave = async () => {
  if (!canGenerate()) return
  
  generateLoading.value = true
  
  try {
    const data = await testcaseStore.generateTestcases(getGenerateData())
    ElMessage.success(`成功生成并保存 ${data.length} 条测试用例`)
    
    if (requirementInputType.value === 'select' && generateForm.requirement_id) {
      router.push({
        path: '/testcases',
        query: { requirementId: generateForm.requirement_id }
      })
    } else {
      router.push('/testcases')
    }
  } catch (e) {
    console.error(e)
  } finally {
    generateLoading.value = false
  }
}

// 文件上传相关
const handleFileChange = (file) => {
  const allowedTypes = [
    'text/plain',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/pdf'
  ]
  const allowedExtensions = ['.txt', '.doc', '.docx', '.pdf']
  
  const fileName = file.name.toLowerCase()
  const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext))
  
  if (!hasValidExtension) {
    ElMessage.error('只支持 .txt, .doc, .docx, .pdf 格式的文件')
    return false
  }
  
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }
  
  uploadedFile.value = file
  return false // 阻止自动上传
}

const handleParseFile = async () => {
  if (!uploadedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploadLoading.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value.raw || uploadedFile.value)
    
    const response = await api.post('/ai/parse-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.code === 0) {
      parsedContent.value = response.data.content
      ElMessage.success('文档解析成功')
    } else {
      ElMessage.error(response.message || '解析失败')
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('文档解析失败')
  } finally {
    uploadLoading.value = false
  }
}

const handleRemoveFile = () => {
  uploadedFile.value = null
  parsedContent.value = ''
}

// 选择/取消选择用例
const handleSelectCase = (index) => {
  const idx = selectedCases.value.indexOf(index)
  if (idx > -1) {
    selectedCases.value.splice(idx, 1)
  } else {
    selectedCases.value.push(index)
  }
}

// 全选/取消全选
const handleSelectAll = () => {
  if (selectedCases.value.length === previewCases.value.length) {
    selectedCases.value = []
  } else {
    selectedCases.value = previewCases.value.map((_, index) => index)
  }
}

// 获取类型标签
const getCaseTypeLabel = (type) => {
  const labels = {
    functional: '功能测试',
    boundary: '边界测试',
    exception: '异常测试',
    performance: '性能测试'
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

const getPriorityLabel = (priority) => {
  const labels = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return labels[priority] || priority
}
</script>

<template>
  <div class="generate-view">
    <el-row :gutter="20">
      <!-- 左侧：配置区域 -->
      <el-col :span="8">
        <el-card class="config-card">
          <template #header>
            <div class="card-title">
              <el-icon><Setting /></el-icon>
              <span>生成配置</span>
            </div>
          </template>
          
          <el-form :model="generateForm" label-position="top">
            <el-form-item label="需求来源" required>
              <el-radio-group v-model="requirementInputType" size="small" class="full-width-radio">
                <el-radio-button value="select">选择需求</el-radio-button>
                <el-radio-button value="text">文本输入</el-radio-button>
                <el-radio-button value="upload">上传文档</el-radio-button>
              </el-radio-group>
            </el-form-item>
            
            <!-- 方式1：选择已有需求 -->
            <el-form-item v-if="requirementInputType === 'select'" label="选择需求">
              <el-select
                v-model="generateForm.requirement_id"
                placeholder="请选择要生成测试用例的需求"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="req in requirementStore.requirements"
                  :key="req.id"
                  :label="req.title"
                  :value="req.id"
                >
                  <div class="requirement-option">
                    <span>{{ req.title }}</span>
                    <el-tag size="small" type="info">{{ req.module || '未分类' }}</el-tag>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
            
            <!-- 方式2：文本输入 -->
            <el-form-item v-if="requirementInputType === 'text'" label="需求内容">
              <el-input
                v-model="generateForm.requirement_text"
                type="textarea"
                :rows="6"
                placeholder="请输入需求详细内容，AI将根据此内容生成测试用例"
              />
            </el-form-item>
            
            <!-- 方式3：上传文档 -->
            <template v-if="requirementInputType === 'upload'">
              <el-form-item label="上传文档">
                <el-upload
                  class="upload-area"
                  drag
                  :auto-upload="false"
                  :limit="1"
                  :on-change="handleFileChange"
                  :on-remove="handleRemoveFile"
                  accept=".txt,.doc,.docx,.pdf"
                >
                  <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                  <div class="el-upload__text">
                    将文件拖到此处，或<em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">
                      支持 .txt, .doc, .docx, .pdf 格式，最大10MB
                    </div>
                  </template>
                </el-upload>
                <el-button
                  v-if="uploadedFile"
                  type="primary"
                  size="small"
                  :loading="uploadLoading"
                  @click="handleParseFile"
                  style="margin-top: 10px"
                >
                  解析文档
                </el-button>
              </el-form-item>
              <el-form-item v-if="parsedContent" label="解析内容">
                <el-input
                  v-model="parsedContent"
                  type="textarea"
                  :rows="6"
                  placeholder="文档解析内容"
                />
                <div class="form-tip">您可以编辑解析后的内容</div>
              </el-form-item>
            </template>
            
            <el-form-item label="生成数量">
              <el-slider
                v-model="generateForm.count"
                :min="1"
                :max="20"
                :step="1"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="测试类型">
              <div class="type-checkboxes">
                <el-checkbox v-model="generateForm.include_boundary">
                  <el-tag type="warning" size="small">边界测试</el-tag>
                </el-checkbox>
                <el-checkbox v-model="generateForm.include_exception">
                  <el-tag type="danger" size="small">异常测试</el-tag>
                </el-checkbox>
                <el-checkbox v-model="generateForm.include_performance">
                  <el-tag type="success" size="small">性能测试</el-tag>
                </el-checkbox>
              </div>
            </el-form-item>
            
            <el-divider>
              <el-icon><Promotion /></el-icon>
              AI 增强配置
            </el-divider>
            
            <el-form-item label="大模型">
              <el-select
                v-model="generateForm.llm_config_id"
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
              <div class="form-tip">选择用于生成测试用例的AI大模型，不选择则使用默认配置</div>
            </el-form-item>
            
            <el-form-item label="提示词">
              <el-select
                v-model="generateForm.prompt_id"
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
              <div class="form-tip">提示词用于指导AI生成测试用例的风格和关注点</div>
            </el-form-item>
            
            <el-form-item label="知识库">
              <el-select
                v-model="generateForm.knowledge_ids"
                placeholder="选择知识库（可多选）"
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
              <div class="form-tip">知识库提供领域知识，帮助AI生成更专业的测试用例</div>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="previewLoading"
                @click="handlePreview"
                style="width: 100%"
              >
                <el-icon><View /></el-icon>
                预览生成
              </el-button>
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="success"
                :loading="generateLoading"
                @click="handleGenerateAndSave"
                style="width: 100%"
              >
                <el-icon><MagicStick /></el-icon>
                直接生成并保存
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 需求详情 -->
        <el-card v-if="selectedRequirement && requirementInputType === 'select'" class="detail-card">
          <template #header>
            <div class="card-title">
              <el-icon><Document /></el-icon>
              <span>需求详情</span>
            </div>
          </template>
          
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="标题">
              {{ selectedRequirement.title }}
            </el-descriptions-item>
            <el-descriptions-item label="模块">
              {{ selectedRequirement.module || '未分类' }}
            </el-descriptions-item>
            <el-descriptions-item label="已有用例">
              {{ selectedRequirement.testcase_count }} 条
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider>需求内容</el-divider>
          
          <div class="requirement-content">
            {{ selectedRequirement.content }}
          </div>
        </el-card>
      </el-col>
      
      <!-- 右侧：预览区域 -->
      <el-col :span="16">
        <el-card class="preview-card">
          <template #header>
            <div class="card-header">
              <div class="card-title">
                <el-icon><List /></el-icon>
                <span>测试用例预览</span>
                <el-tag v-if="previewCases.length" type="info" size="small">
                  {{ previewCases.length }} 条
                </el-tag>
              </div>
              
              <div v-if="previewCases.length" class="header-actions">
                <el-button size="small" @click="handleSelectAll">
                  {{ selectedCases.length === previewCases.length ? '取消全选' : '全选' }}
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  :loading="generateLoading"
                  :disabled="selectedCases.length === 0"
                  @click="handleSave"
                >
                  保存选中 ({{ selectedCases.length }})
                </el-button>
              </div>
            </div>
          </template>
          
          <!-- 空状态 -->
          <el-empty
            v-if="!previewCases.length && !previewLoading"
            description="请先输入需求内容并点击【预览生成】按钮"
          >
            <template #image>
              <el-icon :size="80" color="#c0c4cc"><MagicStick /></el-icon>
            </template>
          </el-empty>
          
          <!-- 加载状态 -->
          <div v-if="previewLoading" class="loading-wrapper">
            <el-icon class="is-loading" :size="40" color="#409eff">
              <Loading />
            </el-icon>
            <p>AI 正在生成测试用例，请稍候...</p>
          </div>
          
          <!-- 用例列表 -->
          <div v-if="previewCases.length && !previewLoading" class="case-list">
            <div
              v-for="(tc, index) in previewCases"
              :key="index"
              class="case-item"
              :class="{ selected: selectedCases.includes(index) }"
              @click="handleSelectCase(index)"
            >
              <div class="case-header">
                <el-checkbox
                  :model-value="selectedCases.includes(index)"
                  @click.stop
                  @change="handleSelectCase(index)"
                />
                <span class="case-title">{{ tc.title }}</span>
                <div class="case-tags">
                  <el-tag
                    size="small"
                    :style="{ backgroundColor: getCaseTypeColor(tc.case_type), color: '#fff', border: 'none' }"
                  >
                    {{ getCaseTypeLabel(tc.case_type) }}
                  </el-tag>
                  <el-tag size="small" type="info">
                    {{ getPriorityLabel(tc.priority) }}
                  </el-tag>
                </div>
              </div>
              
              <div class="case-body">
                <div class="case-section">
                  <label>前置条件:</label>
                  <p>{{ tc.precondition || '无' }}</p>
                </div>
                <div class="case-section">
                  <label>测试步骤:</label>
                  <p>{{ tc.steps }}</p>
                </div>
                <div class="case-section">
                  <label>预期结果:</label>
                  <p>{{ tc.expected_result }}</p>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.generate-view {
  height: 100%;
}

.config-card,
.detail-card,
.preview-card {
  height: fit-content;
}

.detail-card {
  margin-top: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
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

.requirement-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.type-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prompt-option,
.knowledge-option,
.llm-config-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.option-tags {
  display: flex;
  gap: 4px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
  line-height: 1.5;
}

.requirement-content {
  max-height: 200px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #909399;
}

.loading-wrapper p {
  margin-top: 16px;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.case-item {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.case-item:hover {
  border-color: #c0c4cc;
  background-color: #fafafa;
}

.case-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.case-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.case-title {
  flex: 1;
  font-weight: 500;
  font-size: 15px;
  color: #303133;
}

.case-tags {
  display: flex;
  gap: 8px;
}

.case-body {
  padding-left: 28px;
}

.case-section {
  margin-bottom: 8px;
}

.case-section:last-child {
  margin-bottom: 0;
}

.case-section label {
  font-size: 13px;
  color: #909399;
  font-weight: 500;
}

.case-section p {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #606266;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.5;
}

.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 20px;
}

.full-width-radio {
  width: 100%;
  display: flex;
}

.full-width-radio :deep(.el-radio-button) {
  flex: 1;
}

.full-width-radio :deep(.el-radio-button__inner) {
  width: 100%;
}
</style>
