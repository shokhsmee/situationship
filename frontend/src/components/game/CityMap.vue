<script setup>
import { ref } from 'vue'

defineProps({
  locations: { type: Array, default: () => [] },
  selectable: { type: Boolean, default: false },
  selectedId: { type: Number, default: null },
  tally: { type: Object, default: () => ({}) },
})
defineEmits(['select'])

const hovered = ref(null)
</script>

<template>
  <div class="relative w-full aspect-[16/10] rounded-xl overflow-hidden border border-noir-600 bg-noir-900">
    <!-- Stylised noir city backdrop -->
    <svg viewBox="0 0 160 100" class="absolute inset-0 w-full h-full">
      <defs>
        <linearGradient id="water" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#12324a" />
          <stop offset="100%" stop-color="#0a1e2e" />
        </linearGradient>
      </defs>
      <rect width="160" height="100" fill="#0f1526" />
      <!-- river -->
      <path d="M0,70 C40,60 60,85 90,75 C120,66 140,88 160,80 L160,100 L0,100 Z" fill="url(#water)" />
      <!-- district blocks -->
      <g fill="#161d33" stroke="#2b3757" stroke-width="0.4">
        <rect x="10" y="12" width="26" height="20" rx="1" />
        <rect x="42" y="16" width="22" height="26" rx="1" />
        <rect x="70" y="10" width="30" height="22" rx="1" />
        <rect x="108" y="14" width="34" height="24" rx="1" />
        <rect x="20" y="40" width="24" height="18" rx="1" />
        <rect x="52" y="46" width="26" height="16" rx="1" />
      </g>
    </svg>

    <!-- Pins -->
    <button
      v-for="loc in locations"
      :key="loc.id"
      class="absolute -translate-x-1/2 -translate-y-full group"
      :style="{ left: loc.map_x + '%', top: loc.map_y + '%' }"
      :disabled="!selectable"
      @click="$emit('select', loc)"
      @mouseenter="hovered = loc.id"
      @mouseleave="hovered = null"
    >
      <span
        class="block text-2xl leading-none transition-transform drop-shadow-lg"
        :class="[
          selectedId === loc.id ? 'scale-150 animate-bounce' : 'group-hover:scale-125',
          selectable ? 'cursor-pointer' : 'cursor-default',
        ]"
      >📍</span>
      <span
        v-if="tally[loc.id]"
        class="absolute -top-1 -right-2 bg-amber-glow text-noir-950 text-[10px] font-bold rounded-full w-4 h-4 flex items-center justify-center"
      >{{ tally[loc.id] }}</span>

      <!-- Tooltip -->
      <div
        v-if="hovered === loc.id"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 w-40 card p-2 text-left z-20"
      >
        <p class="font-display text-xs text-amber-glow">{{ loc.name }}</p>
        <p class="text-[10px] text-evidence/60 mt-0.5">{{ loc.description }}</p>
      </div>
    </button>
  </div>
</template>
