<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Global users</h1>
        <p class="text-sm text-muted mt-1">Search and manage accounts across all tenants</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </div>

    <div
      v-if="truncationNotice"
      class="rounded-2xl border border-cyan-500/30 bg-cyan-500/10 px-4 py-3 text-sm text-secondary"
    >
      {{ truncationNotice }}
    </div>

    <Card>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <div class="lg:col-span-2">
          <label class="label-base block text-sm mb-1">Search</label>
          <input
            v-model="search"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Username or email…"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Tenant</label>
          <select v-model="filters.tenantId" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
            <option value="">All tenants</option>
            <option v-for="t in tenantOptions" :key="t.id" :value="t.id">{{ t.name }}</option>
          </select>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Role</label>
          <select v-model="filters.role" class="select-base w-full px-3 py-2 rounded-lg">
            <option value="">All roles</option>
            <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="text-center py-10 text-muted">Loading…</div>
      <div
        v-else-if="loadError"
        class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
      >
        {{ loadError }}
      </div>
      <div v-else-if="!filteredRows.length" class="text-center py-12 text-muted">
        <p>No users match your filters</p>
      </div>
      <div v-else class="space-y-4">
        <div class="grid gap-3 lg:hidden">
          <article
            v-for="row in filteredRows"
            :key="`m-${row.id}`"
            class="rounded-xl border border-border-color/70 bg-card/50 p-4 space-y-3"
          >
            <div class="flex justify-between gap-2">
              <div class="min-w-0">
                <p class="font-semibold text-primary truncate">{{ row.username }}</p>
                <p class="text-xs text-muted truncate">{{ row.email }}</p>
              </div>
              <span class="text-[11px] px-2 py-1 rounded-full border shrink-0" :class="statusClass(row)">
                {{ statusLabel(row) }}
              </span>
            </div>
            <div class="text-xs space-y-1 text-secondary">
              <p><span class="text-muted">Role:</span> {{ row.role_display || row.role }}</p>
              <p><span class="text-muted">Tenant:</span> {{ tenantLabel(row) }}</p>
              <p><span class="text-muted">Last seen:</span> {{ formatDate(row.last_seen) }}</p>
            </div>
            <div class="flex flex-wrap gap-2 justify-end">
              <button
                type="button"
                class="btn-outline px-3 py-1.5 rounded-lg text-xs"
                :disabled="actionBusyId === row.id"
                @click="toggleLock(row)"
              >
                {{ row.is_lock_active ? 'Unlock' : 'Lock' }}
              </button>
              <button type="button" class="btn-outline px-3 py-1.5 rounded-lg text-xs" @click="openPasswordModal(row)">
                Reset password
              </button>
              <button
                type="button"
                class="btn-primary px-3 py-1.5 rounded-lg text-xs"
                :disabled="actionBusyId === row.id"
                @click="revokeSessions(row)"
              >
                Revoke sessions
              </button>
            </div>
          </article>
        </div>

        <div class="hidden lg:block overflow-x-auto">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Username</th>
                <th class="py-2 pr-4">Email</th>
                <th class="py-2 pr-4">Role</th>
                <th class="py-2 pr-4">Tenant</th>
                <th class="py-2 pr-4">Last seen</th>
                <th class="py-2 pr-4">Status</th>
                <th class="py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="row in filteredRows"
                :key="row.id"
                class="border-b border-border-color/60 hover:bg-slate-50/50 dark:hover:bg-slate-800/30"
              >
                <td class="py-2 pr-4 font-medium text-primary">{{ row.username }}</td>
                <td class="py-2 pr-4 text-secondary">{{ row.email }}</td>
                <td class="py-2 pr-4">{{ row.role_display || row.role }}</td>
                <td class="py-2 pr-4 text-secondary text-xs">{{ tenantLabel(row) }}</td>
                <td class="py-2 pr-4 text-muted text-xs whitespace-nowrap">{{ formatDate(row.last_seen) }}</td>
                <td class="py-2 pr-4">
                  <span class="text-[11px] px-2 py-1 rounded-full border" :class="statusClass(row)">
                    {{ statusLabel(row) }}
                  </span>
                </td>
                <td class="py-2 text-right">
                  <div class="flex flex-wrap justify-end gap-1.5">
                    <button
                      type="button"
                      class="btn-outline px-2 py-1 rounded-lg text-xs"
                      :disabled="actionBusyId === row.id"
                      @click="toggleLock(row)"
                    >
                      {{ row.is_lock_active ? 'Unlock' : 'Lock' }}
                    </button>
                    <button type="button" class="btn-outline px-2 py-1 rounded-lg text-xs" @click="openPasswordModal(row)">
                      Reset password
                    </button>
                    <button
                      type="button"
                      class="btn-primary px-2 py-1 rounded-lg text-xs"
                      :disabled="actionBusyId === row.id"
                      @click="revokeSessions(row)"
                    >
                      Revoke sessions
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </Card>

    <div
      v-if="passwordModal.open"
      class="fixed inset-0 z-50 bg-black/55 backdrop-blur-sm p-4 flex items-center justify-center"
      @click.self="passwordModal.open = false"
    >
      <div class="w-full max-w-sm rounded-2xl border border-border-color bg-card p-5 space-y-4">
        <h2 class="text-lg font-semibold text-primary">Set new password</h2>
        <p class="text-xs text-muted">{{ passwordModal.user?.username }}</p>
        <input
          v-model="passwordModal.value"
          type="password"
          class="input-base w-full px-3 py-2 rounded-lg"
          placeholder="New password"
          autocomplete="new-password"
        />
        <div class="flex justify-end gap-2">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="passwordModal.open = false">
            Cancel
          </button>
          <button
            type="button"
            class="btn-primary px-4 py-2 rounded-lg text-sm"
            :disabled="passwordSubmitting"
            @click="submitPassword"
          >
            {{ passwordSubmitting ? 'Saving…' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import api, { platformAPI, usersAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const loadError = ref(null)
const rows = ref([])
const tenantNameById = ref({})
const search = ref('')
const filters = ref({ tenantId: '', role: '' })
const actionBusyId = ref(null)
const passwordModal = ref({ open: false, user: null, value: '' })
const passwordSubmitting = ref(false)
const truncationNotice = ref('')

const roleOptions = ['Developer', 'Manager', 'Employee', 'Visitor']

const tenantOptions = computed(() =>
  Object.entries(tenantNameById.value).map(([id, name]) => ({ id, name })),
)

const filteredRows = computed(() => {
  let list = rows.value
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(
      (u) =>
        (u.username && u.username.toLowerCase().includes(q)) || (u.email && u.email.toLowerCase().includes(q)),
    )
  }
  if (filters.value.role) {
    list = list.filter((u) => u.role === filters.value.role)
  }
  return list
})

function statusLabel(row) {
  if (row.is_lock_active) return 'Locked'
  if (row.is_active === false) return 'Inactive'
  return 'Active'
}

function statusClass(row) {
  if (row.is_lock_active) return 'border-amber-500/50 text-amber-700 dark:text-amber-200'
  if (row.is_active === false) return 'border-slate-500/40 text-muted'
  return 'border-emerald-500/40 text-emerald-700 dark:text-emerald-200'
}

function tenantLabel(row) {
  const tid = row.tenant_id
  if (tid && tenantNameById.value[tid]) return tenantNameById.value[tid]
  return row.organization_name || '—'
}

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

async function fetchTenantsMap() {
  const { data } = await platformAPI.tenants.list({ page_size: 500 })
  const map = {}
  const list = data.results || data || []
  for (const t of list) {
    map[String(t.id)] = t.name
  }
  tenantNameById.value = map
}

async function fetchAllUsers() {
  const acc = []
  let page = 1
  const params = { page_size: 100 }
  if (filters.value.tenantId) params.tenant_id = filters.value.tenantId

  for (;;) {
    const { data } = await api.get('/users/', { params: { ...params, page } })
    const chunk = data.results || []
    acc.push(...chunk)
    if (!data.next || !chunk.length) break
    page += 1
    if (page > 200) break
  }
  return acc
}

async function enrichUsers(list) {
  const chunkSize = 20
  const out = []
  for (let i = 0; i < list.length; i += chunkSize) {
    const slice = list.slice(i, i + chunkSize)
    const details = await Promise.all(
      slice.map((u) =>
        usersAPI
          .detail(u.id)
          .then((r) => ({ ...u, ...r.data }))
          .catch(() => u),
      ),
    )
    out.push(...details)
  }
  return out
}

const MAX_DETAIL_ENRICH = 250

async function load() {
  loading.value = true
  loadError.value = null
  truncationNotice.value = ''
  try {
    await fetchTenantsMap()
    const base = await fetchAllUsers()
    const slice = base.slice(0, MAX_DETAIL_ENRICH)
    rows.value = await enrichUsers(slice)
    if (base.length > MAX_DETAIL_ENRICH) {
      truncationNotice.value = `Loaded detail for the first ${MAX_DETAIL_ENRICH} of ${base.length} users. Filter by tenant to reduce the set.`
    }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load users'
    rows.value = []
  } finally {
    loading.value = false
  }
}

async function toggleLock(row) {
  actionBusyId.value = row.id
  try {
    if (row.is_lock_active) {
      await usersAPI.unlock(row.id)
    } else {
      await usersAPI.lock(row.id, { reason: 'Super admin lock' })
    }
    const { data } = await usersAPI.detail(row.id)
    const idx = rows.value.findIndex((r) => r.id === row.id)
    if (idx >= 0) rows.value[idx] = { ...rows.value[idx], ...data }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Action failed'
  } finally {
    actionBusyId.value = null
  }
}

async function revokeSessions(row) {
  actionBusyId.value = row.id
  try {
    await usersAPI.revokeSessions(row.id)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not revoke sessions'
  } finally {
    actionBusyId.value = null
  }
}

function openPasswordModal(row) {
  passwordModal.value = { open: true, user: row, value: '' }
}

async function submitPassword() {
  const u = passwordModal.value.user
  if (!u || !passwordModal.value.value) return
  passwordSubmitting.value = true
  try {
    await usersAPI.adminSetPassword(u.id, { new_password: passwordModal.value.value })
    passwordModal.value = { open: false, user: null, value: '' }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Password reset failed'
  } finally {
    passwordSubmitting.value = false
  }
}

onMounted(load)
</script>
