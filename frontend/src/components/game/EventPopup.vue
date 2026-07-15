<script setup>
import { ref, watch, computed } from 'vue'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const typed = ref('')
let typer = null

// Golden glow for good news (unlocks / time gained), red siren otherwise.
const good = computed(() => {
  const e = ui.currentEvent
  if (!e) return true
  return ['unlock_evidence', 'add_time', 'reveal_hint'].includes(e.effect_type)
})

watch(
  () => ui.currentEvent,
  (evt) => {
    clearInterval(typer)
    typed.value = ''
    if (!evt) return
    const text = evt.narration || ''
    let i = 0
    typer = setInterval(() => {
      typed.value = text.slice(0, ++i)
      if (i >= text.length) clearInterval(typer)
    }, 24)
  },
)
</script>

<template>
  <Transition name="event">
    <div
      v-if="ui.currentEvent"
      class="fixed inset-0 z-[70] flex items-center justify-center p-6 backdrop-blur-sm"
      :class="good ? 'bg-amber-glow/10' : 'bg-red-900/30 animate-pulse-ring'"
      @click="ui.dismissEvent()"
    >
      <div
        class="card max-w-lg w-full p-8 text-center border-2"
        :class="good ? 'border-amber-glow shadow-glow' : 'border-red-500'"
      >
        <div class="text-5xl mb-4">{{ good ? '🗝️' : '🚨' }}</div>
        <p class="font-display text-lg leading-relaxed min-h-[3rem]">{{ typed }}</p>
        <p v-if="ui.currentEvent.new_deadline" class="mt-3 text-sm text-amber-glow">⏱ Time changed</p>
        <button class="btn-ghost mt-6" @click.stop="ui.dismissEvent()">Continue</button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.event-enter-active {
  transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.event-leave-active {
  transition: all 0.25s ease;
}
.event-enter-from,
.event-leave-to {
  opacity: 0;
  transform: scale(0.85);
}
</style>
