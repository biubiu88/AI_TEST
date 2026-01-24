<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { permissionApi } from '@/api'

// 搜索参数
const searchForm = reactive({
  status: ''
})

// 对话框相关
const dialogVisible = ref(false)
const dialogTitle = ref('新建菜单')
const isEdit = ref(false)
const formRef = ref(null)

const formData = reactive({
  id: null,
  parent_id: 0,
  name: '',
  path: '',
  component: '',
  redirect: '',
  icon: '',
  title: '',
  hidden: false,
  alwaysShow: false,
  keepAlive: false,
  sort: 0,
  type: 'menu',
  permission: '',
  status: 1
})

const formRules = {
  name: [{ required: true, message: '请输入菜单名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择菜单类型', trigger: 'change' }]
}

// 菜单选项
const typeOptions = [
  { label: '目录', value: 'directory' },
  { label: '菜单', value: 'menu' },
  { label: '按钮', value: 'button' }
]

const statusOptions = [
  { label: '启用', value: 1 },
  { label: '禁用', value: 0 }
]

// 菜单列表
const menuList = ref([])
const allMenus = ref([])

// 加载数据
const loadData = async () => {
  try {
    const res = await permissionApi.getMenus()
    menuList.value = res.data || []
    
    // 获取所有菜单（包括禁用的）用于选择父菜单
    const allRes = await permissionApi.getAllMenus()
    allMenus.value = allRes.data || []
  } catch (error) {
    console.error('获取菜单列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  loadData()
}

// 重置搜索
const handleReset = () => {
  searchForm.status = ''
  loadData()
}

// 新建菜单
const handleAdd = (row = null) => {
  dialogTitle.value = '新建菜单'
  isEdit.value = false
  resetForm()
  
  // 如果点击了子菜单按钮，设置父菜单
  if (row) {
    formData.parent_id = row.id
    formData.type = row.type === 'directory' ? 'menu' : 'button'
  }
  
  dialogVisible.value = true
}

// 编辑菜单
const handleEdit = (row) => {
  dialogTitle.value = '编辑菜单'
  isEdit.value = true

  formData.id = row.id
  formData.parent_id = row.parent_id || row.parentId
  formData.name = row.name
  formData.path = row.path
  formData.component = row.component
  formData.redirect = row.redirect
  formData.icon = row.meta?.icon || row.icon
  formData.title = row.meta?.title || row.title || row.name
  formData.hidden = row.meta?.hidden || row.hidden || false
  formData.alwaysShow = row.meta?.alwaysShow || row.alwaysShow || false
  formData.keepAlive = row.meta?.keepAlive || row.keepAlive || false
  formData.sort = row.sort || 0
  formData.type = row.type
  formData.permission = row.meta?.permission || row.permission || ''
  formData.status = row.status

  dialogVisible.value = true
}

// 删除菜单
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除菜单"${row.title || row.name}"吗？`,
      '提示',
      { type: 'warning' }
    )
    await permissionApi.deleteMenu(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

// 重置表单
const resetForm = () => {
  formData.id = null
  formData.parent_id = 0
  formData.name = ''
  formData.path = ''
  formData.component = ''
  formData.redirect = ''
  formData.icon = ''
  formData.title = ''
  formData.hidden = false
  formData.alwaysShow = false
  formData.keepAlive = false
  formData.sort = 0
  formData.type = 'menu'
  formData.permission = ''
  formData.status = 1
  formRef.value?.resetFields()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    const submitData = {
      parentId: formData.parent_id,
      name: formData.name,
      path: formData.path,
      component: formData.component,
      redirect: formData.redirect,
      icon: formData.icon,
      title: formData.title || formData.name,
      hidden: formData.hidden,
      alwaysShow: formData.alwaysShow,
      keepAlive: formData.keepAlive,
      sort: formData.sort,
      type: formData.type,
      permission: formData.permission,
      status: formData.status
    }
    
    if (isEdit.value) {
      await permissionApi.updateMenu(formData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await permissionApi.createMenu(submitData)
      ElMessage.success('创建成功')
    }
    
    dialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
  }
}

// 获取菜单类型标签
const getTypeLabel = (type) => {
  const labels = {
    directory: '目录',
    menu: '菜单',
    button: '按钮'
  }
  return labels[type] || type
}

// 获取菜单类型标签样式
const getTypeType = (type) => {
  const types = {
    directory: 'primary',
    menu: 'success',
    button: 'info'
  }
  return types[type] || 'info'
}

// 获取状态标签
const getStatusLabel = (status) => {
  return status === 1 ? '启用' : '禁用'
}

// 获取状态标签样式
const getStatusType = (status) => {
  return status === 1 ? 'success' : 'info'
}

// 父级菜单选项（排除自己和子菜单）
const parentMenuOptions = computed(() => {
  const buildOptions = (menus, level = 0) => {
    const options = []
    menus.forEach(menu => {
      // 排除自己和子菜单（编辑时）
      if (isEdit.value && (menu.id === formData.id || isChildOf(menu.id, formData.id))) {
        return
      }
      
      const prefix = '　'.repeat(level)
      options.push({
        label: `${prefix}${menu.title || menu.name}`,
        value: menu.id
      })
      
      if (menu.children && menu.children.length > 0) {
        options.push(...buildOptions(menu.children, level + 1))
      }
    })
    return options
  }
  
  // 添加根目录选项
  return [
    { label: '作为顶级菜单', value: 0 },
    ...buildOptions(menuList.value)
  ]
})

// 判断是否是子菜单
const isChildOf = (parentId, childId) => {
  if (parentId === childId) return true
  
  const findInChildren = (menus, targetId) => {
    for (const menu of menus) {
      if (menu.id === targetId) return true
      if (menu.children && menu.children.length > 0) {
        if (findInChildren(menu.children, targetId)) return true
      }
    }
    return false
  }
  
  return findInChildren(menuList.value, childId)
}

// 根据菜单类型禁用某些字段
const isDirectory = computed(() => formData.type === 'directory')
const isButton = computed(() => formData.type === 'button')

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="menu-view">
    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
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
          <span>菜单列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新建菜单
          </el-button>
        </div>
      </template>

      <!-- 数据表格 -->
      <el-table
        :data="menuList"
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        stripe
        border
      >
        <el-table-column prop="title" label="菜单名称" min-width="200">
          <template #default="{ row }">
            <el-icon v-if="row.meta?.icon || row.icon" style="margin-right: 5px">
              <component :is="row.meta?.icon || row.icon" />
            </el-icon>
            {{ row.meta?.title || row.title || row.name }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getTypeType(row.type)" size="small">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="路由路径" min-width="150" show-overflow-tooltip />
        <el-table-column prop="component" label="组件路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="icon" label="图标" width="100" align="center">
          <template #default="{ row }">
            <el-icon v-if="row.meta?.icon || row.icon">
              <component :is="row.meta?.icon || row.icon" />
            </el-icon>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              @click="handleAdd(row)"
              v-if="row.type !== 'button'"
            >
              添加子菜单
            </el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="上级菜单" prop="parent_id">
              <el-tree-select
                v-model="formData.parent_id"
                :data="allMenus"
                :props="{ label: 'title', children: 'children', value: 'id' }"
                placeholder="选择上级菜单"
                check-strictly
                :render-after-expand="false"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单类型" prop="type">
              <el-select v-model="formData.type" style="width: 100%">
                <el-option
                  v-for="opt in typeOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="菜单名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入菜单名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="菜单标题" prop="title">
              <el-input v-model="formData.title" placeholder="请输入菜单标题" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="!isButton">
          <el-col :span="12">
            <el-form-item label="路由路径" prop="path">
              <el-input v-model="formData.path" placeholder="例如: /system/menu" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="组件路径" prop="component" v-if="!isDirectory">
              <el-input v-model="formData.component" placeholder="例如: @/views/MenuView.vue" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="图标" prop="icon">
              <el-input v-model="formData.icon" placeholder="例如: Menu" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number v-model="formData.sort" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="重定向" prop="redirect" v-if="isDirectory">
          <el-input v-model="formData.redirect" placeholder="例如: /system/menu" />
        </el-form-item>

        <el-form-item label="权限标识" prop="permission">
          <el-input v-model="formData.permission" placeholder="例如: system:menu:edit" />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="状态">
              <el-switch
                v-model="formData.status"
                :active-value="1"
                :inactive-value="0"
                active-text="启用"
                inactive-text="禁用"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8" v-if="!isButton">
            <el-form-item label="隐藏菜单">
              <el-switch v-model="formData.hidden" />
            </el-form-item>
          </el-col>
          <el-col :span="8" v-if="isDirectory">
            <el-form-item label="始终显示">
              <el-switch v-model="formData.alwaysShow" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="缓存页面" v-if="!isButton && !isDirectory">
          <el-switch v-model="formData.keepAlive" />
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
.menu-view {
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
</style>
