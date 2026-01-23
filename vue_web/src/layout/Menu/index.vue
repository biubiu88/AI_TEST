<template>
  <el-scrollbar>
    <el-menu
      class="layout-menu"
      :background-color="menuBackgroundColor"
      :text-color="menuTextColor"
      :active-text-color="menuActiveTextColor"
      :default-active="activeMenu"
      :class="isCollapse ? 'collapse' : ''"
      :collapse="isCollapse"
      :collapse-transition="false"
      :unique-opened="expandOneMenu"
      @select="handleMenuSelect"
    >
      <template v-for="item in menuList" :key="item.path || item.name">
        <!-- 有子菜单 -->
        <el-sub-menu v-if="item.children && item.children.length > 0 && !item.meta?.hidden" :index="item.path || item.name">
          <template #title>
            <el-icon v-if="item.meta?.icon">
              <component :is="item.meta.icon" />
            </el-icon>
            <span>{{ item.meta?.title || item.name }}</span>
          </template>
          <menu-item :menu-list="item.children" />
        </el-sub-menu>
        <!-- 无子菜单 -->
        <el-menu-item v-else-if="!item.meta?.hidden" :index="item.path">
          <el-icon v-if="item.meta?.icon">
            <component :is="item.meta.icon" />
          </el-icon>
          <template #title>{{ item.meta?.title || item.name }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </el-scrollbar>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { usePermissionStore } from '@/stores/permission'
import { defaultAsyncRoutes } from '@/router'
import MenuItem from './MenuItem.vue'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()
const permissionStore = usePermissionStore()

const isCollapse = computed(() => appStore.isCollapse)
const expandOneMenu = computed(() => appStore.expandOneMenu)

// 菜单配置 - 优先使用动态菜单，没有则使用默认菜单
const menuList = computed(() => {
  if (permissionStore.menus.length > 0) {
    // 使用动态菜单
    return permissionStore.menus
  }
  // 使用默认菜单
  return defaultAsyncRoutes[0]?.children || []
})

// 主题配置相关的计算属性
const menuBackgroundColor = computed(() => {
  return 'transparent'
})

const menuTextColor = computed(() => {
  return '#eaeaea'
})

const menuActiveTextColor = computed(() => {
  return '#409eff'
})

const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})

const handleMenuSelect = (path) => {
  router.push(path)
}
</script>

<style lang="scss" scoped>
.el-scrollbar {
  background-color: var(--theme-menuBar, #2b2f3a);
  flex: 1;
}

.layout-menu {
  width: 100%;
  border: none;
  background-color: transparent;
  
  &.collapse {
    margin-left: 0px;
    
    :deep(.el-menu-item) {
      padding: 0 20px !important;
      justify-content: center;
      
      .el-icon {
        margin-right: 0 !important;
      }
    }
  }
  
  :deep() {
    .el-menu-item {
      background-color: transparent !important;
      color: var(--theme-menuBarColor, #eaeaea) !important;
      height: 50px;
      line-height: 50px;
      
      .el-icon {
        color: var(--theme-menuBarColor, #eaeaea) !important;
        font-size: 18px;
        margin-right: 10px;
      }
      
      &.is-active {
        background-color: var(--theme-menuBarActiveColor, #409eff) !important;
        color: #ffffff !important;
        
        .el-icon {
          color: #ffffff !important;
        }
      }
      
      &:hover:not(.is-active) {
        background-color: var(--theme-menuBar-light-1, #2f3349) !important;
      }
    }
  }
}
</style>
