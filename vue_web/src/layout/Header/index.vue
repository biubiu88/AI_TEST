<template>
  <header>
    <div class="left-box">
      <!-- 收缩按钮 -->
      <div class="menu-icon" @click="toggleCollapse">
        <el-icon :size="20">
          <component :is="isCollapse ? 'Expand' : 'Fold'" />
        </el-icon>
      </div>
      <!-- 面包屑导航 -->
      <el-breadcrumb separator="/" v-if="isBreadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>{{ route.meta.title || '页面' }}</el-breadcrumb-item>
      </el-breadcrumb>
    </div>
    <div class="right-box">
      <!-- 快捷功能按钮 -->
      <div class="function-list">
        <div class="function-list-item">
          <el-tooltip content="全屏显示" placement="bottom">
            <el-icon class="function-icon" @click="toggleFullscreen">
              <FullScreen />
            </el-icon>
          </el-tooltip>
        </div>
        <div class="function-list-item">
          <el-tooltip content="主题设置" placement="bottom">
            <el-icon class="theme-settings-icon" @click="openThemeSettings">
              <Setting />
            </el-icon>
          </el-tooltip>
        </div>
      </div>
      <!-- 用户信息 -->
      <div class="user-info">
        <el-dropdown>
          <span class="el-dropdown-link">
            <el-avatar :size="28" style="margin-right: 8px;">
              <el-icon><User /></el-icon>
            </el-avatar>
            {{ userName }}
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="showProfile">个人中心</el-dropdown-item>
              <el-dropdown-item @click="showPasswordLayer">修改密码</el-dropdown-item>
              <el-dropdown-item divided @click="loginOut">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 修改密码弹窗 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm" label-width="80px">
        <el-form-item label="原密码">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="changePassword">确定</el-button>
      </template>
    </el-dialog>
  </header>
</template>

<script setup>
import { computed, ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useThemeConfigStore } from '@/stores/themeConfig'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Setting, FullScreen, User, ArrowDown } from '@element-plus/icons-vue'

const emit = defineEmits(['openThemeSettings'])

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const themeConfigStore = useThemeConfigStore()
const userStore = useUserStore()

const userName = computed(() => {
  return userStore.userInfo?.nickname || userStore.userInfo?.username || localStorage.getItem('userName') || '用户'
})
const isCollapse = computed(() => appStore.isCollapse)
const isBreadcrumb = computed(() => themeConfigStore.isBreadcrumb !== false)

// 修改密码相关
const passwordDialogVisible = ref(false)
const passwordLoading = ref(false)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 切换收缩状态
const toggleCollapse = () => {
  appStore.toggleCollapse()
}

// 退出登录
const loginOut = async () => {
  await userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

// 显示修改密码弹窗
const showPasswordLayer = () => {
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordDialogVisible.value = true
}

// 修改密码
const changePassword = async () => {
  if (!passwordForm.oldPassword || !passwordForm.newPassword || !passwordForm.confirmPassword) {
    ElMessage.warning('请填写完整信息')
    return
  }
  if (passwordForm.newPassword.length < 6) {
    ElMessage.warning('新密码长度不能少于6位')
    return
  }
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  
  passwordLoading.value = true
  try {
    await userStore.changePassword(passwordForm)
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
  } catch (error) {
    // 错误已在拦截器中处理
  } finally {
    passwordLoading.value = false
  }
}

// 个人中心
const showProfile = () => {
  ElMessage.info('个人中心功能开发中')
}

// 打开主题设置
const openThemeSettings = () => {
  emit('openThemeSettings')
}

// 切换全屏
const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen()
    }
  }
}
</script>

<style lang="scss" scoped>
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  background-color: var(--theme-topBar, var(--system-header-background, #ffffff));
  color: var(--theme-topBarColor, var(--system-header-text-color, #606266));
  padding: 0 20px;
  border-bottom: 1px solid #e8e8e8;
  transition: all 0.3s ease;
}

.left-box {
  height: 100%;
  display: flex;
  align-items: center;

  .menu-icon {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 4px;
    margin-right: 10px;
    transition: background-color 0.3s;

    &:hover {
      background-color: var(--system-header-item-hover-color, #f5f5f5);
    }

    .el-icon {
      color: var(--system-header-text-color, #606266);
    }
  }
  
  :deep(.el-breadcrumb) {
    .el-breadcrumb__item {
      .el-breadcrumb__inner {
        color: var(--system-header-text-color, #606266);
      }
    }
  }
}

.right-box {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-left: auto;

  .function-list {
    display: flex;

    .function-list-item {
      width: 40px;
      height: 40px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: var(--system-header-item-hover-color, #f5f5f5);
      }

      .function-icon,
      .theme-settings-icon {
        font-size: 18px;
        color: var(--system-header-text-color, #606266);
        transition: color 0.3s;

        &:hover {
          color: var(--el-color-primary);
        }
      }
    }
  }

  .user-info {
    margin-left: 20px;

    .el-dropdown-link {
      display: flex;
      align-items: center;
      color: var(--system-header-text-color, #606266);
      cursor: pointer;
    }
  }
}
</style>
