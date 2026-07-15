import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import http, { TOKEN_KEY } from '@/api/http'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)
  const isWriter = computed(() => ['admin', 'writer'].includes(user.value?.role))
  const isAdmin = computed(() => user.value?.role === 'admin')

  function _apply({ access_token, user: u }) {
    token.value = access_token
    user.value = u
    localStorage.setItem(TOKEN_KEY, access_token)
  }

  async function login(username, password) {
    _apply((await http.post('/auth/login', { username, password })).data)
  }

  async function register(payload) {
    _apply((await http.post('/auth/register', payload)).data)
  }

  async function telegram(initData) {
    _apply((await http.post('/auth/telegram', { init_data: initData })).data)
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      user.value = (await http.get('/auth/me')).data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  return { token, user, isAuthenticated, isWriter, isAdmin, login, register, telegram, fetchMe, logout }
})
