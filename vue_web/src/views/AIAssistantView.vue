<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { aiAssistantApi } from '@/api'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

// 初始化 Markdown 解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>';
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>';
  }
})

// 渲染 Markdown 内容
const renderMarkdown = (content) => {
  return md.render(content || '')
}

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

// 复制消息
const copyMessage = (content) => {
  navigator.clipboard.writeText(content).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(err => {
    console.error('复制失败:', err)
    ElMessage.error('复制失败')
  })
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
        <div class="header-top">
          <el-icon class="app-icon"><ChatLineRound /></el-icon>
          <h3>AI 助手</h3>
        </div>
        <el-button class="new-session-btn" type="primary" @click="createSession">
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
          <div class="session-icon">
            <el-icon><ChatDotRound /></el-icon>
          </div>
          <div class="session-main">
            <div class="session-name">{{ session.session_name }}</div>
            <div class="session-time">{{ formatTime(session.updated_at) }}</div>
          </div>
          <div class="session-actions" @click.stop>
            <el-dropdown trigger="click" placement="bottom-end">
              <el-button type="primary" link size="small" class="more-btn">
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="renameForm.session_name = session.session_name; currentSession = session; renameDialogVisible = true">
                    <el-icon><EditPen /></el-icon>重命名
                  </el-dropdown-item>
                  <el-dropdown-item @click="deleteSession(session)" style="color: #f56c6c">
                    <el-icon><Delete /></el-icon>删除
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
            <div class="empty-illustration">
              <div class="ai-circle">
                <el-icon><Cpu /></el-icon>
              </div>
              <div class="pulse-ring"></div>
            </div>
            <h3>开始与 AI 助手对话吧！</h3>
            <p>我可以帮你生成测试用例、分析需求、编写脚本或解答任何测试相关的技术难题</p>
            <div class="quick-suggestions">
              <div class="suggestion-tag" @click="messageContent = '帮我生成一个登录页面的测试用例'; sendMessage()">
                生成登录测试用例
              </div>
              <div class="suggestion-tag" @click="messageContent = '如何进行性能测试压力测试？'; sendMessage()">
                性能测试建议
              </div>
            </div>
          </div>
          
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message-item', message.role]"
          >
            <div class="message-avatar">
              <el-avatar :size="40" :icon="message.role === 'user' ? 'User' : 'Service'" 
                :class="message.role === 'user' ? 'user-avatar' : 'ai-avatar'" />
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <div class="message-text markdown-body" v-html="renderMarkdown(message.content)"></div>
              </div>
              <div class="message-footer">
                <span class="message-time">{{ formatTime(message.created_at) }}</span>
                <el-button v-if="message.role === 'assistant'" type="primary" link size="small" class="copy-btn" @click="copyMessage(message.content)">
                  <el-icon><CopyDocument /></el-icon>复制
                </el-button>
              </div>
            </div>
          </div>
          
          <div v-if="sending" class="message-item assistant">
            <div class="message-avatar">
              <el-avatar :size="40" icon="Service" class="ai-avatar" />
            </div>
            <div class="message-content">
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
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
  height: 100%;
  gap: 20px;
  padding: 0;
  background-color: #f0f2f5;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  overflow: hidden;
}

.ai-assistant-view.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  height: 100vh;
  padding: 0;
  gap: 0;
  background: #fff;
}

/* 侧边栏优化 */
.session-sidebar {
  width: 300px;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
}

.fullscreen .session-sidebar {
  border-radius: 0;
  box-shadow: none;
  border: none;
  border-right: 1px solid #f0f0f0;
}

.sidebar-header {
  padding: 24px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.app-icon {
  font-size: 24px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.new-session-btn {
  width: 100%;
  height: 40px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: #fff;
  font-weight: 600;
  transition: all 0.3s;
}

.new-session-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px 12px;
}

.session-item {
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid transparent;
}

.session-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #764ba2;
  font-size: 18px;
}

.session-item:hover {
  background: #f8faff;
  border-color: #e0e7ff;
}

.session-item.active {
  background: #f0f4ff;
  border-color: #667eea;
}

.session-item.active .session-icon {
  background: #667eea;
  color: #fff;
}

.session-main {
  flex: 1;
  min-width: 0;
}

