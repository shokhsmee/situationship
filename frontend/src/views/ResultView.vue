<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import ResultReveal from '@/components/game/ResultReveal.vue'

const route = useRoute()
const router = useRouter()
const game = useGameStore()
const ready = ref(false)
const gameId = Number(route.params.id)

onMounted(async () => {
  // Need locations for the map highlight; result may already be in the store
  // (arrived via WebSocket) or must be pulled (direct navigation / reconnect).
  if (!game.locations.length) await game.fetchState(gameId).catch(() => {})
  if (!game.result) await game.fetchResult(gameId).catch(() => {})
  ready.value = true
})

function again() {
  game.reset()
  router.push({ name: 'home' })
}
</script>

<template>
  <div v-if="ready && game.result" class="px-4">
    <ResultReveal :result="game.result" :locations="game.locations" @again="again" />
  </div>
  <div v-else class="text-center py-20 text-evidence/40">{{ $t('common.loading') }}</div>
</template>
