<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { aiAssistantApi } from '@/api'

// 会话列表
const sessions = ref([])
const currentSession = ref(null)
const messages = ref([])
const loading = ref(false)
const sending = ref(false)
const fullscreen = ref(false)

// 配置选项
const knowledgeBases = ref([])
const prompts = ref([])
const mcpConfigs = ref([])
const models = ref([])

// 会话设置对话框
const settingsDialogVisible = ref(false)
const settingsForm = reactive({
  session_name: '',
  model_id: null,
  prompt_id: null,
  knowledge_ids: [],
  mcp_config_id: null
})

// 会话名称编辑对话框
const renameDialogVisible = ref(false)
const renameForm = reactive({
  session_name: ''
})

// 输入框
const inputRef = ref(null)
const messageContent = ref('')

// 消息列表滚动容器
const messagesContainer = ref(null)

// 加载会话列表
const loadSessions = async () => {
  try {
    loading.value = true
    const res = await aiAssistantApi.getSessions()
    sessions.value = res.data.list
    
    if (sessions.value.length > 0 && !currentSession.value) {
      selectSession(sessions.value[0])
    }
  } catch (error) {
    console.error('加载会话列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 选择会话
const selectSession = async (session) => {
  currentSession.value = session
  await loadMessages(session.id)
}

// 加载消息
const loadMessages = async (sessionId) => {
  try {
    const res = await aiAssistantApi.getMessages(sessionId)
    messages.value = res.data
    scrollToBottom()
  } catch (error) {
    console.error('加载消息失败:', error)
  }
}

// 创建新会话
const createSession = async () => {
  try {
    const res = await aiAssistantApi.createSession({
      session_name: '新会话'
    })
    sessions.value.unshift(res.data)
    selectSession(res.data)
    ElMessage.success('创建成功')
  } catch (error) {
    console.error('创建会话失败:', error)
  }
}

// 删除会话
const deleteSession = async (session) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除会话"${session.session_name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await aiAssistantApi.deleteSession(session.id)
    
    const index = sessions.value.findIndex(s => s.id === session.id)
    if (index > -1) {
      sessions.value.splice(index, 1)
    }
    
    if (currentSession.value?.id === session.id) {
      currentSession.value = null
      messages.value = []
    }
    
    ElMessage.success('删除成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 重命名会话
const renameSession = async () => {
  try {
    await aiAssistantApi.updateSession(currentSession.value.id, {
      session_name: renameForm.session_name
    })
    currentSession.value.session_name = renameForm.session_name
    renameDialogVisible.value = false
    ElMessage.success('重命名成功')
  } catch (error) {
    console.error('重命名失败:', error)
  }
}

// 打开设置对话框
const openSettings = async () => {
  console.log('打开设置对话框')
  try {
    console.log('开始获取配置数据')
    const [kbRes, promptRes, mcpRes, modelRes] = await Promise.all([
      aiAssistantApi.getKnowledgeBases(),
      aiAssistantApi.getPrompts(),
      aiAssistantApi.getMcpConfigs(),
      aiAssistantApi.getModels()
    ])
    
    console.log('获取配置数据成功:', { kbRes, promptRes, mcpRes, modelRes })
    
    // 更新下拉框数据
    knowledgeBases.value = kbRes.data || []
    prompts.value = promptRes.data || []
    mcpConfigs.value = mcpRes.data || []
    models.value = modelRes.data || []
    
    console.log('更新后的下拉框数据:', {
      knowledgeBases: knowledgeBases.value,
      prompts: prompts.value,
      mcpConfigs: mcpConfigs.value,
      models: models.value
    })
    
    // 设置表单数据
    settingsForm.session_name = currentSession.value.session_name
    settingsForm.model_id = currentSession.value.model_id
    settingsForm.prompt_id = currentSession.value.prompt_id
    settingsForm.knowledge_ids = currentSession.value.knowledge_ids || []
    settingsForm.mcp_config_id = currentSession.value.mcp_config_id
    
    // 等待DOM更新后再打开对话框
    await nextTick()
    
    console.log('设置表单数据:', {
      session_name: settingsForm.session_name,
      model_id: settingsForm.model_id,
      prompt_id: settingsForm.prompt_id,
      knowledge_ids: settingsForm.knowledge_ids,
      mcp_config_id: settingsForm.mcp_config_id
    })
    
    settingsDialogVisible.value = true
    console.log('设置对话框已打开')
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败，请检查网络连接或重新登录')
  }
}

// 保存设置
const saveSettings = async () => {
  try {
    await aiAssistantApi.updateSession(currentSession.value.id, settingsForm)
    currentSession.value = { ...currentSession.value, ...settingsForm }
    settingsDialogVisible.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存设置失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!messageContent.value.trim() || sending.value) return
  
  const content = messageContent.value.trim()
  messageContent.value = ''
  
  try {
    sending.value = true
    
    const userMessage = {
      role: 'user',
      content: content,
      message_type: 'text',
      created_at: new Date().toISOString()
    }
    messages.value.push(userMessage)
    scrollToBottom()
    
    const res = await aiAssistantApi.sendMessage(currentSession.value.id, {
      content: content,
      options: {
        model_id: currentSession.value.model_id,
        prompt_id: currentSession.value.prompt_id,
        knowledge_ids: currentSession.value.knowledge_ids,
        mcp_config_id: currentSession.value.mcp_config_id
      }
    })
    
    messages.value.push(res.data)
    scrollToBottom()
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送失败，请重试')
  } finally {
    sending.value = false
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 切换全屏模式
const toggleFullscreen = () => {
  fullscreen.value = !fullscreen.value
}

// 格式化时间
const formatTime = (time) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString()
  }
}

// 获取模型名称
const getModelName = (modelId) => {
  if (!modelId) return ''
  const model = models.value.find(m => m.id === modelId)
  return model ? model.name : '未知模型'
}

onMounted(() => {
  loadSessions()
})
</script>

<template>
  <div class="ai-assistant-view" :class="{ fullscreen: fullscreen }">
    <!-- 会话列表侧边栏 -->
    <div class="session-sidebar">
      <div class="sidebar-header">
        <h3>AI助手</h3>
        <el-button type="primary" size="small" @click="createSession">
          <el-icon><Plus /></el-icon>
          新建会话
        </el-button>
      </div>
      
      <div class="session-list" v-loading="loading">
        <div
          v-for="session in sessions"
          :key="session.id"
          :class="['session-item', { active: currentSession?.id === session.id }]"
          @click="selectSession(session)"
        >
          <div class="session-main">
            <div class="session-name">{{ session.session_name }}</div>
            <div class="session-time">{{ formatTime(session.updated_at) }}</div>
          </div>
          <div class="session-actions" @click.stop>
            <el-dropdown trigger="click">
              <el-button type="primary" link size="small">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="renameForm.session_name = session.session_name; currentSession = session; renameDialogVisible = true">
                    重命名
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteSession(session)" style="color: #f56c6c">
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area">
      <div v-if="currentSession" class="chat-container">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-title">
            <h3>{{ currentSession.session_name }}</h3>
            <div class="chat-badges">
              <el-tag v-if="currentSession.model_id" size="small" type="primary">
                <el-icon><Monitor /></el-icon>
                {{ getModelName(currentSession.model_id) }}
              </el-tag>
              <el-tag v-if="currentSession.prompt_id" size="small" type="info">
                <el-icon><Promotion /></el-icon>
                提示词
              </el-tag>
              <el-tag v-if="currentSession.knowledge_ids?.length" size="small" type="success">
                <el-icon><Collection /></el-icon>
                {{ currentSession.knowledge_ids.length }}个知识库
              </el-tag>
              <el-tag v-if="currentSession.mcp_config_id" size="small" type="warning">
                <el-icon><Connection /></el-icon>
                MCP启用
              </el-tag>
            </div>
          </div>
          <div class="header-actions">
            <el-button type="primary" link @click="openSettings">
              <el-icon><Setting /></el-icon>
              设置
            </el-button>
            <el-button type="primary" link @click="toggleFullscreen">
              <el-icon><FullScreen v-if="!fullscreen" /><Aim v-else /></el-icon>
              {{ fullscreen ? '退出全屏' : '全屏' }}
            </el-button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-icon">
              <el-icon><ChatLineRound /></el-icon>
            </div>
            <h3>开始与AI助手对话吧！</h3>
            <p>你可以询问测试相关的问题，让我帮你生成测试用例、分析需求等</p>
          </div>
          
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', message.role]"
          >
            <div class="message-avatar">
              <el-icon v-if="message.role === 'user'"><User /></el-icon>
              <el-icon v-else><Robot /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text">{{ message.content }}</div>
              <div class="message-time">{{ formatTime(message.created_at) }}</div>
            </div>
          </div>
          
          <div v-if="sending" class="message-item assistant">
            <div class="message-avatar">
              <el-icon><Robot /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-text typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="input-area">
          <div class="input-wrapper">
            <el-input
              ref="inputRef"
              v-model="messageContent"
              type="textarea"
              :rows="3"
              placeholder="输入消息，按Enter发送，Shift+Enter换行"
              @keydown.enter.exact.prevent="sendMessage"
              :disabled="sending"
              resize="none"
            />
            <div class="input-actions">
              <el-button type="primary" :loading="sending" @click="sendMessage" size="large">
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
          <div class="input-hint">
            <el-icon><InfoFilled /></el-icon>
            AI助手可以帮你生成测试用例、分析需求、提供测试建议等
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <el-icon><ChatLineRound /></el-icon>
        </div>
        <h2>AI助手</h2>
        <p>选择一个会话或创建新会话开始对话</p>
        <el-button type="primary" size="large" @click="createSession">
          <el-icon><Plus /></el-icon>
          新建会话
        </el-button>
      </div>
    </div>

    <!-- 设置对话框 -->
    <el-dialog
      v-model="settingsDialogVisible"
      title="会话设置"
      width="600px"
      destroy-on-close
      append-to-body
      :z-index="10000"
    >
      <el-form label-width="100px">
        <el-form-item label="会话名称">
          <el-input v-model="settingsForm.session_name" placeholder="请输入会话名称" />
        </el-form-item>
        
        <el-form-item label="选择大模型">
          <el-select v-model="settingsForm.model_id" placeholder="选择大模型" clearable style="width: 100%">
            <el-option
              v-for="model in models"
              :key="model.id"
              :label="model.name"
              :value="model.id"
            >
              <div>
                <span>{{ model.name }}</span>
                <el-tag size="small" style="margin-left: 8px">{{ model.provider }}</el-tag>
              </div>
              <div style="color: #999; font-size: 12px; margin-top: 4px">
                {{ model.description }}
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="使用提示词">
          <el-select v-model="settingsForm.prompt_id" placeholder="选择提示词" clearable style="width: 100%">
            <el-option
              v-for="prompt in prompts"
              :key="prompt.id"
              :label="prompt.name"
              :value="prompt.id"
            >
              <div>
                <span>{{ prompt.name }}</span>
                <span style="color: #999; font-size: 12px; margin-left: 10px">
                  {{ prompt.description }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="关联知识库">
          <el-select
            v-model="settingsForm.knowledge_ids"
            placeholder="选择知识库"
            multiple
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            >
              <div>
                <span>{{ kb.name }}</span>
                <span style="color: #999; font-size: 12px; margin-left: 10px">
                  {{ kb.description }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="启用MCP">
          <el-select v-model="settingsForm.mcp_config_id" placeholder="选择MCP配置" clearable style="width: 100%">
            <el-option
              v-for="mcp in mcpConfigs"
              :key="mcp.id"
              :label="mcp.name"
              :value="mcp.id"
            >
              <div>
                <span>{{ mcp.name }}</span>
                <span style="color: #999; font-size: 12px; margin-left: 10px">
                  {{ mcp.server_name }}
                </span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settingsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重命名对话框 -->
    <el-dialog
      v-model="renameDialogVisible"
      title="重命名会话"
      width="400px"
      destroy-on-close
      append-to-body
      :z-index="10000"
    >
      <el-form label-width="80px">
        <el-form-item label="会话名称">
          <el-input v-model="renameForm.session_name" placeholder="请输入会话名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="renameSession">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.ai-assistant-view {
  display: flex;
  height: calc(100vh - 80px);
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
}

.ai-assistant-view.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  height: 100vh;
  padding: 0;
  gap: 0;
  background: #fff;
}

.session-sidebar {
  width: 280px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.fullscreen .session-sidebar {
  border-radius: 0;
  box-shadow: none;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e8ecf1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.sidebar-header h3 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.session-item {
  padding: 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid transparent;
}

.session-item:hover {
  background: #f8f9fa;
  border-color: #e8ecf1;
}

.session-item.active {
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  border-color: #667eea;
}

.session-main {
  flex: 1;
}

.session-name {
  font-weight: 500;
  margin-bottom: 4px;
  color: #333;
}

.session-time {
  font-size: 12px;
  color: #999;
}

.session-actions {
  opacity: 0;
  transition: opacity 0.3s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.chat-area {
  flex: 1;
  background: #fff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.fullscreen .chat-area {
  border-radius: 0;
  box-shadow: none;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e8ecf1;
  background: #fff;
}

.chat-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.chat-title h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chat-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.chat-badges .el-tag {
  display: flex;
  align-items: center;
  gap: 4px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  background: #f8f9fa;
}

.message-item {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.message-item.assistant .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.message-item.user .message-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.message-content {
  max-width: 70%;
}

.message-text {
  background: #fff;
  padding: 16px 20px;
  border-radius: 12px;
  line-height: 1.6;
  color: #333;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-item.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
  text-align: right;
}

.message-item.assistant .message-time {
  text-align: left;
}

.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

.input-area {
  padding: 16px 24px;
  border-top: 1px solid #e8ecf1;
  background: #fff;
}

.input-wrapper {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid #e8ecf1;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-wrapper :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  resize: none;
  font-size: 14px;
  line-height: 1.6;
}

.input-wrapper :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.input-hint {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f0f9ff;
  border-radius: 6px;
  color: #667eea;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  padding: 40px;
}

.empty-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.empty-icon .el-icon {
  font-size: 64px;
  color: #667eea;
}

.empty-state h2 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.empty-state p {
  margin: 0 0 24px 0;
  color: #666;
  text-align: center;
  max-width: 400px;
}

/* 滚动条样式 */
.session-list::-webkit-scrollbar,
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.session-list::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #d8dce5;
  border-radius: 3px;
}

.session-list::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

.session-list::-webkit-scrollbar-track,
.messages-container::-webkit-scrollbar-track {
  background: transparent;
}
</style>
