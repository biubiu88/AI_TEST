<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { permissionApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  keyword: '',
  status: '',
  page: 1,
  per_page: 50
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建角色')
const isEdit = ref(false)
const formRef = ref(null)

// 权限对话框
const permDialogVisible = ref(false)
const currentRole = ref(null)
const allPermissions = ref([])
const selectedPermissions = ref([])

const formData = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  status: 1,
  sort: 0
})

const formRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '角色编码只能包含字母、数字和下划线', trigger: 'blur' }
  ]
}

// 状态选项
const statusOptions = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 }
]

// 角色列表
const roleList = ref([])
const total = ref(0)
const loading = ref(false)

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await permissionApi.getRoles(searchForm)
    roleList.value = res.data.list
    total.value = res.data.total
  } catch (error) {
    console.error('获取角色列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载权限列表
const loadPermissions = async () => {
  try {
    const res = await permissionApi.getAllPermissions()
    allPermissions.value = res.data || []
  } catch (error) {
    console.error('获取权限列表失败:', error)
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

// 新建角色
const handleAdd = () => {
  dialogTitle.value = '新建角色'
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

// 编辑角色
const handleEdit = (row) => {
  dialogTitle.value = '编辑角色'
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除角色
const handleDelete = async (row) => {
  if (row.code === 'admin') {
    ElMessage.warning('系统角色不可删除')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要删除角色"${row.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await permissionApi.deleteRole(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 管理权限
const handleManagePermissions = async (row) => {
  currentRole.value = row
  try {
    const res = await permissionApi.getRole(row.id)
    selectedPermissions.value = (res.data?.permissions || []).map(p => p.id)
    permDialogVisible.value = true
  } catch (error) {
    console.error('获取角色权限失败:', error)
  }
}

// 保存权限
const handleSavePermissions = async () => {
  if (!currentRole.value) return

  try {
    const submitData = {
      name: currentRole.value.name,
      code: currentRole.value.code,
      description: currentRole.value.description,
      status: currentRole.value.status,
      sort: currentRole.value.sort,
      permissions: selectedPermissions.value
    }

    await permissionApi.updateRole(currentRole.value.id, submitData)
    ElMessage.success('权限分配成功')
    permDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('分配权限失败:', error)
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.status = 1
  formData.sort = 0
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    const submitData = {
      name: formData.name,
      code: formData.code,
      description: formData.description,
      status: formData.status,
      sort: formData.sort
    }

    if (isEdit.value) {
      await permissionApi.updateRole(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await permissionApi.createRole(submitData)
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

// 权限分组
const groupedPermissions = computed(() => {
  const groups = {}
  allPermissions.value.forEach(perm => {
    // 根据权限编码的前缀分组
    const prefix = perm.code.split(':')[0] || 'other'
    if (!groups[prefix]) {
      groups[prefix] = []
    }
    groups[prefix].push(perm)
  })
  return groups
})

onMounted(() => {
  loadData()
  loadPermissions()
})
</script>

<template>
  <div class="role-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索角色名称或编码"
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
          <span>角色列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建角色
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="roleList"
        v-loading="loading"
        stripe
        border
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="角色名称" width="150" />
        <el-table-column prop="code" label="角色编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="80" align="center">
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
        <el-table-column label="操作" width="240" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleManagePermissions(row)">管理权限</el-button>
            <el-button
              type="danger"
              link
              @click="handleDelete(row)"
              :disabled="row.code === 'admin'"
            >
              删除
            </el-button>
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
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input
            v-model="formData.code"
            placeholder="请输入角色编码（英文）"
            :disabled="isEdit && formData.code === 'admin'"
          />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number v-model="formData.sort" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
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
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 权限管理对话框 -->
    <el-dialog
      v-model="permDialogVisible"
      title="管理权限"
      width="700px"
      destroy-on-close
    >
      <div class="perm-manage">
        <p>为角色 <strong>{{ currentRole?.name }}</strong> 分配权限：</p>
        <el-checkbox-group v-model="selectedPermissions">
          <div v-for="(perms, group) in groupedPermissions" :key="group" class="perm-group">
            <h4>{{ group }}</h4>
            <el-checkbox
              v-for="perm in perms"
              :key="perm.id"
              :label="perm.id"
            >
              {{ perm.name }}
            </el-checkbox>
          </div>
        </el-checkbox-group>
      </div>
      <template #footer>
        <el-button @click="permDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSavePermissions">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.role-view {
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

.perm-manage p {
  margin-bottom: 20px;
  font-size: 14px;
}

.perm-group {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.perm-group h4 {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #606266;
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 10px;
}

.perm-group .el-checkbox {
  display: inline-block;
  margin-right: 20px;
  margin-bottom: 10px;
}
</style>
