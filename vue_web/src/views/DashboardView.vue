<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { testcaseApi, requirementApi } from '@/api'
import { useUserStore } from '@/stores/user'
import { usePermissionStore } from '@/stores/permission'
import {
  Document,
  List,
  MagicStick,
  ChatDotRound,
  Collection,
  ArrowRight,
  Calendar,
  User,
  TrendCharts
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

// 统计数据
const stats = reactive({
  totalRequirements: 0,
  totalTestcases: 0,
  pendingTestcases: 0,
  aiGeneratedTestcases: 0
})

// 最近用例
const recentTestcases = ref([])

// 待处理任务
const pendingTasks = ref([])

// 加载统计数据
const loadStats = async () => {
  try {
    const [statsRes, testcaseRes] = await Promise.all([
      testcaseApi.getStats(),
      testcaseApi.getList({ page: 1, per_page: 5 })
    ])

    if (statsRes.data) {
      stats.totalTestcases = statsRes.data.total || 0
      stats.pendingTestcases = statsRes.data.pending || 0
      stats.aiGeneratedTestcases = statsRes.data.aiGenerated || 0
    }

    if (testcaseRes.data) {
      recentTestcases.value = testcaseRes.data.list || []
    }

    // 获取需求数量
    const reqRes = await requirementApi.getList({ page: 1, per_page: 1 })
    if (reqRes.data) {
      stats.totalRequirements = reqRes.data.total || 0
    }

    // 模拟待处理任务
    pendingTasks.value = [
      { id: 1, title: '审核测试用例 #123', type: 'review', time: '2小时前' },
      { id: 2, title: '执行测试套件 #456', type: 'execute', time: '5小时前' },
      { id: 3, title: '更新需求文档 #789', type: 'update', time: '1天前' }
    ]
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 所有快捷入口
const allShortcuts = [
  {
    title: '测试用例管理',
    icon: List,
    path: '/testing/testcases',
    desc: '查看和管理所有测试用例',
    color: '#409eff',
    permission: 'testcase:view'
  },
  {
    title: '生成用例',
    icon: MagicStick,
    path: '/testing/generate',
    desc: '使用AI智能生成测试用例',
    color: '#67c23a',
    permission: 'ai:generate'
  },
  {
    title: '需求管理',
    icon: Document,
    path: '/testing/requirements',
    desc: '管理产品需求和文档',
    color: '#e6a23c',
    permission: 'requirement:view'
  },
  {
    title: '提示词管理',
    icon: ChatDotRound,
    path: '/testing/prompts',
    desc: '配置AI生成提示词',
    color: '#f56c6c',
    permission: 'prompt:view'
  },
  {
    title: '知识库管理',
    icon: Collection,
    path: '/knowledge/knowledges',
    desc: '管理测试知识资产',
    color: '#909399',
    permission: 'knowledge:view'
  },
  {
    title: '系统配置',
    icon: TrendCharts,
    path: '/system/users',
    desc: '管理系统用户和权限',
    color: '#8e44ad',
    permission: 'system:user'
  }
]

// 根据权限过滤快捷入口
const shortcuts = computed(() => {
  const permissions = permissionStore.permissions
  return allShortcuts.filter(shortcut => {
    // 如果是管理员，显示所有快捷入口
    if (userStore.isAdmin) return true
    // 否则只显示有权限的快捷入口
    return permissions.includes(shortcut.permission)
  })
})

// 跳转到快捷入口
const goToShortcut = (path) => {
  router.push(path)
}

// 获取任务类型标签
const getTaskTypeLabel = (type) => {
  const labels = {
    review: '审核',
    execute: '执行',
    update: '更新'
  }
  return labels[type] || type
}

// 获取任务类型颜色
const getTaskTypeColor = (type) => {
  const colors = {
    review: 'warning',
    execute: 'danger',
    update: 'info'
  }
  return colors[type] || ''
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="dashboard-view">
    <!-- 欢迎区域 -->
    <el-card class="welcome-card">
      <div class="welcome-content">
        <div class="welcome-text">
          <h2>欢迎回来，{{ userStore.getUserInfo?.nickname || userStore.getUserInfo?.username }}！</h2>
          <p>今天是 {{ new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}</p>
        </div>
        <div class="welcome-stats">
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalTestcases }}</div>
            <div class="stat-label">测试用例</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalRequirements }}</div>
            <div class="stat-label">需求文档</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.pendingTestcases }}</div>
            <div class="stat-label">待执行</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.aiGeneratedTestcases }}</div>
            <div class="stat-label">AI生成</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 快捷入口 -->
    <el-card class="shortcuts-card">
      <template #header>
        <div class="card-header">
          <span>快捷入口</span>
        </div>
      </template>
      <div class="shortcuts-grid">
        <div
          v-for="shortcut in shortcuts"
          :key="shortcut.path"
          class="shortcut-item"
          @click="goToShortcut(shortcut.path)"
        >
          <div class="shortcut-icon" :style="{ backgroundColor: shortcut.color }">
            <el-icon :size="32">
              <component :is="shortcut.icon" />
            </el-icon>
          </div>
          <div class="shortcut-content">
            <h3>{{ shortcut.title }}</h3>
            <p>{{ shortcut.desc }}</p>
          </div>
          <el-icon class="shortcut-arrow" :size="20">
            <ArrowRight />
          </el-icon>
        </div>
      </div>
    </el-card>

    <div class="dashboard-row">
      <!-- 最近用例 -->
      <el-card class="recent-card">
        <template #header>
          <div class="card-header">
            <span>最近用例</span>
            <el-button type="primary" link @click="router.push('/testing/testcases')">
              查看全部
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        <div class="recent-list">
          <div v-if="recentTestcases.length === 0" class="empty-state">
            <el-icon :size="48" color="#909399">
              <List />
            </el-icon>
            <p>暂无测试用例</p>
          </div>
          <div
            v-for="item in recentTestcases"
            :key="item.id"
            class="recent-item"
            @click="router.push('/testing/testcases')"
          >
            <div class="recent-info">
              <h4>{{ item.title }}</h4>
              <p>{{ item.case_type }} | {{ item.priority }}</p>
            </div>
            <el-tag :type="item.status === 'passed' ? 'success' : item.status === 'failed' ? 'danger' : 'info'" size="small">
              {{ item.status }}
            </el-tag>
          </div>
        </div>
      </el-card>

      <!-- 待处理任务 -->
      <el-card class="tasks-card">
        <template #header>
          <div class="card-header">
            <span>待处理任务</span>
          </div>
        </template>
        <div class="tasks-list">
          <div v-if="pendingTasks.length === 0" class="empty-state">
            <el-icon :size="48" color="#909399">
              <Calendar />
            </el-icon>
            <p>暂无待处理任务</p>
          </div>
          <div v-for="task in pendingTasks" :key="task.id" class="task-item">
            <div class="task-info">
              <h4>{{ task.title }}</h4>
              <p>{{ task.time }}</p>
            </div>
            <el-tag :type="getTaskTypeColor(task.type)" size="small">
              {{ getTaskTypeLabel(task.type) }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.welcome-card :deep(.el-card__body) {
  padding: 30px;
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.welcome-text h2 {
  margin: 0 0 10px 0;
  font-size: 28px;
  font-weight: 600;
}

.welcome-text p {
  margin: 0;
  font-size: 16px;
  opacity: 0.9;
}

.welcome-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.shortcuts-card {
  margin-bottom: 0;
}

.shortcuts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.shortcut-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.shortcut-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.shortcut-content {
  flex: 1;
}

.shortcut-content h3 {
  margin: 0 0 5px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.shortcut-content p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.shortcut-arrow {
  color: #c0c4cc;
  transition: all 0.3s;
}

.shortcut-item:hover .shortcut-arrow {
  color: #409eff;
  transform: translateX(5px);
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.recent-card,
.tasks-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.recent-list,
.tasks-list {
  min-height: 200px;
}

.recent-item,
.task-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.recent-item:hover,
.task-item:hover {
  background-color: #f5f7fa;
}

.recent-item:last-child,
.task-item:last-child {
  border-bottom: none;
}

.recent-info,
.task-info h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #303133;
}

.recent-info p,
.task-info p {
  margin: 0;
  font-size: 12px;
  color: #909399;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
}

.empty-state p {
  margin-top: 10px;
  font-size: 14px;
}

@media screen and (max-width: 1200px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }

  .welcome-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .welcome-stats {
    width: 100%;
    justify-content: space-around;
  }
}
</style>
