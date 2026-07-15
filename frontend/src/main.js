import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { MotionPlugin } from '@vueuse/motion'
import App from './App.vue'
import { router } from './router'
import { i18n } from './i18n'
import { useAuthStore } from './stores/auth'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(MotionPlugin)

// Establish auth BEFORE first render so route guards (and deep-linked Mini App
// URLs like /lobby/:id) see the correct state instead of bouncing to home.
const auth = useAuthStore()

async function bootstrap() {
  const initData = window.Telegram?.WebApp?.initData
  if (initData && !auth.token) {
    // Opened inside Telegram: sign in via initData before mounting.
    try {
      await auth.telegram(initData)
    } catch {
      /* fall through to unauthenticated */
    }
  } else {
    await auth.fetchMe()
  }
  app.mount('#app')
}

bootstrap()
