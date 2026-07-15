<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useGameStore } from '@/stores/game'
import { useUiStore } from '@/stores/ui'
import { useTelegram } from '@/composables/useTelegram'
import http from '@/api/http'

const router = useRouter()
const auth = useAuthStore()
const game = useGameStore()
const ui = useUiStore()
const { isTelegram, initData } = useTelegram()

const mode = ref('login') // 'login' | 'register'
const form = ref({ username: '', password: '', display_name: '' })
const scenarios = ref([])
const joinCode = ref('')
const busy = ref(false)

onMounted(async () => {
  // Auto-auth inside Telegram.
  if (isTelegram.value && initData && !auth.isAuthenticated) {
    try {
      await auth.telegram(initData)
    } catch {
      ui.toast('Telegram sign-in failed', 'error')
    }
  }
  if (auth.isAuthenticated) await loadScenarios()
})

async function loadScenarios() {
  scenarios.value = (await http.get('/games/scenarios')).data
}

async function submitAuth() {
  busy.value = true
  try {
    if (mode.value === 'login') await auth.login(form.value.username, form.value.password)
    else await auth.register(form.value)
    await loadScenarios()
  } catch (e) {
    ui.toast(e.response?.data?.detail || 'Authentication failed', 'error')
  } finally {
    busy.value = false
  }
}

async function playGuest() {
  const n = Math.floor(Math.random() * 1e6)
  form.value = { username: `guest_${n}`, password: `g${n}`, display_name: `Guest ${n}` }
  mode.value = 'register'
  await submitAuth()
}

async function createGame(scenarioId) {
  busy.value = true
  try {
    const { id } = await game.create(scenarioId)
    router.push({ name: 'lobby', params: { id } })
  } catch (e) {
    ui.toast(e.response?.data?.detail || 'Could not create game', 'error')
  } finally {
    busy.value = false
  }
}

async function joinGame() {
  if (!joinCode.value) return
  busy.value = true
  try {
    const state = await game.join(joinCode.value.trim().toUpperCase())
    router.push({ name: 'lobby', params: { id: state.id } })
  } catch (e) {
    ui.toast(e.response?.data?.detail || 'Could not join', 'error')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-10">
    <div class="text-center mb-10">
      <h1 class="font-display text-4xl text-amber-glow mb-2">{{ $t('app.title') }}</h1>
      <p class="text-evidence/60 italic">{{ $t('app.tagline') }}</p>
    </div>

    <!-- Auth -->
    <div v-if="!auth.isAuthenticated" class="card p-6 max-w-sm mx-auto">
      <div class="flex gap-2 mb-4">
        <button class="btn flex-1" :class="mode === 'login' ? 'btn-amber' : 'btn-ghost'" @click="mode = 'login'">
          {{ $t('auth.login') }}
        </button>
        <button class="btn flex-1" :class="mode === 'register' ? 'btn-amber' : 'btn-ghost'" @click="mode = 'register'">
          {{ $t('auth.register') }}
        </button>
      </div>
      <form class="space-y-3" @submit.prevent="submitAuth">
        <div v-if="mode === 'register'">
          <label class="label">{{ $t('auth.displayName') }}</label>
          <input v-model="form.display_name" class="input" required />
        </div>
        <div>
          <label class="label">{{ $t('auth.username') }}</label>
          <input v-model="form.username" class="input" required />
        </div>
        <div>
          <label class="label">{{ $t('auth.password') }}</label>
          <input v-model="form.password" type="password" class="input" required />
        </div>
        <button class="btn-amber w-full" :disabled="busy">{{ $t(`auth.${mode}`) }}</button>
      </form>
      <button class="btn-ghost w-full mt-3" :disabled="busy" @click="playGuest">
        {{ $t('auth.guest') }}
      </button>
    </div>

    <!-- Authenticated home -->
    <div v-else class="space-y-8">
      <div class="card p-5">
        <h2 class="font-display text-xl mb-3">{{ $t('home.join') }}</h2>
        <div class="flex gap-2">
          <input v-model="joinCode" :placeholder="$t('home.code')" class="input uppercase tracking-widest" />
          <button class="btn-amber" :disabled="busy" @click="joinGame">{{ $t('home.join') }}</button>
        </div>
      </div>

      <div>
        <h2 class="font-display text-xl mb-3">{{ $t('home.browse') }}</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <button
            v-for="s in scenarios"
            :key="s.id"
            class="card p-4 text-left hover:border-amber-glow transition-colors group"
            :disabled="busy"
            @click="createGame(s.id)"
          >
            <div class="flex justify-between items-start">
              <h3 class="font-display text-lg group-hover:text-amber-glow">{{ s.title }}</h3>
              <span class="text-xs text-evidence/50">★ {{ s.difficulty }}</span>
            </div>
            <p class="text-xs text-evidence/50 mt-2">{{ s.min_players }}–{{ s.max_players }} players</p>
          </button>
        </div>
        <p v-if="!scenarios.length" class="text-evidence/40 text-sm">No published cases yet.</p>
      </div>
    </div>
  </div>
</template>
