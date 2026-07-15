<script setup>
import { useUiStore } from '@/stores/ui'
const ui = useUiStore()
const locales = ['en', 'ru', 'uz']
</script>

<template>
  <div class="flex gap-1 text-xs">
    <button
      v-for="l in locales"
      :key="l"
      class="px-2 py-1 rounded uppercase transition-colors"
      :class="ui.locale === l ? 'bg-amber-glow text-noir-950' : 'text-evidence/50 hover:text-evidence'"
      @click="ui.setLocale(l)"
    >
      {{ l }}
    </button>
  </div>
</template>
