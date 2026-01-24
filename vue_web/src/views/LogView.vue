<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { logApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  keyword: '',
  action: '',
  module: '',
  status: '',
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
  { label: '查询', value: 'query' },
  { label: '导出', value: 'export' },
  { label: '导入', value: 'import' }
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
  { label: '模型配置', value: 'llm_config' },
  { label: 'MCP配置', value: 'mcp_config' },
  { label: 'AI助手', value: 'ai_assistant' },
  { label: '日志', value: 'log' }
]

// 状态选项
const statusOptions = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'fail' },
  { label: '错误', value: 'error' }
]

// 日志列表
const logList = ref([])
const total = ref(0)
const loading = ref(false)

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
  searchForm.status = ''
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
    <div style="text-align: left; max-height: 500px; overflow-y: auto;">
      <h4 style="margin-top: 0;">基本信息</h4>
      <p><strong>用户：</strong>${row.username || '-'}</p>
      <p><strong>操作：</strong>${getActionLabel(row.action)}</p>
      <p><strong>模块：</strong>${row.module || '-'}</p>
      <p><strong>描述：</strong>${row.description || '-'}</p>
      <p><strong>状态：</strong><span style="color: ${row.status === 'success' ? '#67c23a' : '#f56c6c'}">${getStatusLabel(row.status)}</span></p>
      
      <h4>请求信息</h4>
      <p><strong>请求方法：</strong>${row.method || '-'}</p>
      <p><strong>请求路径：</strong>${row.path || '-'}</p>
      <p><strong>响应状态码：</strong>${row.status_code || '-'}</p>
      <p><strong>响应时间：</strong>${row.response_time ? row.response_time + 'ms' : '-'}</p>
      ${row.params ? `<p><strong>请求参数：</strong><pre style="background: #f5f5f5; padding: 8px; border-radius: 4px; max-height: 200px; overflow: auto;">${row.params}</pre></p>` : ''}
      ${row.error_msg ? `<p><strong>错误信息：</strong><span style="color: #f56c6c;">${row.error_msg}</span></p>` : ''}
      
      <h4>客户端信息</h4>
      <p><strong>IP地址：</strong>${row.ip || '-'}</p>
      <p><strong>浏览器：</strong>${row.browser || '-'} ${row.browser_version || ''}</p>
      <p><strong>操作系统：</strong>${row.os || '-'} ${row.os_version || ''}</p>
      <p><strong>设备类型：</strong>${getDeviceLabel(row.device)}</p>
      <p><strong>User-Agent：</strong><small style="word-break: break-all;">${row.user_agent || '-'}</small></p>
      
      <h4>时间信息</h4>
      <p><strong>创建时间：</strong>${row.created_at || '-'}</p>
    </div>
  `

  ElMessageBox.alert(htmlContent, '日志详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭',
    customClass: 'log-detail-dialog'
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

// 获取设备标签
const getDeviceLabel = (device) => {
  const labels = {
    desktop: '桌面端',
    mobile: '移动端',
    tablet: '平板'
  }
  return labels[device] || device || '-'
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
        <el-table-column prop="username" label="用户" width="100" />
        <el-table-column prop="action" label="动作" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="100" align="center" />
        <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="method" label="请求方法" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.method" :type="row.method === 'GET' ? 'success' : row.method === 'POST' ? 'primary' : row.method === 'DELETE' ? 'danger' : 'warning'" size="small">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="请求路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status_code" label="状态码" width="90" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status_code" :type="row.status_code < 300 ? 'success' : row.status_code < 400 ? 'warning' : 'danger'" size="small">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_time" label="响应时间" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.response_time" :style="{color: row.response_time > 1000 ? '#f56c6c' : row.response_time > 500 ? '#e6a23c' : '#67c23a'}">
              {{ row.response_time }}ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column label="浏览器" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.browser }} {{ row.browser_version }}
          </template>
        </el-table-column>
        <el-table-column label="操作系统" width="120" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.os }} {{ row.os_version }}
          </template>
        </el-table-column>
        <el-table-column prop="device" label="设备" width="80" align="center">
          <template #default="{ row }">
            {{ getDeviceLabel(row.device) }}
          </template>
        </el-table-column>
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
