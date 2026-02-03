import { createApp } from 'vue'
import App from './App.vue'

// Element Plus
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// Router & Pinia
import router from './router'
import { createPinia } from 'pinia'

// i18n
import i18n from './i18n'

// Permission Directives
import { setupPermissionDirectives } from './utils/permission'

// Styles
import './assets/main.css'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册权限指令
setupPermissionDirectives(app)

app.use(pinia)
app.use(ElementPlus, { locale: zhCn })
app.use(i18n)
app.use(router)

app.mount('#app')
