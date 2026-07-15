<script setup>
import { onMounted, ref, computed, reactive } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'
import LocationEditor from './LocationEditor.vue'
import RoleEditor from './RoleEditor.vue'
import EvidenceEditor from './EvidenceEditor.vue'
import EventEditor from './EventEditor.vue'

const route = useRoute()
const admin = useAdminStore()
const ui = useUiStore()
const id = Number(route.params.id)

const TABS = ['General', 'Locations', 'Roles', 'Evidence', 'Events', 'Final Answer', 'Timers', 'Validate']
const PHASES = ['intro', 'evidence', 'discussion', 'vote', 'insider_guess']
const tab = ref('General')
const s = computed(() => admin.current)

const general = reactive({})
const timers = reactive({})

onMounted(async () => {
  await Promise.all([admin.loadScenario(id), admin.loadGenres()])
  Object.assign(general, {
    title: s.value.title, genre_id: s.value.genre_id, intro_text: s.value.intro_text,
    task_text: s.value.task_text, difficulty: s.value.difficulty,
    min_players: s.value.min_players, max_players: s.value.max_players, rounds: s.value.rounds,
    correct_location_id: s.value.correct_location_id, correct_answer_text: s.value.correct_answer_text,
    truth_story: s.value.truth_story,
  })
  PHASES.forEach((p) => (timers[p] = s.value.timers?.[p] ?? ''))
})

async function saveGeneral() {
  await admin.updateScenario(id, general)
  ui.toast('Saved', 'success')
}
async function saveTimers() {
  const clean = {}
  PHASES.forEach((p) => { if (timers[p] !== '' && timers[p] != null) clean[p] = Number(timers[p]) })
  await admin.updateScenario(id, { timers: clean })
  ui.toast('Timers saved', 'success')
}
async function runValidate() {
  await admin.validate(id)
}
async function togglePublish() {
  try {
    if (s.value.is_published) await admin.unpublish(id)
    else await admin.publish(id)
    ui.toast(s.value.is_published ? 'Published' : 'Unpublished', 'success')
  } catch (e) {
    ui.toast('Fix validation errors first', 'error')
    await runValidate()
  }
}
</script>

<template>
  <div v-if="s" class="max-w-5xl mx-auto px-4 py-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <RouterLink to="/admin" class="text-xs text-evidence/50 hover:text-amber-glow">← Studio</RouterLink>
        <h1 class="font-display text-2xl text-amber-glow">{{ s.title }}</h1>
      </div>
      <button
        class="btn text-sm"
        :class="s.is_published ? 'btn-ghost' : 'btn-amber'"
        @click="togglePublish"
      >{{ s.is_published ? 'Unpublish' : 'Publish' }}</button>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 flex-wrap border-b border-noir-800 pb-2">
      <button
        v-for="t in TABS"
        :key="t"
        class="px-3 py-1.5 rounded-lg text-sm"
        :class="tab === t ? 'bg-amber-glow text-noir-950' : 'text-evidence/60 hover:bg-noir-800'"
        @click="tab = t"
      >{{ t }}</button>
    </div>

    <!-- General -->
    <div v-if="tab === 'General'" class="card p-5 space-y-3 max-w-2xl">
      <div><label class="label">Title</label><input v-model="general.title" class="input" /></div>
      <div>
        <label class="label">Genre</label>
        <select v-model="general.genre_id" class="input">
          <option v-for="g in admin.genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div><label class="label">Intro</label><textarea v-model="general.intro_text" class="input" rows="3" /></div>
      <div><label class="label">Task</label><textarea v-model="general.task_text" class="input" rows="2" /></div>
      <div class="grid grid-cols-4 gap-2">
        <div><label class="label">Difficulty</label><input v-model.number="general.difficulty" type="number" class="input" /></div>
        <div><label class="label">Min</label><input v-model.number="general.min_players" type="number" class="input" /></div>
        <div><label class="label">Max</label><input v-model.number="general.max_players" type="number" class="input" /></div>
        <div><label class="label">Rounds</label><input v-model.number="general.rounds" type="number" class="input" /></div>
      </div>
      <button class="btn-amber" @click="saveGeneral">{{ $t('common.save') }}</button>
    </div>

    <LocationEditor v-else-if="tab === 'Locations'" :scenario="s" />
    <RoleEditor v-else-if="tab === 'Roles'" :scenario="s" />
    <EvidenceEditor v-else-if="tab === 'Evidence'" :scenario="s" />
    <EventEditor v-else-if="tab === 'Events'" :scenario="s" />

    <!-- Final Answer -->
    <div v-else-if="tab === 'Final Answer'" class="card p-5 space-y-3 max-w-2xl">
      <div>
        <label class="label">Correct location</label>
        <select v-model="general.correct_location_id" class="input">
          <option :value="null">— none —</option>
          <option v-for="l in s.locations" :key="l.id" :value="l.id">{{ l.name }}</option>
        </select>
      </div>
      <div><label class="label">Correct answer text</label><input v-model="general.correct_answer_text" class="input" /></div>
      <div><label class="label">Truth story (revealed at the end)</label><textarea v-model="general.truth_story" class="input" rows="5" /></div>
      <button class="btn-amber" @click="saveGeneral">{{ $t('common.save') }}</button>
    </div>

    <!-- Timers -->
    <div v-else-if="tab === 'Timers'" class="card p-5 space-y-3 max-w-md">
      <p class="text-xs text-evidence/50">Seconds per phase. Leave blank for defaults.</p>
      <div v-for="p in PHASES" :key="p" class="flex items-center justify-between">
        <label class="label mb-0 capitalize">{{ p }}</label>
        <input v-model="timers[p]" type="number" class="input w-32" />
      </div>
      <button class="btn-amber" @click="saveTimers">{{ $t('common.save') }}</button>
    </div>

    <!-- Validate -->
    <div v-else-if="tab === 'Validate'" class="card p-5 space-y-3 max-w-2xl">
      <button class="btn-amber" @click="runValidate">Run validation</button>
      <div v-if="admin.validation">
        <p class="font-display" :class="admin.validation.valid ? 'text-emerald-400' : 'text-red-400'">
          {{ admin.validation.valid ? '✓ Ready to publish' : '✗ Not ready' }}
        </p>
        <ul class="mt-2 space-y-1 text-sm">
          <li v-for="(e, i) in admin.validation.errors" :key="'e' + i" class="text-red-400">✗ {{ e }}</li>
          <li v-for="(w, i) in admin.validation.warnings" :key="'w' + i" class="text-amber-glow/80">⚠ {{ w }}</li>
        </ul>
      </div>
    </div>
  </div>
  <div v-else class="text-center py-20 text-evidence/40">{{ $t('common.loading') }}</div>
</template>
