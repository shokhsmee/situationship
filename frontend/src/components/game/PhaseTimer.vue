<script setup>
import { toRef, computed } from 'vue'
import { useTimer } from '@/composables/useTimer'

const props = defineProps({
  deadline: { type: Number, default: null },
  total: { type: Number, default: 90 },
})

const { label, progress, urgent } = useTimer(toRef(props, 'deadline'), toRef(props, 'total'))

const R = 42
const C = 2 * Math.PI * R
const dash = computed(() => C * (1 - progress.value))
</script>

<template>
  <div class="relative w-24 h-24" :class="{ 'animate-pulse-ring': urgent }">
    <svg viewBox="0 0 100 100" class="w-full h-full -rotate-90">
      <circle cx="50" cy="50" :r="R" fill="none" stroke="currentColor" class="text-noir-700" stroke-width="6" />
      <circle
        cx="50"
        cy="50"
        :r="R"
        fill="none"
        :stroke="urgent ? '#ef4444' : '#f5a623'"
        stroke-width="6"
        stroke-linecap="round"
        :stroke-dasharray="C"
        :stroke-dashoffset="dash"
        style="transition: stroke-dashoffset 0.25s linear"
      />
    </svg>
    <div
      class="absolute inset-0 flex items-center justify-center font-display text-lg"
      :class="urgent ? 'text-red-400' : 'text-amber-glow'"
    >
      {{ label }}
    </div>
  </div>
</template>
