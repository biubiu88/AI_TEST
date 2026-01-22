import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    isCollapse: false, // 侧边栏是否收缩展示
    contentFullScreen: false, // 内容是否可全屏展示
    showLogo: true, // 是否显示Logo
    fixedTop: false, // 是否固定顶部
    showTabs: true, // 是否显示导航历史
    expandOneMenu: true, // 一次是否只能展开一个菜单
    elementSize: 'small', // element默认尺寸
    lang: '', // 默认采用的国际化方案
    theme: {
      style: 'default',
      primaryColor: '#409eff',
      menuType: 'side'
    },
    menuList: []
  }),

  actions: {
    setCollapse(value) {
      this.isCollapse = value
    },
    toggleCollapse() {
      this.isCollapse = !this.isCollapse
    },
    setContentFullScreen(value) {
      this.contentFullScreen = value
    },
    setMenuList(arr) {
      this.menuList = arr
    }
  },

  persist: {
    enabled: true,
    strategies: [
      {
        key: 'app',
        storage: localStorage,
      }
    ]
  }
})
