<template>
  <div class="theme-settings">
    <el-drawer 
      title="主题设置" 
      v-model="isDrawer" 
      direction="rtl" 
      destroy-on-close 
      size="350px"
      @close="onDrawerClose"
    >
      <template #header>
        <span>主题设置</span>
      </template>

      <el-scrollbar class="theme-settings-scrollbar">
        <!-- 全局主题 -->
        <el-divider content-position="left">全局主题</el-divider>
        <div class="setting-item">
          <div class="setting-label">主题色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.primary" 
              size="default"
              @change="onPrimaryColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">深色模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isDark" 
              size="small" 
              @change="onDarkModeChange"
            />
          </div>
        </div>

        <!-- 顶栏设置 -->
        <el-divider content-position="left">顶栏设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">顶栏背景色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.topBar" 
              size="default"
              @change="onTopBarColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">顶栏字体颜色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.topBarColor" 
              size="default"
              @change="onTopBarTextColorChange"
            />
          </div>
        </div>

        <!-- 菜单设置 -->
        <el-divider content-position="left">菜单设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">菜单背景色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBar" 
              size="default"
              @change="onMenuBarColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">菜单字体颜色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBarColor" 
              size="default"
              @change="onMenuBarTextColorChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">菜单高亮色</div>
          <div class="setting-value">
            <el-color-picker 
              v-model="themeConfig.menuBarActiveColor" 
              size="default"
              @change="onMenuBarActiveColorChange"
            />
          </div>
        </div>

        <!-- 界面设置 -->
        <el-divider content-position="left">界面设置</el-divider>
        <div class="setting-item">
          <div class="setting-label">菜单折叠</div>
          <div class="setting-value">
            <el-switch
              v-model="themeConfig.isCollapse"
              size="small"
              @change="onCollapseChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">侧边栏 Logo</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isShowLogo" 
              size="small" 
              @change="onIsShowLogoChange"
            />
          </div>
        </div>
        <div class="setting-item" v-if="themeConfig.isShowLogo">
          <div class="setting-label">Logo 文字</div>
          <div class="setting-value">
            <el-input 
              v-model="themeConfig.logoText" 
              size="small"
              placeholder="请输入Logo文字"
              @input="onLogoTextChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">面包屑导航</div>
          <div class="setting-value">
            <el-switch
              v-model="themeConfig.isBreadcrumb"
              size="small"
              @change="onIsBreadcrumbChange"
            />
          </div>
        </div>

        <!-- 特殊效果 -->
        <el-divider content-position="left">特殊效果</el-divider>
        <div class="setting-item">
          <div class="setting-label">灰色模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isGrayscale" 
              size="small" 
              @change="onGrayscaleChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">色弱模式</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isInvert" 
              size="small" 
              @change="onInvertChange"
            />
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-label">水印功能</div>
          <div class="setting-value">
            <el-switch 
              v-model="themeConfig.isWartermark" 
              size="small" 
              @change="onWatermarkChange"
            />
          </div>
        </div>
        <div class="setting-item" v-if="themeConfig.isWartermark">
          <div class="setting-label">水印文案</div>
          <div class="setting-value">
            <el-input 
              v-model="themeConfig.wartermarkText" 
              size="small"
              placeholder="请输入水印文案"
              @input="onWatermarkTextChange"
            />
          </div>
        </div>

        <!-- 配置操作 -->
        <div class="config-actions">
          <el-alert title="主题配置功能" type="info" :closable="false" />
          <el-button 
            size="default" 
            class="config-btn" 
            type="primary" 
            @click="onCopyConfigClick"
          >
            <el-icon class="mr5">
              <DocumentCopy />
            </el-icon>
            复制配置
          </el-button>
          <el-button 
            size="default" 
            class="config-btn-reset" 
            type="info" 
            @click="onResetConfigClick"
          >
            <el-icon class="mr5">
              <RefreshRight />
            </el-icon>
            恢复默认
          </el-button>
        </div>
      </el-scrollbar>
    </el-drawer>
  </div>
</template>

<script setup>
import { reactive, ref, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DocumentCopy, RefreshRight } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useThemeConfigStore } from '@/stores/themeConfig'
import { useChangeColor } from '@/utils/theme'
import Watermark from '@/utils/watermark'

const appStore = useAppStore()
const themeConfigStore = useThemeConfigStore()
const { getLightColor, getDarkColor } = useChangeColor()

const isDrawer = ref(false)

