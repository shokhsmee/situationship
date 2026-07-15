<script setup>
import { ref } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useUiStore } from '@/stores/ui'

const props = defineProps({ scenario: { type: Object, required: true } })
const admin = useAdminStore()
const ui = useUiStore()

const blank = () => ({ scenario_id: props.scenario.id, name: '', description: '', icon: '', can_be_insider: true })
const draft = ref(blank())

const edit = (r) => (draft.value = { ...r })
const reset = () => (draft.value = blank())

async function save() {
  if (!draft.value.name) return
  await admin.saveRole(draft.value)
  ui.toast('Role saved', 'success')
  reset()
}
async function remove(r) {
  await admin.deleteRole(r.id, props.scenario.id)
  ui.toast('Role deleted')
}
</script>

<template>
  <div class="grid lg:grid-cols-2 gap-4">
    <div class="card p-4 space-y-2 h-fit">
      <input v-model="draft.name" class="input" placeholder="Role name (e.g. Mayor)" />
      <textarea v-model="draft.description" class="input" rows="2" placeholder="Description" />
      <input v-model="draft.icon" class="input" placeholder="Icon (e.g. crown)" />
      <label class="flex items-center gap-2 text-sm">
        <input v-model="draft.can_be_insider" type="checkbox" /> Can be the insider
      </label>
      <div class="flex gap-2">
        <button class="btn-amber flex-1" @click="save">{{ draft.id ? 'Update' : 'Add' }}</button>
        <button v-if="draft.id" class="btn-ghost" @click="reset">Cancel</button>
      </div>
    </div>

    <div class="space-y-2">
      <div v-for="r in scenario.roles" :key="r.id" class="card p-3 flex items-center justify-between">
        <span class="text-sm">
          {{ r.name }}
          <span v-if="r.can_be_insider" class="text-red-400 text-xs">· insider-capable</span>
        </span>
        <span class="flex gap-2">
          <button class="text-xs text-amber-glow" @click="edit(r)">Edit</button>
          <button class="text-xs text-red-400" @click="remove(r)">Del</button>
        </span>
      </div>
      <p v-if="!scenario.roles.length" class="text-xs text-evidence/40">No roles yet.</p>
    </div>
  </div>
</template>
