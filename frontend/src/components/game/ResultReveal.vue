<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
  locations: { type: Array, default: () => [] },
})
defineEmits(['again'])

const investigatorsWin = computed(() => props.result.outcome === 'investigators_win')
const correctLocation = computed(() =>
  props.locations.find((l) => l.id === props.result.correct_location_id),
)
const ranked = computed(() => [...(props.result.scores || [])].sort((a, b) => b.total - a.total))
</script>

<template>
  <div class="max-w-lg mx-auto space-y-6 py-6">
    <!-- Outcome banner -->
    <div
      class="card p-6 text-center border-2"
      :class="investigatorsWin ? 'border-emerald-500' : 'border-red-500'"
    >
      <div class="text-6xl mb-2">{{ investigatorsWin ? '🎉' : '🕳️' }}</div>
      <h1 class="font-display text-3xl" :class="investigatorsWin ? 'text-emerald-400' : 'text-red-400'">
        {{ investigatorsWin ? $t('result.investigatorsWin') : $t('result.insiderWin') }}
      </h1>
    </div>

    <!-- Truth reconstruction -->
    <div class="card p-5">
      <h2 class="font-display text-lg text-amber-glow mb-2">{{ $t('result.truth') }}</h2>
      <p class="text-sm text-evidence/80 leading-relaxed">{{ result.truth_story }}</p>
      <p v-if="correctLocation" class="mt-3 text-sm">
        📍 <span class="text-amber-glow">{{ correctLocation.name }}</span>
      </p>
    </div>

    <!-- Insider unmasking -->
    <div class="card p-5 text-center">
      <p class="text-sm text-evidence/60">{{ $t('result.insiderWas') }}</p>
      <p class="font-display text-2xl text-red-400 mt-1">Player #{{ result.insider_player_id }}</p>
      <span
        class="inline-block mt-2 px-3 py-1 rounded-full text-xs"
        :class="result.insider_caught ? 'bg-emerald-600 text-white' : 'bg-noir-700 text-evidence/70'"
      >
        {{ result.insider_caught ? $t('result.caught') : $t('result.escaped') }}
      </span>
    </div>

    <!-- Scoreboard -->
    <div class="card p-5">
      <h2 class="font-display text-lg mb-3">{{ $t('result.scoreboard') }}</h2>
      <ul class="space-y-2">
        <li
          v-for="(s, i) in ranked"
          :key="s.player_id"
          class="flex items-center justify-between px-3 py-2 rounded-lg bg-noir-900"
        >
          <span>{{ ['🥇', '🥈', '🥉'][i] || '·' }} Player #{{ s.player_id }}</span>
          <span class="font-display text-amber-glow">{{ s.total }}</span>
        </li>
      </ul>
    </div>

    <button class="btn-amber w-full" @click="$emit('again')">{{ $t('result.playAgain') }}</button>
  </div>
</template>
