import { defineStore } from 'pinia'

export const useThemeConfigStore = defineStore('themeConfig', {
  state: () => ({
    // 是否开启设置抽屉
    isDrawer: false,

    // 全局主题
    primary: '#409eff',
    isDark: false,

    // 顶栏设置
    topBar: '#ffffff',
    topBarColor: '#606266',
    isTopBarColorGradual: false,

    // 菜单设置
    menuBar: '#2b2f3a',
    menuBarColor: '#eaeaea',
    menuBarActiveColor: '#409eff',
    isMenuBarColorGradual: false,

    // 界面设置
    isCollapse: false,
    isUniqueOpened: true,
    isFixedHeader: true,
    isFixedHeaderChange: false,
    isLockScreen: false,
    lockScreenTime: 30,

    // 界面显示
    isShowLogo: true,
    logoText: 'TestCase AI',
    isShowLogoChange: false,
    isBreadcrumb: true,
    isBreadcrumbIcon: false,
    isTagsview: false,
    isTagsviewIcon: false,
    isCacheTagsView: false,
    isSortableTagsView: false,
    isFooter: false,
    isGrayscale: false,
    isInvert: false,
    isWartermark: false,
    wartermarkText: 'TestCase AI',

    // 其它设置
    animation: 'default',
    layout: 'default',

    // 全局网站标题
    globalTitle: 'TestCase AI',
    globalViceTitle: '测试用例生成器',
    globalViceTitleMsg: 'AI驱动的测试用例生成平台',
    globalComponentSize: 'small',
  }),

  actions: {
    setThemeConfig(data) {
      Object.assign(this, data)
    },
    updateThemeConfig(key, value) {
      this[key] = value
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'themeConfig',
        storage: localStorage,
      }
    ]
  }
})