// 主题配置
const themeConfig = reactive({
  primary: '#409eff',
  isDark: false,
  topBar: '#ffffff',
  topBarColor: '#606266',
  menuBar: '#2b2f3a',
  menuBarColor: '#eaeaea',
  menuBarActiveColor: '#409eff',
  isCollapse: false,
  isShowLogo: true,
  logoText: 'TestCase AI',
  isBreadcrumb: true,
  isGrayscale: false,
  isInvert: false,
  isWartermark: false,
  wartermarkText: 'TestCase AI',
})

// 工具函数
const copyText = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('复制成功')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 应用CSS变量
const applyCSSVariables = () => {
  const root = document.documentElement
  
  // 主题色
  root.style.setProperty('--el-color-primary', themeConfig.primary)
  root.style.setProperty('--theme-primary', themeConfig.primary)
  
  // 生成主题色的渐变色系
  for (let i = 1; i <= 9; i++) {
    root.style.setProperty(`--el-color-primary-light-${i}`, getLightColor(themeConfig.primary, i / 10))
  }
  root.style.setProperty('--el-color-primary-dark-2', getDarkColor(themeConfig.primary, 0.1))
  
  // 深色模式处理
  if (themeConfig.isDark) {
    root.setAttribute('data-theme', 'dark')
    document.body.classList.add('dark-mode')
    
    // 深色模式变量
    root.style.setProperty('--el-bg-color', '#141414')
    root.style.setProperty('--el-bg-color-page', '#0a0a0a')
    root.style.setProperty('--el-text-color-primary', '#e5eaf3')
    root.style.setProperty('--el-text-color-regular', '#cfd3dc')
    root.style.setProperty('--el-border-color', '#4c4d4f')
    root.style.setProperty('--el-fill-color', '#1d1e1f')
    
    // 深色模式下的主题颜色
    root.style.setProperty('--theme-topBar', '#1f1f1f')
    root.style.setProperty('--theme-topBarColor', '#e5eaf3')
    root.style.setProperty('--theme-menuBar', '#191919')
    root.style.setProperty('--theme-menuBarColor', '#bfcbd9')
    root.style.setProperty('--theme-menuBar-light-1', '#2a2a2a')
    root.style.setProperty('--system-container-background', '#0a0a0a')
  } else {
    root.removeAttribute('data-theme')
    document.body.classList.remove('dark-mode')
    
    // 浅色模式变量
    const lightModeVars = [
      '--el-bg-color', '--el-bg-color-page', '--el-text-color-primary',
      '--el-text-color-regular', '--el-border-color', '--el-fill-color'
    ]
    lightModeVars.forEach(varName => root.style.removeProperty(varName))
    
    root.style.setProperty('--theme-topBar', themeConfig.topBar)
    root.style.setProperty('--theme-topBarColor', themeConfig.topBarColor)
    root.style.setProperty('--theme-menuBar', themeConfig.menuBar)
    root.style.setProperty('--theme-menuBarColor', themeConfig.menuBarColor)
    root.style.setProperty('--theme-menuBar-light-1', getLightColor(themeConfig.menuBar, 0.05))
    root.style.setProperty('--system-container-background', '#f5f5f5')
  }
  
  // 菜单高亮色
  root.style.setProperty('--theme-menuBarActiveColor', themeConfig.menuBarActiveColor)
  
  // 系统变量设置
  root.style.setProperty('--system-header-background', themeConfig.isDark ? '#1f1f1f' : themeConfig.topBar)
  root.style.setProperty('--system-header-text-color', themeConfig.isDark ? '#e5eaf3' : themeConfig.topBarColor)
  root.style.setProperty('--system-menu-background', themeConfig.isDark ? '#191919' : themeConfig.menuBar)
  root.style.setProperty('--system-logo-background', themeConfig.isDark ? '#191919' : themeConfig.menuBar)
  root.style.setProperty('--system-logo-color', themeConfig.isDark ? '#bfcbd9' : themeConfig.menuBarColor)
}

// 保存配置到localStorage
const saveConfig = () => {
  localStorage.setItem('simpleThemeConfig', JSON.stringify(themeConfig))
  
  // 同时更新Pinia store
  Object.keys(themeConfig).forEach(key => {
    themeConfigStore.updateThemeConfig(key, themeConfig[key])
  })
}

// 从localStorage加载配置
const loadConfig = () => {
  const saved = localStorage.getItem('simpleThemeConfig')
  if (saved) {
    try {
      const config = JSON.parse(saved)
      Object.keys(config).forEach(key => {
        if (config.hasOwnProperty(key)) {
          themeConfig[key] = config[key]
          themeConfigStore.updateThemeConfig(key, config[key])
        }
      })
    } catch (error) {
      console.warn('Failed to parse theme config:', error)
    }
  }
}

