<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { testcaseApi, requirementApi, logApi } from '@/api'
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
  TrendCharts,
  Setting,
  InfoFilled,
  Select,
  DataLine
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const router = useRouter()
const userStore = useUserStore()
const permissionStore = usePermissionStore()

// 折线图表容器
const chartContainer = ref(null)
let chartInstance = null

// API调用图表容器
const apiChartContainer = ref(null)
let apiChartInstance = null

// API调用图表时间范围
const apiChartTimeRange = ref('month')

// 统计数据
const stats = reactive({
  totalRequirements: 0,
  totalTestcases: 0,
  pendingTestcases: 0,
  aiGeneratedTestcases: 0,
  totalApiCalls: 0,
  todayApiCalls: 0,
  successApiCalls: 0,
  failApiCalls: 0
})

// 最近用例
const recentTestcases = ref([])

// 最近需求
const recentRequirements = ref([])

// 快捷入口设置对话框
const shortcutSettingsVisible = ref(false)
const userShortcuts = ref([])
const selectedShortcut = ref('')

// 加载统计数据
const loadStats = async () => {
  try {
    const [statsRes, testcaseRes, reqRes, logStatsRes] = await Promise.all([
      testcaseApi.getStats(),
      testcaseApi.getList({ page: 1, per_page: 5 }),
      requirementApi.getList({ page: 1, per_page: 5 }),
      logApi.getStatistics()
    ])

    if (statsRes.data) {
      stats.totalTestcases = statsRes.data.total || 0
      stats.pendingTestcases = statsRes.data.pending || 0
      stats.aiGeneratedTestcases = statsRes.data.ai_generated || 0
    }

    if (testcaseRes.data) {
      recentTestcases.value = testcaseRes.data.list || []
    }

    if (reqRes.data) {
      stats.totalRequirements = reqRes.data.total || 0
      recentRequirements.value = reqRes.data.list || []
    }

    // 加载日志统计数据
    if (logStatsRes.data) {
      stats.totalApiCalls = logStatsRes.data.total || 0
      stats.todayApiCalls = logStatsRes.data.today_count || 0
      stats.successApiCalls = logStatsRes.data.success_count || 0
      stats.failApiCalls = logStatsRes.data.fail_count || 0
    }

    // 加载图表数据
    loadChartData()
    loadApiChartData()
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 加载图表数据
const loadChartData = async () => {
  try {
    // 获取最近7天的用例统计数据
    const chartData = await testcaseApi.getList({ page: 1, per_page: 1000 })
    if (chartData.data && chartData.data.list) {
      initChart(chartData.data.list)
    }
  } catch (error) {
    console.error('加载图表数据失败:', error)
  }
}

// 初始化折线图
const initChart = (testcases) => {
  if (!chartContainer.value) return

  // 按日期统计用例数量
  const dateMap = {}
  const today = new Date()
  const last7Days = []
  
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    last7Days.push(dateStr)
    dateMap[dateStr] = 0
  }

  // 统计每天的用例数量
  testcases.forEach(tc => {
    if (tc.created_at) {
      const dateStr = tc.created_at.split('T')[0]
      if (dateMap.hasOwnProperty(dateStr)) {
        dateMap[dateStr]++
      }
    }
  })

  const values = last7Days.map(date => dateMap[date])

  // 销毁旧图表
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新图表
  chartInstance = echarts.init(chartContainer.value)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: last7Days.map(date => {
        const d = new Date(date)
        return `${d.getMonth() + 1}/${d.getDate()}`
      })
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '新增用例',
        type: 'line',
        smooth: true,
        data: values,
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      }
    ]
  }
  chartInstance.setOption(option)

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

// 加载API调用图表数据
const loadApiChartData = async () => {
  try {
    // 根据时间范围获取不同数量的数据
    let pageSize = 1000
    if (apiChartTimeRange.value === 'quarter') {
      pageSize = 5000
    } else if (apiChartTimeRange.value === 'year') {
      pageSize = 10000
    }

    const logData = await logApi.getList({ page: 1, pageSize })
    if (logData.data && logData.data.list) {
      initApiChart(logData.data.list, apiChartTimeRange.value)
    }
  } catch (error) {
    console.error('加载API图表数据失败:', error)
  }
}

