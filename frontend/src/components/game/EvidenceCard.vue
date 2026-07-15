<script setup>
const props = defineProps({
  evidence: { type: Object, required: true },
  revealable: { type: Boolean, default: false },
  revealed: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})
defineEmits(['reveal', 'select'])

const icon = { document: '📄', witness: '🗣️', physical: '🔩', medical: '💉', rumor: '💬' }
</script>

<template>
  <div
    class="rounded-lg p-3 border text-left transition-all bg-evidence text-noir-950 border-noir-700/40"
    :class="[
      compact ? 'w-40' : 'w-full',
      revealed ? 'opacity-95' : 'opacity-100',
      'shadow-pin hover:-translate-y-0.5',
    ]"
    @click="$emit('select', evidence)"
  >
    <div class="flex items-center justify-between mb-1">
      <span class="text-lg">{{ icon[evidence.type] || '📎' }}</span>
      <span class="text-[10px] uppercase tracking-wide text-noir-700/70">{{ evidence.type }}</span>
    </div>
    <h4 class="font-display text-sm leading-tight">{{ evidence.title }}</h4>
    <p v-if="!compact" class="text-xs mt-1 text-noir-800/80">{{ evidence.text }}</p>

    <button
      v-if="revealable && !revealed"
      class="mt-2 w-full text-xs font-semibold py-1 rounded bg-noir-900 text-amber-glow hover:brightness-125"
      @click.stop="$emit('reveal', evidence)"
    >
      {{ $t('game.reveal') }}
    </button>
    <span v-else-if="revealed" class="mt-2 block text-[10px] text-emerald-700">✓ {{ $t('game.revealed') }}</span>
  </div>
</template>
