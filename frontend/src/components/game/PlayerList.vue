<script setup>
defineProps({
  players: { type: Array, default: () => [] },
  mePlayerId: { type: Number, default: null },
})
const emoji = ['🕵️', '👮', '👩‍⚕️', '🧑‍🌾', '👔', '🧑‍🔬', '👵', '🧑‍🚒']
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <div
      v-for="(p, i) in players"
      :key="p.id"
      class="flex items-center gap-2 px-3 py-1.5 rounded-full text-sm"
      :class="p.id === mePlayerId ? 'bg-amber-glow/20 border border-amber-glow' : 'bg-noir-800'"
    >
      <span class="text-lg leading-none">{{ emoji[i % emoji.length] }}</span>
      <span>{{ p.id === mePlayerId ? 'You' : `#${p.id}` }}</span>
      <span v-if="p.is_host" title="Host">👑</span>
      <span
        class="w-2 h-2 rounded-full"
        :class="p.connected ? 'bg-emerald-400' : 'bg-noir-600'"
      />
      <span v-if="p.score" class="text-xs text-amber-glow">{{ p.score }}</span>
    </div>
  </div>
</template>
