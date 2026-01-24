<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { permissionApi, userApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  keyword: '',
  status: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建用户')
const isEdit = ref(false)
const formRef = ref(null)

// 角色对话框
const roleDialogVisible = ref(false)
const currentUser = ref(null)
const selectedRoles = ref([])

const formData = reactive({
  id: null,
  username: '',
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  status: 'active'
})

const formRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== formData.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 状态选项
const statusOptions = [
  { label: '启用', value: 'active' },
  { label: '禁用', value: 'inactive' },
  { label: '封禁', value: 'banned' }
]

// 用户列表
const userList = ref([])
const total = ref(0)
const loading = ref(false)

// 所有角色列表
const allRoles = ref([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await userApi.getList(searchForm)
    userList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('获取用户列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载角色列表
const loadRoles = async () => {
  try {
    const res = await permissionApi.getAllRoles()
    allRoles.value = res.data || []
  } catch (error) {
    console.error('获取角色列表失败:', error)
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

// 新建用户
const handleAdd = () => {
  dialogTitle.value = '新建用户'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑用户
const handleEdit = (row) => {
  dialogTitle.value = '编辑用户'
  isEdit.value = true
  Object.assign(formData, row)
  formData.password = ''
  formData.confirmPassword = ''
  dialogVisible.value = true
}

// 删除用户
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户"${row.username}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await userApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 管理角色
const handleManageRoles = async (row) => {
  currentUser.value = row
  try {
    const res = await permissionApi.getUserRoles(row.id)
    selectedRoles.value = (res.data || []).map(r => r.id)
    roleDialogVisible.value = true
  } catch (error) {
    console.error('获取用户角色失败:', error)
  }
}

// 保存角色
const handleSaveRoles = async () => {
  if (!currentUser.value) return

  try {
    await permissionApi.setUserRoles(currentUser.value.id, selectedRoles.value)
    ElMessage.success('角色分配成功')
    roleDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('分配角色失败:', error)
  }
}

// 重置密码
const handleResetPassword = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入新密码', '重置密码', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /^.{6,}$/,
      inputErrorMessage: '密码长度不能少于6位'
    })
    await userApi.resetPassword(row.id, value)
    ElMessage.success('密码重置成功')
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.username = ''
  formData.email = ''
  formData.nickname = ''
  formData.password = ''
  formData.confirmPassword = ''
  formData.status = 'active'
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    // 编辑时如果密码为空，不更新密码
    const submitData = {
      username: formData.username,
      email: formData.email,
      nickname: formData.nickname,
      status: formData.status
    }

    if (!isEdit.value || formData.password) {
      submitData.password = formData.password
    }

    if (isEdit.value) {
      await userApi.update(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await userApi.create(submitData)
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
  const labels = {
    active: '启用',
    inactive: '禁用',
    banned: '封禁'
  }
  return labels[status] || status
}

// 获取状态标签样式
const getStatusType = (status) => {
  const types = {
    active: 'success',
    inactive: 'info',
    banned: 'danger'
  }
  return types[status] || ''
}

onMounted(() => {
  loadData()
  loadRoles()
})
</script>

<template>
  <div class="user-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索用户名、邮箱或昵称"
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
          <span>用户列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建用户
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="userList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="nickname" label="昵称" width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" />
        <el-table-column prop="roles" label="角色" width="180">
          <template #default="{ row }">
            <el-tag
              v-for="role in row.roles"
              :key="role.code"
              size="small"
              style="margin-right: 5px"
            >
              {{ role.name }}
            </el-tag>
            <span v-if="!row.roles || row.roles.length === 0">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ row.created_at?.replace('T', ' ').slice(0, 19) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleManageRoles(row)">管理角色</el-button>
            <el-button type="warning" link @click="handleResetPassword(row)">重置密码</el-button>
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
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="formData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="formData.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit || formData.password">
          <el-input
            v-model="formData.password"
            type="password"
            placeholder="请输入密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword" v-if="!isEdit || formData.password">
          <el-input
            v-model="formData.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
          />
        </el-form-item>
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 角色管理对话框 -->
    <el-dialog
      v-model="roleDialogVisible"
      title="管理角色"
      width="500px"
      destroy-on-close
    >
      <div class="role-manage">
        <p>为用户 <strong>{{ currentUser?.username }}</strong> 分配角色：</p>
        <el-checkbox-group v-model="selectedRoles">
          <el-checkbox
            v-for="role in allRoles"
            :key="role.id"
            :label="role.id"
            :disabled="role.code === 'admin' && currentUser?.username === 'admin'"
          >
            {{ role.name }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveRoles">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-view {
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

.role-manage p {
  margin-bottom: 20px;
  font-size: 14px;
}

.role-manage .el-checkbox {
  display: block;
  margin-bottom: 10px;
}
</style>
