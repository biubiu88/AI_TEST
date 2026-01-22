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
      <template v-for="item in menuItems" :key="item.path">
        <el-menu-item :index="item.path">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </template>
    </el-menu>
  </el-scrollbar>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const route = useRoute()
const appStore = useAppStore()

const isCollapse = computed(() => appStore.isCollapse)
const expandOneMenu = computed(() => appStore.expandOneMenu)

// 菜单配置
const menuItems = [
  {
    path: '/requirements',
    icon: 'Document',
    title: '需求管理'
  },
  {
    path: '/testcases',
    icon: 'List',
    title: '测试用例'
  },
  {
    path: '/generate',
    icon: 'MagicStick',
    title: '生成用例'
  },
  {
    path: '/prompts',
    icon: 'ChatDotRound',
    title: '提示词管理'
  },
  {
    path: '/knowledges',
    icon: 'Collection',
    title: '知识库管理'
  }
]

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
