<script setup>
import { onMounted, ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const admin = useAdminStore()
const ui = useUiStore()
const creating = ref(false)
const draft = ref({ title: '', genre_id: null })

onMounted(async () => {
  await Promise.all([admin.loadScenarios(), admin.loadGenres(), admin.loadDashboard()])
  if (admin.genres.length) draft.value.genre_id = admin.genres[0].id
})

async function createScenario() {
  if (!draft.value.title || !draft.value.genre_id) return
  const s = await admin.createScenario(draft.value)
  ui.toast('Scenario created', 'success')
  router.push({ name: 'admin-scenario', params: { id: s.id } })
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="font-display text-2xl text-amber-glow">Scenario Studio</h1>
      <RouterLink to="/admin/genres" class="btn-ghost text-sm">Manage genres</RouterLink>
    </div>

    <!-- Stats -->
    <div v-if="admin.dashboard" class="grid sm:grid-cols-3 gap-3">
      <div class="card p-4">
        <p class="text-3xl font-display text-amber-glow">{{ admin.dashboard.games_total }}</p>
        <p class="text-xs text-evidence/60">games created</p>
      </div>
      <div class="card p-4">
        <p class="text-3xl font-display text-amber-glow">{{ admin.dashboard.games_finished }}</p>
        <p class="text-xs text-evidence/60">games finished</p>
      </div>
      <div class="card p-4">
        <p class="text-3xl font-display text-amber-glow">{{ admin.scenarios.length }}</p>
        <p class="text-xs text-evidence/60">scenarios</p>
      </div>
    </div>

    <div v-if="admin.dashboard?.scenarios?.length" class="card p-4">
      <h2 class="text-sm text-evidence/60 mb-2">Win rates</h2>
      <div v-for="s in admin.dashboard.scenarios" :key="s.scenario_id" class="flex justify-between text-sm py-1">
        <span>{{ s.title }}</span>
        <span class="text-evidence/60">
          {{ s.games_played }} played · {{ Math.round(s.investigator_win_rate * 100) }}% investigators
        </span>
      </div>
    </div>

    <!-- Create -->
    <div class="card p-4">
      <button v-if="!creating" class="btn-amber" @click="creating = true">+ New scenario</button>
      <div v-else class="flex flex-wrap gap-2 items-end">
        <div class="flex-1 min-w-[12rem]">
          <label class="label">Title</label>
          <input v-model="draft.title" class="input" />
        </div>
        <div>
          <label class="label">Genre</label>
          <select v-model="draft.genre_id" class="input">
            <option v-for="g in admin.genres" :key="g.id" :value="g.id">{{ g.name }}</option>
          </select>
        </div>
        <button class="btn-amber" @click="createScenario">Create</button>
      </div>
    </div>

    <!-- List -->
    <div class="grid gap-3 sm:grid-cols-2">
      <RouterLink
        v-for="s in admin.scenarios"
        :key="s.id"
        :to="{ name: 'admin-scenario', params: { id: s.id } }"
        class="card p-4 hover:border-amber-glow transition-colors"
      >
        <div class="flex justify-between">
          <h3 class="font-display">{{ s.title }}</h3>
          <span
            class="text-xs px-2 py-0.5 rounded-full"
            :class="s.is_published ? 'bg-emerald-600 text-white' : 'bg-noir-700 text-evidence/60'"
          >{{ s.is_published ? 'published' : 'draft' }}</span>
        </div>
        <p class="text-xs text-evidence/50 mt-1">Difficulty ★{{ s.difficulty }} · {{ s.min_players }}–{{ s.max_players }}p</p>
      </RouterLink>
    </div>
  </div>
</template>
