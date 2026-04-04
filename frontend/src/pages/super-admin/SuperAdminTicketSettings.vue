<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-primary">Ticket Settings</h1>
      <p class="text-sm text-muted mt-1">Configure queues, SLA policies, routing, canned responses, tags, and roles</p>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 overflow-x-auto border-b border-border-color/40 pb-px">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap"
        :class="activeTab === tab.key
          ? 'bg-card border border-b-0 border-border-color/70 text-primary'
          : 'text-muted hover:text-primary'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Queues -->
    <Card v-if="activeTab === 'queues'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">Queues</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('queues')">Add Queue</button>
      </div>
      <div v-if="data.queues.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.queues.rows.length" class="text-center py-6 text-muted text-sm">No queues configured</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in data.queues.rows"
          :key="item.id"
          class="flex items-center justify-between gap-3 rounded-lg border border-border-color/50 px-4 py-3"
        >
          <div class="min-w-0">
            <p class="font-medium text-primary text-sm">{{ item.name }}</p>
            <p v-if="item.description" class="text-xs text-muted truncate">{{ item.description }}</p>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" :class="tinyBtn('edit')" @click="openEditModal('queues', item)">Edit</button>
            <button type="button" :class="tinyBtn('delete')" @click="deleteItem('queues', item)">Delete</button>
          </div>
        </div>
      </div>
    </Card>

    <!-- SLA Policies -->
    <Card v-if="activeTab === 'sla'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">SLA Policies</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('sla')">Add Policy</button>
      </div>
      <div v-if="data.sla.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.sla.rows.length" class="text-center py-6 text-muted text-sm">No SLA policies configured</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in data.sla.rows"
          :key="item.id"
          class="flex items-center justify-between gap-3 rounded-lg border border-border-color/50 px-4 py-3"
        >
          <div class="min-w-0">
            <p class="font-medium text-primary text-sm">{{ item.name }}</p>
            <p class="text-xs text-muted">
              Response: {{ item.first_response_minutes ?? '—' }}m · Resolution: {{ item.resolution_minutes ?? '—' }}m · Priority: {{ item.priority || 'any' }}
            </p>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" :class="tinyBtn('edit')" @click="openEditModal('sla', item)">Edit</button>
            <button type="button" :class="tinyBtn('delete')" @click="deleteItem('sla', item)">Delete</button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Routing Rules -->
    <Card v-if="activeTab === 'routing'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">Routing Rules</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('routing')">Add Rule</button>
      </div>
      <div v-if="data.routing.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.routing.rows.length" class="text-center py-6 text-muted text-sm">No routing rules configured</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in data.routing.rows"
          :key="item.id"
          class="flex items-center justify-between gap-3 rounded-lg border border-border-color/50 px-4 py-3"
        >
          <div class="min-w-0">
            <p class="font-medium text-primary text-sm">{{ item.name }}</p>
            <p class="text-xs text-muted truncate">{{ item.description || item.condition_summary || '—' }}</p>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" :class="tinyBtn('edit')" @click="openEditModal('routing', item)">Edit</button>
            <button type="button" :class="tinyBtn('delete')" @click="deleteItem('routing', item)">Delete</button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Canned Responses -->
    <Card v-if="activeTab === 'canned'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">Canned Responses</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('canned')">Add Response</button>
      </div>
      <div v-if="data.canned.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.canned.rows.length" class="text-center py-6 text-muted text-sm">No canned responses configured</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in data.canned.rows"
          :key="item.id"
          class="flex items-center justify-between gap-3 rounded-lg border border-border-color/50 px-4 py-3"
        >
          <div class="min-w-0">
            <p class="font-medium text-primary text-sm">{{ item.title }}</p>
            <p class="text-xs text-muted truncate">{{ item.body?.substring(0, 80) || '—' }}</p>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" :class="tinyBtn('edit')" @click="openEditModal('canned', item)">Edit</button>
            <button type="button" :class="tinyBtn('delete')" @click="deleteItem('canned', item)">Delete</button>
          </div>
        </div>
      </div>
    </Card>

    <!-- Tags -->
    <Card v-if="activeTab === 'tags'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">Tags</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('tags')">Add Tag</button>
      </div>
      <div v-if="data.tags.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.tags.rows.length" class="text-center py-6 text-muted text-sm">No tags configured</div>
      <div v-else class="flex flex-wrap gap-2">
        <div
          v-for="item in data.tags.rows"
          :key="item.id"
          class="inline-flex items-center gap-2 rounded-full border border-border-color/70 px-3 py-1.5"
        >
          <span class="text-sm text-primary">{{ item.name }}</span>
          <button type="button" class="text-muted hover:text-red-400 transition-colors text-xs" @click="deleteItem('tags', item)">&times;</button>
        </div>
      </div>
    </Card>

    <!-- Roles -->
    <Card v-if="activeTab === 'roles'">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-primary">Ticket Roles</h2>
        <button type="button" class="btn-primary px-3 py-1.5 rounded-lg text-xs" @click="openModal('roles')">Add Role</button>
      </div>
      <div v-if="data.roles.loading" class="text-center py-6 text-muted text-sm">Loading…</div>
      <div v-else-if="!data.roles.rows.length" class="text-center py-6 text-muted text-sm">No ticket roles configured</div>
      <div v-else class="space-y-2">
        <div
          v-for="item in data.roles.rows"
          :key="item.id"
          class="flex items-center justify-between gap-3 rounded-lg border border-border-color/50 px-4 py-3"
        >
          <div class="min-w-0">
            <p class="font-medium text-primary text-sm">{{ item.name }}</p>
            <p v-if="item.permissions?.length" class="text-xs text-muted truncate">{{ item.permissions.join(', ') }}</p>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" :class="tinyBtn('edit')" @click="openEditModal('roles', item)">Edit</button>
            <button type="button" :class="tinyBtn('delete')" @click="deleteItem('roles', item)">Delete</button>
          </div>
        </div>
      </div>
    </Card>

    <!-- CRUD Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 bg-black/55 backdrop-blur-sm p-4 flex items-center justify-center"
      @click.self="closeModal"
    >
      <div class="w-full max-w-lg rounded-2xl border border-border-color bg-card p-5 space-y-4">
        <div class="flex items-start justify-between gap-3">
          <h2 class="text-lg font-semibold text-primary">{{ modalTitle }}</h2>
          <button type="button" class="btn-outline px-3 py-1 text-xs rounded-lg" @click="closeModal">Close</button>
        </div>

        <!-- Queue form -->
        <template v-if="modalSection === 'queues'">
          <div>
            <label class="label-base block text-sm mb-1">Name *</label>
            <input v-model="modalForm.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Description</label>
            <textarea v-model="modalForm.description" rows="2" class="input-base w-full px-3 py-2 rounded-lg resize-y" />
          </div>
        </template>

        <!-- SLA form -->
        <template v-if="modalSection === 'sla'">
          <div>
            <label class="label-base block text-sm mb-1">Name *</label>
            <input v-model="modalForm.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label-base block text-sm mb-1">First Response (min)</label>
              <input v-model.number="modalForm.first_response_minutes" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Resolution (min)</label>
              <input v-model.number="modalForm.resolution_minutes" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Priority</label>
            <select v-model="modalForm.priority" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Any</option>
              <option value="low">Low</option>
              <option value="medium">Normal</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </template>

        <!-- Routing form -->
        <template v-if="modalSection === 'routing'">
          <div>
            <label class="label-base block text-sm mb-1">Name *</label>
            <input v-model="modalForm.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Description</label>
            <textarea v-model="modalForm.description" rows="2" class="input-base w-full px-3 py-2 rounded-lg resize-y" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Condition (JSON)</label>
            <textarea v-model="modalForm.condition" rows="3" class="input-base w-full px-3 py-2 rounded-lg resize-y font-mono text-xs" placeholder='{"priority": "critical"}' />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Target Queue ID</label>
            <input v-model="modalForm.target_queue_id" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </template>

        <!-- Canned response form -->
        <template v-if="modalSection === 'canned'">
          <div>
            <label class="label-base block text-sm mb-1">Title *</label>
            <input v-model="modalForm.title" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Body *</label>
            <textarea v-model="modalForm.body" rows="5" class="input-base w-full px-3 py-2 rounded-lg resize-y" />
          </div>
        </template>

        <!-- Tag form -->
        <template v-if="modalSection === 'tags'">
          <div>
            <label class="label-base block text-sm mb-1">Tag Name *</label>
            <input v-model="modalForm.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </template>

        <!-- Role form -->
        <template v-if="modalSection === 'roles'">
          <div>
            <label class="label-base block text-sm mb-1">Name *</label>
            <input v-model="modalForm.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Permissions (comma-separated)</label>
            <input v-model="modalForm.permissions_raw" type="text" class="input-base w-full px-3 py-2 rounded-lg" placeholder="view, reply, assign, transition" />
          </div>
        </template>

        <div class="flex items-center justify-end gap-2">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="closeModal">Cancel</button>
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="modalSaving" @click="submitModal">
            {{ modalSaving ? 'Saving…' : (editingItem ? 'Save Changes' : 'Create') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformTicketsAPI } from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'

const notify = useNotification()

const tabs = [
  { key: 'queues', label: 'Queues' },
  { key: 'sla', label: 'SLA Policies' },
  { key: 'routing', label: 'Routing Rules' },
  { key: 'canned', label: 'Canned Responses' },
  { key: 'tags', label: 'Tags' },
  { key: 'roles', label: 'Roles' },
]

const activeTab = ref('queues')
const showModal = ref(false)
const modalSection = ref('')
const modalSaving = ref(false)
const editingItem = ref(null)
const modalForm = ref({})

const data = reactive({
  queues: { loading: false, rows: [] },
  sla: { loading: false, rows: [] },
  routing: { loading: false, rows: [] },
  canned: { loading: false, rows: [] },
  tags: { loading: false, rows: [] },
  roles: { loading: false, rows: [] },
})

const apiMap = {
  queues: { list: platformTicketsAPI.queues, create: platformTicketsAPI.createQueue, update: platformTicketsAPI.updateQueue, remove: platformTicketsAPI.deleteQueue },
  sla: { list: platformTicketsAPI.slaPolicies, create: platformTicketsAPI.createSlaPolicy, update: platformTicketsAPI.updateSlaPolicy, remove: platformTicketsAPI.deleteSlaPolicy },
  routing: { list: platformTicketsAPI.routingRules, create: platformTicketsAPI.createRoutingRule, update: platformTicketsAPI.updateRoutingRule, remove: platformTicketsAPI.deleteRoutingRule },
  canned: { list: platformTicketsAPI.cannedResponses, create: platformTicketsAPI.createCannedResponse, update: platformTicketsAPI.updateCannedResponse, remove: platformTicketsAPI.deleteCannedResponse },
  tags: { list: platformTicketsAPI.tags, create: platformTicketsAPI.createTag, remove: platformTicketsAPI.deleteTag },
  roles: { list: platformTicketsAPI.roles, create: platformTicketsAPI.createRole, update: platformTicketsAPI.updateRole, remove: platformTicketsAPI.deleteRole },
}

const modalTitle = computed(() => {
  const labels = { queues: 'Queue', sla: 'SLA Policy', routing: 'Routing Rule', canned: 'Canned Response', tags: 'Tag', roles: 'Role' }
  const label = labels[modalSection.value] || 'Item'
  return editingItem.value ? `Edit ${label}` : `Add ${label}`
})

function tinyBtn(kind) {
  const base = 'inline-flex items-center justify-center rounded-lg border px-2 py-1 text-[11px] font-medium transition-colors'
  if (kind === 'edit') return `${base} border-cyan-500/40 bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20`
  if (kind === 'delete') return `${base} border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20`
  return `${base} border-border-color/70 text-muted hover:bg-card`
}

function defaultForm(section) {
  if (section === 'queues') return { name: '', description: '' }
  if (section === 'sla') return { name: '', first_response_minutes: null, resolution_minutes: null, priority: '' }
  if (section === 'routing') return { name: '', description: '', condition: '', target_queue_id: '' }
  if (section === 'canned') return { title: '', body: '' }
  if (section === 'tags') return { name: '' }
  if (section === 'roles') return { name: '', permissions_raw: '' }
  return {}
}

function openModal(section) {
  modalSection.value = section
  editingItem.value = null
  modalForm.value = defaultForm(section)
  showModal.value = true
}

function openEditModal(section, item) {
  modalSection.value = section
  editingItem.value = item
  const form = { ...item }
  if (section === 'roles' && Array.isArray(item.permissions)) {
    form.permissions_raw = item.permissions.join(', ')
  }
  modalForm.value = form
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingItem.value = null
}

async function loadSection(section) {
  const entry = data[section]
  const api = apiMap[section]
  if (!api?.list) return
  entry.loading = true
  try {
    const { data: resp } = await api.list()
    entry.rows = resp.results ?? resp
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || `Failed to load ${section}`)
  } finally {
    entry.loading = false
  }
}

async function submitModal() {
  const section = modalSection.value
  const api = apiMap[section]
  if (!api) return

  modalSaving.value = true
  try {
    const payload = { ...modalForm.value }

    if (section === 'roles' && payload.permissions_raw != null) {
      payload.permissions = payload.permissions_raw.split(',').map((s) => s.trim()).filter(Boolean)
      delete payload.permissions_raw
    }
    delete payload.id

    if (editingItem.value?.id && api.update) {
      await api.update(editingItem.value.id, payload)
      notify.success('Updated.')
    } else {
      await api.create(payload)
      notify.success('Created.')
    }
    closeModal()
    await loadSection(section)
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Save failed')
  } finally {
    modalSaving.value = false
  }
}

async function deleteItem(section, item) {
  const api = apiMap[section]
  if (!api?.remove) return
  const ok = window.confirm(`Delete "${item.name || item.title || item.id}"?`)
  if (!ok) return
  try {
    await api.remove(item.id)
    notify.success('Deleted.')
    await loadSection(section)
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Delete failed')
  }
}

onMounted(() => {
  for (const key of Object.keys(apiMap)) {
    loadSection(key)
  }
})
</script>