// 切换API图表时间范围
const handleApiChartTimeRangeChange = (value) => {
  apiChartTimeRange.value = value
  loadApiChartData()
}

// 初始化API调用折线图
const initApiChart = (logs, timeRange = 'month') => {
  if (!apiChartContainer.value) return

  // 根据时间范围生成日期标签
  const dateLabels = []
  const dateMap = {}
  const today = new Date()

  if (timeRange === 'month') {
    // 月度：显示最近30天
    for (let i = 29; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0 }
    }
  } else if (timeRange === 'quarter') {
    // 季度：显示最近3个月，按周统计
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - (i * 7))
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay())
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)

      const dateStr = `${weekStart.getMonth() + 1}/${weekStart.getDate()}-${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: weekStart, endDate: weekEnd }
    }
  } else if (timeRange === 'year') {
    // 年度：显示最近12个月
    for (let i = 11; i >= 0; i--) {
      const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
      const dateStr = `${date.getFullYear()}/${date.getMonth() + 1}`
      dateLabels.push(dateStr)
      dateMap[dateStr] = { total: 0, success: 0, fail: 0, startDate: date, endDate: new Date(date.getFullYear(), date.getMonth() + 1, 0) }
    }
  }

  // 统计API调用数量
  logs.forEach(log => {
    if (log.created_at) {
      const logDate = new Date(log.created_at)

      if (timeRange === 'month') {
        const dateStr = log.created_at.split('T')[0]
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }
      } else if (timeRange === 'quarter') {
        // 按周统计
        for (const label of dateLabels) {
          const range = dateMap[label]
          if (logDate >= range.startDate && logDate <= range.endDate) {
            range.total++
            if (log.status === 'success') {
              range.success++
            } else if (log.status === 'fail' || log.status === 'error') {
              range.fail++
            }
            break
          }
        }
      } else if (timeRange === 'year') {
        // 按月统计
        const dateStr = `${logDate.getFullYear()}/${logDate.getMonth() + 1}`
        if (dateMap.hasOwnProperty(dateStr)) {
          dateMap[dateStr].total++
          if (log.status === 'success') {
            dateMap[dateStr].success++
          } else if (log.status === 'fail' || log.status === 'error') {
            dateMap[dateStr].fail++
          }
        }
      }
    }
  })

  const totalValues = dateLabels.map(date => dateMap[date].total)
  const successValues = dateLabels.map(date => dateMap[date].success)
  const failValues = dateLabels.map(date => dateMap[date].fail)

  // 销毁旧图表
  if (apiChartInstance) {
    apiChartInstance.dispose()
  }

  // 创建新图表
  apiChartInstance = echarts.init(apiChartContainer.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: ['总调用', '成功', '失败'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dateLabels,
      axisLabel: {
        rotate: timeRange === 'year' ? 0 : 0,
        interval: timeRange === 'month' ? 4 : timeRange === 'quarter' ? 0 : 0
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [
      {
        name: '总调用',
        type: 'line',
        smooth: true,
        data: totalValues,
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '成功',
        type: 'line',
        smooth: true,
        data: successValues,
        itemStyle: {
          color: '#67c23a'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      },
      {
        name: '失败',
        type: 'line',
        smooth: true,
        data: failValues,
        itemStyle: {
          color: '#f56c6c'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }
  apiChartInstance.setOption(option)

  // 监听窗口大小变化
  window.addEventListener('resize', () => {
    apiChartInstance?.resize()
  })
}

// 所有快捷入口
const allShortcuts = [
  {
    id: 'testcases',
    title: '测试用例管理',
    icon: List,
    path: '/testing/testcases',
    desc: '查看和管理所有测试用例',
    color: '#409eff',
    permission: 'testcase:view'
  },
  {
    id: 'generate',
    title: '生成用例',
    icon: MagicStick,
    path: '/testing/generate',
    desc: '使用AI智能生成测试用例',
    color: '#67c23a',
    permission: 'ai:generate'
  },
  {
    id: 'requirements',
    title: '需求管理',
    icon: Document,
    path: '/testing/requirements',
    desc: '管理产品需求和文档',
    color: '#e6a23c',
    permission: 'requirement:view'
  },
  {
    id: 'prompts',
    title: '提示词管理',
    icon: ChatDotRound,
    path: '/testing/prompts',
    desc: '配置AI生成提示词',
    color: '#f56c6c',
    permission: 'prompt:view'
  },
  {
    id: 'knowledge',
    title: '知识库管理',
    icon: Collection,
    path: '/knowledge/knowledges',
    desc: '管理测试知识资产',
    color: '#909399',
    permission: 'knowledge:view'
  },
  {
    id: 'reviews',
    title: '用例评审',
    icon: TrendCharts,
    path: '/testing/reviews',
    desc: 'AI智能评审测试用例',
    color: '#8e44ad',
    permission: 'review:view'
  }
]

// 从本地存储加载用户快捷入口设置
const loadUserShortcuts = () => {
  const saved = localStorage.getItem('userShortcuts')
  if (saved) {
    userShortcuts.value = JSON.parse(saved)
  } else {
    // 默认显示前4个
    userShortcuts.value = allShortcuts.slice(0, 4).map(s => s.id)
  }
}

// 打开设置对话框时初始化选中状态
const openSettings = () => {
  selectedShortcut.value = ''
  shortcutSettingsVisible.value = true
}

// 切换快捷入口选择
const toggleShortcut = (shortcutId) => {
  const index = userShortcuts.value.indexOf(shortcutId)
  if (index > -1) {
    // 已选中，取消选中
    userShortcuts.value.splice(index, 1)
    selectedShortcut.value = ''
  } else {
    // 未选中，添加选中
    userShortcuts.value.push(shortcutId)
    selectedShortcut.value = shortcutId
  }
}

// 保存用户快捷入口设置
const saveUserShortcuts = () => {
  localStorage.setItem('userShortcuts', JSON.stringify(userShortcuts.value))
  shortcutSettingsVisible.value = false
}

// 根据权限和用户设置过滤快捷入口
const shortcuts = computed(() => {
  const permissions = permissionStore.permissions
  return allShortcuts.filter(shortcut => {
    // 检查权限
    if (!userStore.isAdmin && !permissions.includes(shortcut.permission)) {
      return false
    }
    // 检查用户是否选中
    return userShortcuts.value.includes(shortcut.id)
  })
})

// 跳转到快捷入口
const goToShortcut = (path) => {
  router.push(path)
}

// 获取需求状态标签
const getRequirementStatusLabel = (status) => {
  const labels = {
    draft: '草稿',
    active: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return labels[status] || status
}

// 获取需求状态颜色
const getRequirementStatusColor = (status) => {
  const colors = {
    draft: 'info',
    active: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return colors[status] || ''
}

onMounted(() => {
  loadUserShortcuts()
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
          <div class="stat-item">
            <div class="stat-number">{{ stats.todayApiCalls }}</div>
            <div class="stat-label">今日API调用</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">{{ stats.totalApiCalls }}</div>
            <div class="stat-label">总API调用</div>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 快捷入口 -->
    <el-card class="shortcuts-card">
      <template #header>
        <div class="card-header">
          <span>快捷入口</span>
          <el-button type="primary" link @click="openSettings">
            <el-icon><Setting /></el-icon>
            设置
          </el-button>
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

    <!-- 数据趋势图表 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span>最近7天用例趋势</span>
        </div>
      </template>
      <div ref="chartContainer" class="chart-container"></div>
    </el-card>

    <!-- API调用趋势图表 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <div class="chart-title">
            <span>API调用趋势</span>
            <el-radio-group v-model="apiChartTimeRange" size="small" @change="handleApiChartTimeRangeChange">
              <el-radio-button label="month">月度</el-radio-button>
              <el-radio-button label="quarter">季度</el-radio-button>
              <el-radio-button label="year">年度</el-radio-button>
            </el-radio-group>
          </div>
          <div class="chart-stats">
            <el-tag type="success" size="small">成功: {{ stats.successApiCalls }}</el-tag>
            <el-tag type="danger" size="small">失败: {{ stats.failApiCalls }}</el-tag>
          </div>
        </div>
      </template>
      <div ref="apiChartContainer" class="chart-container"></div>
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

      <!-- 最近需求 -->
      <el-card class="requirements-card">
        <template #header>
          <div class="card-header">
            <span>最近需求</span>
            <el-button type="primary" link @click="router.push('/testing/requirements')">
              查看全部
              <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        <div class="requirements-list">
          <div v-if="recentRequirements.length === 0" class="empty-state">
            <el-icon :size="48" color="#909399">
              <Document />
            </el-icon>
            <p>暂无需求文档</p>
          </div>
          <div
            v-for="item in recentRequirements"
            :key="item.id"
            class="requirement-item"
            @click="router.push('/testing/requirements')"
          >
            <div class="requirement-info">
              <h4>{{ item.title }}</h4>
              <p>{{ item.module || '未分类' }} | {{ item.priority }}</p>
            </div>
            <el-tag :type="getRequirementStatusColor(item.status)" size="small">
              {{ getRequirementStatusLabel(item.status) }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 快捷入口设置对话框 -->
    <el-dialog
      v-model="shortcutSettingsVisible"
      title="快捷入口设置"
      width="720px"
      :close-on-click-modal="false"
      class="shortcut-settings-dialog"
    >
      <template #header>
        <div class="dialog-header">
          <div class="header-icon">
            <el-icon :size="24"><Setting /></el-icon>
          </div>
          <div class="header-text">
            <h3>快捷入口设置</h3>
            <p>自定义您的工作台快捷入口</p>
          </div>
        </div>
      </template>
      <div class="shortcut-settings">
        <div class="settings-tip">
          <el-icon :size="16" color="#409eff"><InfoFilled /></el-icon>
          <span>点击卡片即可添加到快捷入口，至少选择2个，最多可选择全部{{ allShortcuts.length }}个</span>
        </div>
        <div class="selected-count">
          <span>已选择：</span>
          <span class="count-number">{{ userShortcuts.length }}</span>
          <span class="count-total"> / {{ allShortcuts.length }}</span>
        </div>
        <div class="shortcut-options">
          <div
            v-for="shortcut in allShortcuts"
            :key="shortcut.id"
            class="shortcut-option"
            :class="{ 
              'selected': userShortcuts.includes(shortcut.id),
              'disabled': !userStore.isAdmin && !permissionStore.permissions.includes(shortcut.permission)
            }"
            @click="(!userStore.isAdmin && !permissionStore.permissions.includes(shortcut.permission)) ? null : toggleShortcut(shortcut.id)"
          >
            <div class="option-checkbox">
              <el-icon v-if="userShortcuts.includes(shortcut.id)" :size="18" color="#409eff">
                <component :is="'Select'" />
              </el-icon>
            </div>
            <div class="option-icon" :style="{ backgroundColor: shortcut.color }">
              <el-icon :size="32">
                <component :is="shortcut.icon" />
              </el-icon>
            </div>
            <div class="option-content">
              <div class="option-title">{{ shortcut.title }}</div>
              <div class="option-desc">{{ shortcut.desc }}</div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button size="large" @click="shortcutSettingsVisible = false" class="cancel-btn">
            取消
          </el-button>
          <el-button
            size="large"
            type="primary"
            @click="saveUserShortcuts"
            :disabled="userShortcuts.length < 2"
            class="save-btn"
          >
            保存设置
          </el-button>
        </div>
      </template>
    </el-dialog>
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
  gap: 30px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
  min-width: 80px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 13px;
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

.chart-card {
  margin-bottom: 0;
}

.chart-container {
  width: 100%;
  height: 300px;
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 15px;
  flex: 1;

  span {
    font-weight: 600;
  }
}

.chart-stats {
  display: flex;
  gap: 10px;
  align-items: center;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.recent-card,
.requirements-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.recent-list,
.requirements-list {
  min-height: 200px;
}

.recent-item,
.requirement-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.recent-item:hover,
.requirement-item:hover {
  background-color: #f5f7fa;
}

.recent-item:last-child,
.requirement-item:last-child {
  border-bottom: none;
}

.recent-info,
.requirement-info h4 {
  margin: 0 0 5px 0;
  font-size: 14px;
  color: #303133;
}

.recent-info p,
.requirement-info p {
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

/* 快捷入口设置对话框样式 */
.shortcut-settings-dialog :deep(.el-dialog__header) {
  padding: 0;
  margin: 0;
  border-bottom: 1px solid #e8eaed;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.header-text h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.3;
}

.header-text p {
  margin: 0;
  font-size: 13px;
  opacity: 0.9;
  line-height: 1.4;
}

.shortcut-settings-dialog :deep(.el-dialog__body) {
  padding: 28px;
  background: #f8f9fb;
}

.shortcut-settings-dialog :deep(.el-dialog__footer) {
  padding: 20px 28px;
  border-top: 1px solid #e8eaed;
  background: #ffffff;
}

.shortcut-settings {
  background: #f8f9fb;
}

.settings-tip {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px 0;
  padding: 14px 18px;
  background: linear-gradient(135deg, #e7f5ff 0%, #f0f9ff 100%);
  border-radius: 8px;
  border: 1px solid #b8e0ff;
  font-size: 14px;
  color: #495057;
  line-height: 1.6;
  box-shadow: 0 1px 3px rgba(64, 158, 255, 0.08);
}

.selected-count {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-bottom: 20px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #495057;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.count-number {
  font-size: 24px;
  font-weight: 700;
  color: #409eff;
  margin: 0 2px;
}

.count-total {
  color: #868e96;
  font-size: 14px;
}

.shortcut-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  max-height: 450px;
  overflow-y: auto;
  padding: 2px;
}

.shortcut-options::-webkit-scrollbar {
  width: 8px;
}

.shortcut-options::-webkit-scrollbar-track {
  background: #e9ecef;
  border-radius: 4px;
}

.shortcut-options::-webkit-scrollbar-thumb {
  background: #adb5bd;
  border-radius: 4px;
  transition: background 0.3s;
}

.shortcut-options::-webkit-scrollbar-thumb:hover {
  background: #868e96;
}

.option-checkbox {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 24px;
  height: 24px;
  border: 2px solid #d0d5dd;
  border-radius: 6px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
  z-index: 2;
}

.shortcut-option:hover .option-checkbox {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.shortcut-option.selected .option-checkbox {
  background-color: #409eff;
  border-color: #409eff;
}

.shortcut-option {
  position: relative;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 18px;
  border: 2px solid #e3e6ea;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: white;
  cursor: pointer;
  min-height: 100px;
  width: 100%;
  box-sizing: border-box;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.shortcut-option:hover {
  background: #fafbfc;
  border-color: #c3cdd8;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.shortcut-option.selected {
  background: linear-gradient(135deg, #e7f5ff 0%, #f0f9ff 100%);
  border-color: #409eff;
  box-shadow: 0 4px 16px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.option-icon {
  width: 58px;
  height: 58px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.shortcut-option:hover .option-icon {
  transform: scale(1.05);
}

.option-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.option-title {
  font-size: 15px;
  font-weight: 600;
  color: #212529;
  line-height: 1.4;
}

.option-desc {
  font-size: 12px;
  color: #868e96;
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}



.shortcut-option.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f1f3f5;
  border-color: #e9ecef;
}

.shortcut-option.disabled:hover {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transform: none;
}

.shortcut-option.disabled .option-checkbox {
  background-color: #f1f3f5;
  border-color: #d0d5dd;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.cancel-btn,
.save-btn {
  min-width: 110px;
  height: 42px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.3s ease;
}

.cancel-btn {
  border: 1px solid #d0d5dd;
  background: white;
  color: #495057;
}

.cancel-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #e9ecef;
  color: #adb5bd;
  box-shadow: none;
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
