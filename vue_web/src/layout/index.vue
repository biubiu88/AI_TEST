<template>
  <el-container class="layout-container">
    <div
      class="mask"
      v-show="!isCollapse && isMobile"
      @click="hideMenu"
    ></div>
    <el-aside
      :width="isCollapse ? '60px' : '200px'"
      :class="isCollapse ? 'hide-aside' : 'show-side'"
      v-show="!contentFullScreen"
    >
      <!-- 菜单上面的logo -->
      <Logo />
      <Menu />
    </el-aside>

    <el-container>
      <el-header v-show="!contentFullScreen">
        <Header @openThemeSettings="openThemeSettings" />
      </el-header>

      <el-main>
        <router-view v-slot="{ Component, route }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
    
    <!-- 主题设置组件 -->
    <ThemeSettings ref="themeSettingsRef" />
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { useAppStore } from '@/stores/app'
import Menu from './Menu/index.vue'
import Logo from './Logo/index.vue'
import Header from './Header/index.vue'
import ThemeSettings from '@/components/ThemeSettings/index.vue'

const appStore = useAppStore()
const themeSettingsRef = ref(null)
const isMobile = ref(false)

// computed
const isCollapse = computed(() => appStore.isCollapse)
const contentFullScreen = computed(() => appStore.contentFullScreen)

// 页面宽度变化监听后执行的方法
const resizeHandler = () => {
  isMobile.value = document.body.clientWidth <= 1000
  if (document.body.clientWidth <= 1000 && !isCollapse.value) {
    appStore.setCollapse(true)
  } else if (document.body.clientWidth > 1000 && isCollapse.value) {
    appStore.setCollapse(false)
  }
}

// 隐藏菜单
const hideMenu = () => {
  appStore.setCollapse(true)
}

// 打开主题设置
const openThemeSettings = () => {
  themeSettingsRef.value?.openDrawer()
}

onMounted(() => {
  resizeHandler()
  window.addEventListener('resize', resizeHandler)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeHandler)
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
  
  .el-header {
    padding: 0;
    height: 60px;
  }

  .el-aside {
    display: flex;
    flex-direction: column;
    transition: width 0.3s;
    overflow-x: hidden;
    background-color: var(--theme-menuBar, var(--system-menu-background, #2b2f3a));

    &::-webkit-scrollbar {
      width: 0 !important;
    }
  }

  .el-main {
    background-color: var(--system-container-background, #f5f5f5);
    height: 100%;
    padding: 20px;
    overflow-y: auto;
  }
}

// 路由切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.2s ease;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(10px);
}

@media screen and (max-width: 1000px) {
  .layout-container {
    .el-aside {
      position: fixed;
      top: 0;
      left: 0;
      height: 100vh;
      z-index: 1000;

      &.hide-aside {
        left: -250px;
      }
    }
    
    .mask {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 999;
      background: rgba(0, 0, 0, 0.5);
    }
  }
}
</style>
