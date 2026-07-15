<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const admin = useAdminStore()
const ui = useUiStore()
const draft = ref({ name: '', icon: '', color: '#f59e0b', description: '' })

onMounted(() => admin.loadGenres())

async function create() {
  if (!draft.value.name) return
  await admin.createGenre(draft.value)
  draft.value = { name: '', icon: '', color: '#f59e0b', description: '' }
  ui.toast('Genre added', 'success')
}

async function remove(id) {
  await admin.deleteGenre(id)
  ui.toast('Genre deleted')
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-6 space-y-5">
    <div class="flex items-center justify-between">
      <h1 class="font-display text-2xl text-amber-glow">Genres</h1>
      <RouterLink to="/admin" class="btn-ghost text-sm">{{ $t('common.back') }}</RouterLink>
    </div>

    <div class="card p-4 flex flex-wrap gap-2 items-end">
      <div class="flex-1 min-w-[10rem]">
        <label class="label">Name</label>
        <input v-model="draft.name" class="input" />
      </div>
      <div class="w-24">
        <label class="label">Icon</label>
        <input v-model="draft.icon" class="input" placeholder="leaf" />
      </div>
      <div class="w-20">
        <label class="label">Color</label>
        <input v-model="draft.color" type="color" class="input h-10 p-1" />
      </div>
      <button class="btn-amber" @click="create">Add</button>
    </div>

    <div class="grid gap-2 sm:grid-cols-2">
      <div v-for="g in admin.genres" :key="g.id" class="card p-3 flex items-center justify-between">
        <span class="flex items-center gap-2">
          <span class="w-4 h-4 rounded-full" :style="{ background: g.color }" />
          <span class="font-display">{{ g.name }}</span>
        </span>
        <button class="text-xs text-red-400 hover:text-red-300" @click="remove(g.id)">Delete</button>
      </div>
    </div>
  </div>
</template>
