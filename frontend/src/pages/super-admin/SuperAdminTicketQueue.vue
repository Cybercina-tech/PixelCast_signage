<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Ticket Queue</h1>
        <p class="text-sm text-muted mt-1">Manage and triage all customer support tickets</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="load" :disabled="loading">
        Refresh
      </button>
    </div>

    <Card>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 mb-4">
        <div>
          <label class="label-base block text-sm mb-1">Tenant</label>
          <input
            v-model="filters.tenant"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Tenant name…"
            @keyup.enter="load"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Status</label>
          <select v-model="filters.status" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
            <option value="">All</option>
            <option value="open">Open</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="pending">Pending</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Priority</label>
          <select v-model="filters.priority" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
            <option value="">All</option>
            <option value="low">Low</option>
            <option value="normal">Normal</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Assignee</label>
          <input
            v-model="filters.assignee"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Assignee name…"
            @keyup.enter="load"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Queue</label>
          <input
            v-model="filters.queue"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Queue name…"
            @keyup.enter="load"
          />
        </div>
      </div>

      <div v-if="loading" class="text-center py-8 text-muted">Loading…</div>
      <div v-else-if="error" class="text-center py-8 text-red-600">{{ error }}</div>
      <div v-else-if="!rows.length" class="text-center py-12 text-muted">
        <p>No tickets match your filters</p>
      </div>
      <div v-else class="space-y-4">
        <!-- Mobile cards -->
        <div class="grid gap-3 lg:hidden">
          <article
            v-for="row in rows"
            :key="`card-${row.id}`"
            class="rounded-xl border border-border-color/70 bg-card/50 p-4"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0">
                <p class="text-[10px] text-muted uppercase tracking-wider">{{ row.tenant_name }}</p>
                <p class="text-[11px] font-mono text-muted">#{{ row.ticket_number }}</p>
                <h3 class="font-semibold text-primary truncate">{{ row.subject }}</h3>
              </div>
              <span class="text-[11px] px-2 py-1 rounded-full border capitalize shrink-0" :class="statusClass(row.status)">
                {{ formatStatus(row.status) }}
              </span>
            </div>
            <div class="mt-3 flex items-center justify-between text-xs flex-wrap gap-2">
              <span class="px-2 py-0.5 rounded-full border capitalize" :class="priorityClass(row.priority)">{{ row.priority }}</span>
              <span class="text-muted">{{ row.assignee_name || 'Unassigned' }}</span>
              <span :class="slaStatusClass(row)">{{ slaStatusLabel(row) }}</span>
            </div>
            <div class="mt-3 flex items-center justify-end gap-2 text-xs">
              <button type="button" :class="actionBtnClass('assign')" @click="openAssignModal(row)">Assign</button>
              <select
                class="select-base px-2 py-1 rounded-lg text-xs"
                @change="handleTransition(row, $event.target.value); $event.target.value = ''"
              >
                <option value="">Transition…</option>
                <option value="start_progress">Start Progress</option>
                <option value="pend">Pend</option>
                <option value="resolve">Resolve</option>
                <option value="close">Close</option>
                <option value="reopen">Reopen</option>
                <option value="escalate">Escalate</option>
              </select>
              <router-link :to="`/super-admin/tickets/${row.id}`" :class="actionBtnClass('open')">View</router-link>
            </div>
          </article>
        </div>

        <!-- Desktop table -->
        <div class="hidden lg:block overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Tenant</th>
                <th class="py-2 pr-4">Ticket</th>
                <th class="py-2 pr-4">Subject</th>
                <th class="py-2 pr-4">Status</th>
                <th class="py-2 pr-4">Priority</th>
                <th class="py-2 pr-4">Assignee</th>
                <th class="py-2 pr-4">SLA</th>
                <th class="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in rows"
                :key="row.id"
                class="border-b border-border-color/60 hover:bg-slate-50/50 dark:hover:bg-slate-800/30"
              >
                <td class="py-2 pr-4 text-secondary text-xs">{{ row.tenant_name }}</td>
                <td class="py-2 pr-4 font-mono text-muted text-xs">#{{ row.ticket_number }}</td>
                <td class="py-2 pr-4 font-medium text-primary max-w-xs truncate">{{ row.subject }}</td>
                <td class="py-2 pr-4">
                  <span class="text-[11px] px-2 py-1 rounded-full border capitalize" :class="statusClass(row.status)">
                    {{ formatStatus(row.status) }}
                  </span>
                </td>
                <td class="py-2 pr-4">
                  <span class="text-[11px] px-2 py-1 rounded-full border capitalize" :class="priorityClass(row.priority)">
                    {{ row.priority }}
                  </span>
                </td>
                <td class="py-2 pr-4 text-secondary">{{ row.assignee_name || '—' }}</td>
                <td class="py-2 pr-4">
                  <span class="text-xs" :class="slaStatusClass(row)">{{ slaStatusLabel(row) }}</span>
                </td>
                <td class="py-2 text-right">
                  <div class="flex items-center justify-end gap-1.5">
                    <button type="button" :class="`${actionBtnClass('assign')}`" @click="openAssignModal(row)">Assign</button>
                    <select
                      class="select-base px-2 py-1 rounded-lg text-xs"
                      @change="handleTransition(row, $event.target.value); $event.target.value = ''"
                    >
                      <option value="">Transition…</option>
                      <option value="start_progress">Start Progress</option>
                      <option value="pend">Pend</option>
                      <option value="resolve">Resolve</option>
                      <option value="close">Close</option>
                      <option value="reopen">Reopen</option>
                      <option value="escalate">Escalate</option>
                    </select>
                    <router-link :to="`/super-admin/tickets/${row.id}`" :class="actionBtnClass('open')">View</router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <!-- Assign modal -->
    <div
      v-if="showAssignModal"
      class="fixed inset-0 z-50 bg-black/55 backdrop-blur-sm p-4 flex items-center justify-center"
      @click.self="showAssignModal = false"
    >
      <div class="w-full max-w-sm rounded-2xl border border-border-color bg-card p-5 space-y-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-primary">Assign Ticket</h2>
            <p class="text-xs text-muted mt-1">#{{ assignTarget?.ticket_number }} — {{ assignTarget?.subject }}</p>
          </div>
          <button type="button" class="btn-outline px-3 py-1 text-xs rounded-lg" @click="showAssignModal = false">Close</button>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Assignee User ID</label>
          <input v-model="assignUserId" type="text" class="input-base w-full px-3 py-2 rounded-lg" placeholder="Enter user ID" />
        </div>
        <div class="flex items-center justify-end gap-2">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="showAssignModal = false">Cancel</button>
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="assigning" @click="submitAssign">
            {{ assigning ? 'Assigning…' : 'Assign' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformTicketsAPI } from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(false)
const error = ref(null)
const rows = ref([])
const filters = ref({ tenant: '', status: '', priority: '', assignee: '', queue: '' })
const notify = useNotification()

const showAssignModal = ref(false)
const assignTarget = ref(null)
const assignUserId = ref('')
const assigning = ref(false)

function statusClass(status) {
  const map = {
    open: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300',
    assigned: 'border-blue-500/30 bg-blue-500/10 text-blue-300',
    in_progress: 'border-violet-500/30 bg-violet-500/10 text-violet-300',
    pending: 'border-amber-500/30 bg-amber-500/10 text-amber-300',
    resolved: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300',
    closed: 'border-slate-500/30 bg-slate-500/10 text-slate-400',
  }
  return map[status] || 'border-border-color/70 bg-card text-muted'
}

function priorityClass(priority) {
  const map = {
    low: 'border-slate-500/30 bg-slate-500/10 text-slate-400',
    normal: 'border-blue-500/30 bg-blue-500/10 text-blue-300',
    high: 'border-orange-500/30 bg-orange-500/10 text-orange-300',
    urgent: 'border-red-500/30 bg-red-500/10 text-red-300',
  }
  return map[priority] || 'border-border-color/70 bg-card text-muted'
}

function formatStatus(s) {
  return s?.replace(/_/g, ' ') || s
}

function actionBtnClass(kind) {
  const base = 'inline-flex items-center justify-center rounded-lg border px-2.5 py-1 text-xs font-medium transition-colors'
  if (kind === 'assign') return `${base} border-cyan-500/40 bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20`
  if (kind === 'open') return `${base} border-indigo-500/40 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20`
  return `${base} border-border-color/70 text-muted hover:bg-card`
}

function slaStatusLabel(row) {
  if (!row.resolution_due_at) return '—'
  const diff = new Date(row.resolution_due_at) - Date.now()
  if (diff <= 0) return 'Breached'
  if (diff < 3600000) return 'At risk'
  return 'On track'
}

function slaStatusClass(row) {
  if (!row.resolution_due_at) return 'text-muted'
  const diff = new Date(row.resolution_due_at) - Date.now()
  if (diff <= 0) return 'text-red-400 font-semibold'
  if (diff < 3600000) return 'text-orange-400'
  return 'text-emerald-400'
}

function openAssignModal(row) {
  assignTarget.value = row
  assignUserId.value = ''
  showAssignModal.value = true
}

async function submitAssign() {
  if (!assignUserId.value.trim()) {
    notify.error('User ID is required.')
    return
  }
  assigning.value = true
  try {
    await platformTicketsAPI.assign(assignTarget.value.id, { assignee_id: assignUserId.value.trim() })
    notify.success('Ticket assigned.')
    showAssignModal.value = false
    await load()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Assign failed')
  } finally {
    assigning.value = false
  }
}

async function handleTransition(row, action) {
  if (!action) return
  try {
    await platformTicketsAPI.transition(row.id, { action })
    notify.success(`Ticket transitioned: ${action.replace(/_/g, ' ')}`)
    await load()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Transition failed')
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (filters.value.tenant) params.tenant = filters.value.tenant
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.assignee) params.assignee = filters.value.assignee
    if (filters.value.queue) params.queue = filters.value.queue
    const { data } = await platformTicketsAPI.list(params)
    rows.value = data.results ?? data
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Failed to load ticket queue'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
