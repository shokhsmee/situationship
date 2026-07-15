<script setup>
import { onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useUiStore } from '@/stores/ui'
import { useGameSocket } from '@/composables/useGameSocket'

const route = useRoute()
const router = useRouter()
const game = useGameStore()
const ui = useUiStore()
const socket = useGameSocket()

const gameId = Number(route.params.id)

onMounted(async () => {
  await game.fetchState(gameId)
  socket.connect(gameId)
})

// Once the host starts, everyone is pushed into the game.
watch(
  () => game.phase,
  (p) => {
    if (p && p !== 'lobby') router.push({ name: 'game', params: { id: gameId } })
  },
)

const canStart = computed(() => game.isHost && game.players.length >= 3)

async function start() {
  try {
    await game.start()
  } catch (e) {
    ui.toast(e.response?.data?.detail || 'Cannot start yet', 'error')
  }
}

function shareCode() {
  navigator.clipboard?.writeText(game.state?.code || '')
  ui.toast('Code copied', 'success')
}
</script>

<template>
  <div v-if="game.state" class="max-w-lg mx-auto px-4 py-10 text-center">
    <p class="text-evidence/50 text-sm uppercase tracking-widest">{{ $t('lobby.title') }}</p>
    <h1 class="font-display text-2xl mt-1 mb-6">{{ game.scenario.title }}</h1>

    <button class="card px-8 py-4 mx-auto mb-6 hover:border-amber-glow" @click="shareCode">
      <span class="block text-xs text-evidence/50">{{ $t('home.code') }}</span>
      <span class="font-display text-4xl tracking-[0.3em] text-amber-glow">{{ game.state.code }}</span>
      <span class="block text-xs text-evidence/40 mt-1">{{ $t('lobby.share') }}</span>
    </button>

    <div class="card p-5 mb-6">
      <h2 class="text-sm text-evidence/60 mb-3">
        {{ $t('lobby.players') }} · {{ game.players.length }}
      </h2>
      <ul class="space-y-2">
        <li
          v-for="p in game.players"
          :key="p.id"
          class="flex items-center justify-between px-3 py-2 rounded-lg bg-noir-900"
        >
          <span class="flex items-center gap-2">
            <span
              class="w-2 h-2 rounded-full"
              :class="p.connected ? 'bg-emerald-400' : 'bg-noir-600'"
            />
            Player #{{ p.id }}
          </span>
          <span v-if="p.is_host" class="text-xs text-amber-glow">{{ $t('lobby.host') }}</span>
        </li>
      </ul>
    </div>

    <button v-if="game.isHost" class="btn-amber w-full" :disabled="!canStart" @click="start">
      {{ $t('lobby.start') }}
    </button>
    <p v-else class="text-evidence/50 text-sm animate-pulse">{{ $t('lobby.waiting') }}</p>
    <p v-if="game.isHost && !canStart" class="text-xs text-evidence/40 mt-2">
      {{ $t('lobby.needMore', { n: 3 }) }}
    </p>
  </div>
  <div v-else class="text-center py-20 text-evidence/40">{{ $t('common.loading') }}</div>
</template>