// 各种变化处理函数
const onPrimaryColorChange = () => {
  if (!themeConfig.primary) return ElMessage.warning('主题色不能为空')
  applyCSSVariables()
  saveConfig()
}

const onTopBarColorChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onTopBarTextColorChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onMenuBarColorChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onMenuBarTextColorChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onMenuBarActiveColorChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onCollapseChange = () => {
  appStore.setCollapse(themeConfig.isCollapse)
  saveConfig()
}

const onDarkModeChange = () => {
  applyCSSVariables()
  saveConfig()
}

const onIsShowLogoChange = () => {
  themeConfigStore.updateThemeConfig('isShowLogo', themeConfig.isShowLogo)
  saveConfig()
}

const onLogoTextChange = () => {
  themeConfigStore.updateThemeConfig('logoText', themeConfig.logoText)
  saveConfig()
}

const onIsBreadcrumbChange = () => {
  themeConfigStore.updateThemeConfig('isBreadcrumb', themeConfig.isBreadcrumb)
  saveConfig()
}

const onGrayscaleChange = () => {
  if (themeConfig.isGrayscale) {
    themeConfig.isInvert = false
  }
  const filter = themeConfig.isGrayscale ? 'grayscale(1)' : 'none'
  document.body.style.filter = filter
  saveConfig()
}

const onInvertChange = () => {
  if (themeConfig.isInvert) {
    themeConfig.isGrayscale = false
  }
  const filter = themeConfig.isInvert ? 'invert(80%)' : 'none'
  document.body.style.filter = filter
  saveConfig()
}

const onWatermarkChange = () => {
  if (themeConfig.isWartermark) {
    Watermark.set(themeConfig.wartermarkText)
  } else {
    Watermark.del()
  }
  saveConfig()
}

const onWatermarkTextChange = () => {
  if (themeConfig.isWartermark && themeConfig.wartermarkText) {
    Watermark.set(themeConfig.wartermarkText)
  }
  saveConfig()
}

const onDrawerClose = () => {
  isDrawer.value = false
  saveConfig()
}

// 打开抽屉
const openDrawer = () => {
  isDrawer.value = true
}

// 复制配置
const onCopyConfigClick = () => {
  const configCopy = { ...themeConfig }
  copyText(JSON.stringify(configCopy, null, 2))
}

// 恢复默认
const onResetConfigClick = () => {
  Object.assign(themeConfig, {
    primary: '#409eff',
    isDark: false,
    topBar: '#ffffff',
    topBarColor: '#606266',
    menuBar: '#2b2f3a',
    menuBarColor: '#eaeaea',
    menuBarActiveColor: '#409eff',
    isCollapse: false,
    isShowLogo: true,
    logoText: 'TestCase AI',
    isBreadcrumb: true,
    isGrayscale: false,
    isInvert: false,
    isWartermark: false,
    wartermarkText: 'TestCase AI',
  })
  
  document.body.style.filter = 'none'
  Watermark.del()
  
  applyCSSVariables()
  saveConfig()
  
  ElMessage.success('已恢复默认配置')
}

// 初始化
onMounted(() => {
  nextTick(() => {
    loadConfig()
    applyCSSVariables()
    
    if (themeConfig.isGrayscale) {
      document.body.style.filter = 'grayscale(1)'
    } else if (themeConfig.isInvert) {
      document.body.style.filter = 'invert(80%)'
    }
    
    if (themeConfig.isWartermark) {
      Watermark.set(themeConfig.wartermarkText)
    }
  })
})

// 暴露方法
defineExpose({
  openDrawer,
})
</script>

<style scoped lang="scss">
.theme-settings-scrollbar {
  height: calc(100vh - 50px);
  padding: 0 15px;

  :deep(.el-scrollbar__view) {
    overflow-x: hidden !important;
  }

  .setting-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    min-height: 32px;

    .setting-label {
      flex: 1;
      color: var(--el-text-color-primary);
      font-size: 14px;
      margin-right: 10px;
    }

    .setting-value {
      display: flex;
      align-items: center;
      flex-shrink: 0;
    }
  }

  .config-actions {
    margin: 20px 0;

    .config-btn {
      width: 100%;
      margin-top: 15px;
    }

    .config-btn-reset {
      width: 100%;
      margin: 10px 0 0;
    }
  }
}

.mr5 {
  margin-right: 5px;
}
</style>
