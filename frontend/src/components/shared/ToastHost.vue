<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
const color = { info: 'border-noir-600', success: 'border-emerald-500', error: 'border-red-500' }
</script>

<template>
  <div class="fixed bottom-4 left-1/2 -translate-x-1/2 z-[60] flex flex-col gap-2 w-[90%] max-w-sm">
    <TransitionGroup name="toast">
      <div
        v-for="t in ui.toasts"
        :key="t.id"
        class="card border-l-4 px-4 py-2 text-sm"
        :class="color[t.kind] || color.info"
      >
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
