<template>
  <div class="logo-container" v-if="isShowLogo">
    <div v-if="!isCollapse" class="logo-full">
      <el-icon :size="28" color="#409eff">
        <MagicStick />
      </el-icon>
      <h1 class="logo-text">{{ logoText }}</h1>
    </div>
    <div v-else class="logo-icon">
      <el-icon :size="24" color="#409eff">
        <MagicStick />
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { useThemeConfigStore } from '@/stores/themeConfig'
import { MagicStick } from '@element-plus/icons-vue'

const appStore = useAppStore()
const themeConfigStore = useThemeConfigStore()

const isCollapse = computed(() => appStore.isCollapse)

const isShowLogo = computed(() => {
  return themeConfigStore.isShowLogo !== false
})

const logoText = computed(() => {
  return themeConfigStore.logoText || 'TestCase AI'
})
</script>

<style lang="scss" scoped>
.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  background-color: var(--system-logo-background, var(--theme-menuBar, #2b2f3a));
  border-bottom: 1px solid var(--theme-menuBar-light-1, #2f3349);
  
  .logo-full {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    
    .logo-text {
      font-size: 18px;
      white-space: nowrap;
      color: var(--system-logo-color, var(--theme-menuBarColor, #eaeaea));
      margin: 0;
      font-weight: 600;
    }
  }
  
  .logo-icon {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
