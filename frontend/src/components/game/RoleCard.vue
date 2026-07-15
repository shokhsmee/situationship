<script setup>
import { ref, onMounted } from 'vue'

defineProps({
  role: { type: Object, default: null },
  isInsider: { type: Boolean, default: false },
  insiderGoal: { type: String, default: null },
})

const flipped = ref(false)
onMounted(() => setTimeout(() => (flipped.value = true), 400))
</script>

<template>
  <div class="[perspective:1000px] w-full max-w-xs mx-auto">
    <div
      class="relative w-full aspect-[3/4] transition-transform duration-700 [transform-style:preserve-3d]"
      :class="flipped ? '[transform:rotateY(180deg)]' : ''"
      @click="flipped = !flipped"
    >
      <!-- Back (face down) -->
      <div class="absolute inset-0 card flex items-center justify-center [backface-visibility:hidden]">
        <span class="font-display text-6xl text-amber-glow/40">?</span>
      </div>

      <!-- Front (role) -->
      <div
        class="absolute inset-0 card p-5 flex flex-col [backface-visibility:hidden] [transform:rotateY(180deg)]"
        :class="isInsider ? 'border-red-500 shadow-[0_0_24px_rgba(239,68,68,0.4)]' : 'border-amber-glow shadow-glow'"
      >
        <div class="text-5xl mb-3">{{ isInsider ? '🕵️' : '🔎' }}</div>
        <h3 class="font-display text-2xl" :class="isInsider ? 'text-red-400' : 'text-amber-glow'">
          {{ role?.name || 'Investigator' }}
        </h3>
        <p class="text-sm text-evidence/70 mt-2 flex-1">{{ role?.description }}</p>
        <div v-if="isInsider && insiderGoal" class="mt-3 p-3 rounded-lg bg-red-950/60 border border-red-800">
          <p class="text-xs uppercase tracking-wide text-red-400 mb-1">{{ $t('game.insiderGoal') }}</p>
          <p class="text-xs text-red-200">{{ insiderGoal }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
