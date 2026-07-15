<script setup>
import { ref } from 'vue'

const props = defineProps({
  players: { type: Array, default: () => [] },
  mePlayerId: { type: Number, default: null },
})
const emit = defineEmits(['guess', 'skip'])

const chosen = ref(null)
function pick(p) {
  if (p.id === props.mePlayerId) return
  chosen.value = p.id
  emit('guess', p.id)
}
const emoji = ['🕵️', '👮', '👩‍⚕️', '🧑‍🌾', '👔', '🧑‍🔬', '👵', '🧑‍🚒']
</script>

<template>
  <div class="space-y-4 text-center">
    <h2 class="font-display text-xl text-red-400">{{ $t('game.guessInsider') }}</h2>
    <div class="flex flex-wrap justify-center gap-3">
      <button
        v-for="(p, i) in players"
        :key="p.id"
        class="flex flex-col items-center gap-1 p-3 rounded-xl border transition-all w-24"
        :class="[
          chosen === p.id ? 'border-red-500 bg-red-950/40 scale-105' : 'border-noir-600 hover:border-red-500/60',
          p.id === mePlayerId ? 'opacity-40 cursor-not-allowed' : '',
        ]"
        :disabled="p.id === mePlayerId"
        @click="pick(p)"
      >
        <span class="text-3xl">{{ emoji[i % emoji.length] }}</span>
        <span class="text-xs">{{ p.id === mePlayerId ? 'You' : `#${p.id}` }}</span>
      </button>
    </div>
    <button class="btn-ghost" @click="$emit('skip')">{{ $t('game.skip') }}</button>
  </div>
</template>
