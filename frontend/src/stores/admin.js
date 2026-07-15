import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '@/api/http'

/** Backs the admin dashboard + Scenario Studio (writer/admin only). */
export const useAdminStore = defineStore('admin', () => {
  const genres = ref([])
  const scenarios = ref([])
  const current = ref(null) // full ScenarioDetail being edited
  const validation = ref(null)
  const dashboard = ref(null)

  // -- Genres -------------------------------------------------------------
  async function loadGenres() {
    genres.value = (await http.get('/admin/genres')).data
  }
  const createGenre = (body) => http.post('/admin/genres', body).then(loadGenres)
  const updateGenre = (id, body) => http.patch(`/admin/genres/${id}`, body).then(loadGenres)
  const deleteGenre = (id) => http.delete(`/admin/genres/${id}`).then(loadGenres)

  // -- Scenarios ----------------------------------------------------------
  async function loadScenarios() {
    scenarios.value = (await http.get('/admin/scenarios')).data
  }
  async function loadScenario(id) {
    current.value = (await http.get(`/admin/scenarios/${id}`)).data
    return current.value
  }
  const createScenario = (body) => http.post('/admin/scenarios', body).then((r) => r.data)
  const updateScenario = (id, body) =>
    http.patch(`/admin/scenarios/${id}`, body).then(() => loadScenario(id))
  const deleteScenario = (id) => http.delete(`/admin/scenarios/${id}`).then(loadScenarios)

  async function validate(id) {
    validation.value = (await http.get(`/admin/scenarios/${id}/validate`)).data
    return validation.value
  }
  const publish = (id) => http.post(`/admin/scenarios/${id}/publish`).then(() => loadScenario(id))
  const unpublish = (id) => http.post(`/admin/scenarios/${id}/unpublish`).then(() => loadScenario(id))

  async function loadDashboard() {
    dashboard.value = (await http.get('/admin/scenarios/dashboard')).data
  }

  // -- Child entities (reload the scenario detail after each write) -------
  const _refresh = (scenarioId) => loadScenario(scenarioId)

  const saveLocation = (b) =>
    (b.id ? http.patch(`/admin/locations/${b.id}`, b) : http.post('/admin/locations', b)).then(() =>
      _refresh(b.scenario_id ?? current.value.id),
    )
  const deleteLocation = (id, sid) => http.delete(`/admin/locations/${id}`).then(() => _refresh(sid))

  const saveRole = (b) =>
    (b.id ? http.patch(`/admin/roles/${b.id}`, b) : http.post('/admin/roles', b)).then(() =>
      _refresh(b.scenario_id ?? current.value.id),
    )
  const deleteRole = (id, sid) => http.delete(`/admin/roles/${id}`).then(() => _refresh(sid))

  const saveEvidence = (b) =>
    (b.id ? http.patch(`/admin/evidence/${b.id}`, b) : http.post('/admin/evidence', b)).then(() =>
      _refresh(b.scenario_id ?? current.value.id),
    )
  const deleteEvidence = (id, sid) => http.delete(`/admin/evidence/${id}`).then(() => _refresh(sid))
  const coverage = (sid) => http.get('/admin/evidence/coverage', { params: { scenario_id: sid } }).then((r) => r.data)

  const saveEvent = (b) =>
    (b.id ? http.patch(`/admin/events/${b.id}`, b) : http.post('/admin/events', b)).then(() =>
      _refresh(b.scenario_id ?? current.value.id),
    )
  const deleteEvent = (id, sid) => http.delete(`/admin/events/${id}`).then(() => _refresh(sid))

  return {
    genres, scenarios, current, validation, dashboard,
    loadGenres, createGenre, updateGenre, deleteGenre,
    loadScenarios, loadScenario, createScenario, updateScenario, deleteScenario,
    validate, publish, unpublish, loadDashboard,
    saveLocation, deleteLocation, saveRole, deleteRole,
    saveEvidence, deleteEvidence, coverage, saveEvent, deleteEvent,
  }
})
