<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { logApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  keyword: '',
  action: '',
  module: '',
  startTime: '',
  endTime: '',
  page: 1,
  per_page: 50
})

// 动作选项
const actionOptions = [
  { label: '登录', value: 'login' },
  { label: '登出', value: 'logout' },
  { label: '创建', value: 'create' },
  { label: '更新', value: 'update' },
  { label: '删除', value: 'delete' },
  { label: '查询', value: 'query' }
]

// 模块选项
const moduleOptions = [
  { label: '用户', value: 'user' },
  { label: '角色', value: 'role' },
  { label: '菜单', value: 'menu' },
  { label: '权限', value: 'permission' },
  { label: '需求', value: 'requirement' },
  { label: '用例', value: 'testcase' },
  { label: '提示词', value: 'prompt' },
  { label: '知识库', value: 'knowledge' },
  { label: '模型配置', value: 'llm' }
]

// 日志列表
const logList = ref([])
const total = ref(0)
const loading = ref(false)

// 模拟数据
const mockLogs = [
  {
    id: 1,
    user: 'admin',
    action: 'login',
    module: 'user',
    description: '用户登录系统',
    ip: '192.168.1.100',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    status: 'success',
    created_at: '2024-01-24 14:30:25'
  },
  {
    id: 2,
    user: 'admin',
    action: 'create',
    module: 'requirement',
    description: '创建需求"用户登录功能"',
    ip: '192.168.1.100',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    status: 'success',
    created_at: '2024-01-24 14:35:10'
  },
  {
    id: 3,
    user: 'admin',
    action: 'update',
    module: 'testcase',
    description: '更新测试用例#123',
    ip: '192.168.1.100',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    status: 'success',
    created_at: '2024-01-24 14:40:05'
  },
  {
    id: 4,
    user: 'testuser',
    action: 'login',
    module: 'user',
    description: '用户登录系统',
    ip: '192.168.1.101',
    browser: 'Firefox 121.0',
    os: 'MacOS 14',
    status: 'success',
    created_at: '2024-01-24 14:45:30'
  },
  {
    id: 5,
    user: 'admin',
    action: 'delete',
    module: 'testcase',
    description: '删除测试用例#456',
    ip: '192.168.1.100',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    status: 'success',
    created_at: '2024-01-24 14:50:15'
  },
  {
    id: 6,
    user: 'testuser',
    action: 'create',
    module: 'testcase',
    description: '创建测试用例"密码验证"',
    ip: '192.168.1.101',
    browser: 'Firefox 121.0',
    os: 'MacOS 14',
    status: 'success',
    created_at: '2024-01-24 14:55:20'
  },
  {
    id: 7,
    user: 'admin',
    action: 'update',
    module: 'menu',
    description: '更新菜单结构',
    ip: '192.168.1.100',
    browser: 'Chrome 120.0',
    os: 'Windows 11',
    status: 'success',
    created_at: '2024-01-24 15:00:05'
  },
  {
    id: 8,
    user: 'testuser',
    action: 'logout',
    module: 'user',
    description: '用户登出系统',
    ip: '192.168.1.101',
    browser: 'Firefox 121.0',
    os: 'MacOS 14',
    status: 'success',
    created_at: '2024-01-24 15:05:30'
  }
]

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await logApi.getList(searchForm)
    logList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('获取日志列表失败:', error)
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
  searchForm.action = ''
  searchForm.module = ''
  searchForm.startTime = ''
  searchForm.endTime = ''
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

// 导出日志
const handleExport = async () => {
  try {
    const res = await logApi.export(searchForm)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
  }
}

// 查看详情
const handleViewDetail = (row) => {
  const htmlContent = `
    <div style="text-align: left;">
      <p><strong>用户：</strong>${row.user}</p>
      <p><strong>动作：</strong>${row.action}</p>
      <p><strong>模块：</strong>${row.module}</p>
      <p><strong>描述：</strong>${row.description}</p>
      <p><strong>IP地址：</strong>${row.ip}</p>
      <p><strong>浏览器：</strong>${row.browser}</p>
      <p><strong>操作系统：</strong>${row.os}</p>
      <p><strong>状态：</strong>${row.status}</p>
      <p><strong>时间：</strong>${row.created_at}</p>
    </div>
  `

  ElMessageBox.alert(htmlContent, '日志详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭'
  })
}

// 获取动作标签
const getActionLabel = (action) => {
  const labels = {
    login: '登录',
    logout: '登出',
    create: '创建',
    update: '更新',
    delete: '删除',
    query: '查询'
  }
  return labels[action] || action
}

// 获取动作标签样式
const getActionType = (action) => {
  const types = {
    login: 'success',
    logout: 'info',
    create: 'primary',
    update: 'warning',
    delete: 'danger',
    query: 'info'
  }
  return types[action] || ''
}

// 获取状态标签
const getStatusLabel = (status) => {
  return status === 'success' ? '成功' : '失败'
}

// 获取状态标签样式
const getStatusType = (status) => {
  return status === 'success' ? 'success' : 'danger'
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="log-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户、描述等"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="动作">
          <el-select v-model="searchForm.action" placeholder="全部" clearable>
            <el-option
              v-for="opt in actionOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="searchForm.module" placeholder="全部" clearable>
            <el-option
              v-for="opt in moduleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.startTime"
            type="datetime"
            placeholder="开始时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
          <span style="margin: 0 10px">-</span>
          <el-date-picker
            v-model="searchForm.endTime"
            type="datetime"
            placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
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
          <el-button type="success" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作栏 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>日志列表</span>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="logList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="user" label="用户" width="100" />
        <el-table-column prop="action" label="动作" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column prop="browser" label="浏览器" width="120" show-overflow-tooltip />
        <el-table-column prop="os" label="操作系统" width="100" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row)">详情</el-button>
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
  </div>
</template>

<style scoped>
.log-view {
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