.session-name {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-time {
  font-size: 12px;
  color: #94a3b8;
}

.session-actions {
  opacity: 0;
  transition: opacity 0.2s;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.more-btn {
  padding: 4px;
}

/* 聊天区域优化 */
.chat-area {
  flex: 1;
  background: #fff;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef0f2;
}

.fullscreen .chat-area {
  border-radius: 0;
  box-shadow: none;
  border: none;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  flex-shrink: 0;
  padding: 16px 24px;
  border-bottom: 1px solid #f0f0f0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-title h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.chat-badges {
  display: flex;
  gap: 6px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding: 30px 24px;
  background: #fcfdfe;
  scroll-behavior: smooth;
}

/* 空状态美化 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  text-align: center;
}

.empty-illustration {
  position: relative;
  margin-bottom: 30px;
}

.ai-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 40px;
  z-index: 2;
  position: relative;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100px;
  height: 100px;
  border: 2px solid #667eea;
  border-radius: 50%;
  opacity: 0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0.5; }
  100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
}

.empty-state h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 12px;
}

.empty-state p {
  color: #64748b;
  max-width: 450px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.quick-suggestions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.suggestion-tag {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 13px;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-tag:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f8faff;
  transform: translateY(-1px);
}

/* 消息气泡优化 */
.message-item {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  max-width: 85%;
}

.message-item.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.user-avatar {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: #fff;
}

.ai-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message-bubble {
  padding: 14px 18px;
  border-radius: 18px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  position: relative;
  line-height: 1.6;
  font-size: 14.5px;
}

.message-item.assistant .message-bubble {
  background: #fff;
  color: #1e293b;
  border: 1px solid #f1f5f9;
  border-top-left-radius: 4px;
}

.message-item.user .message-bubble {
  background: #667eea;
  color: #fff;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.message-text {
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* Markdown 样式优化 */
:deep(.markdown-body) {
  font-size: 14.5px;
  line-height: 1.6;
  
  p {
    margin-bottom: 8px;
    &:last-child { margin-bottom: 0; }
  }
  
  ul, ol {
    padding-left: 20px;
    margin-bottom: 8px;
  }
  
  li { margin-bottom: 4px; }
  
  code {
    background-color: rgba(175, 184, 193, 0.2);
    padding: 0.2em 0.4em;
    border-radius: 6px;
    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
    font-size: 85%;
  }
  
  pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 8px;
    overflow: auto;
    margin-bottom: 12px;
    
    code {
      background-color: transparent;
      padding: 0;
      font-size: 13px;
    }
  }
  
  table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
    overflow-x: auto;
    display: block;
    
    th, td {
      border: 1px solid #d0d7de;
      padding: 6px 13px;
    }
    
    th {
      font-weight: 600;
      background-color: #f6f8fa;
    }
    
    tr:nth-child(2n) {
      background-color: #f6f8fa;
    }
  }
  
  blockquote {
    border-left: 4px solid #d0d7de;
    padding: 0 1em;
    color: #656d76;
    margin: 0 0 8px 0;
  }
}

.message-item.user :deep(.markdown-body) {
  color: #fff;
  
  code {
    background-color: rgba(255, 255, 255, 0.2);
    color: #fff;
  }
  
  pre {
    background-color: rgba(0, 0, 0, 0.2);
    code { color: #fff; }
  }
  
  table {
    th, td { border-color: rgba(255, 255, 255, 0.3); }
    tr:nth-child(2n) { background-color: rgba(255, 255, 255, 0.1); }
  }
  
  blockquote {
    border-left-color: rgba(255, 255, 255, 0.3);
    color: rgba(255, 255, 255, 0.8);
  }
}

.message-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
}

.message-item.user .message-footer {
  justify-content: flex-end;
}

.copy-btn {
  padding: 0;
  height: auto;
  font-size: 11px;
}

/* 输入区域优化 */
.input-area {
  flex-shrink: 0;
  padding: 20px 24px;
  background: #fff;
  border-top: 1px solid #f0f0f0;
}

.input-wrapper {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 8px;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.08);
}

.input-wrapper :deep(.el-textarea__inner) {
  border: none;
  background: transparent;
  padding: 8px 12px;
  font-size: 15px;
  color: #1e293b;
  box-shadow: none !important;
}

.input-wrapper :deep(.el-textarea__inner):focus {
  box-shadow: none;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
  padding: 4px 8px;
}

.input-actions .el-button {
  border-radius: 10px;
  padding: 10px 24px;
}

.input-hint {
  margin-top: 12px;
  color: #94a3b8;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: center;
}

/* 输入状态动画 */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: 10px 5px;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #667eea;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1.0); }
}

/* 滚动条 */
.session-list::-webkit-scrollbar,
.messages-container::-webkit-scrollbar {
  width: 5px;
}

.session-list::-webkit-scrollbar-thumb,
.messages-container::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}

.session-list::-webkit-scrollbar-thumb:hover,
.messages-container::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
