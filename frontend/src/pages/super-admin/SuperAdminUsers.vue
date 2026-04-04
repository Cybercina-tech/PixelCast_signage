<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Global Users</h1>
        <p class="text-sm text-muted mt-1">Manage accounts across all tenants — screens, storage, subscriptions</p>
      </div>
      <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
        Refresh
      </button>
    </div>

    <!-- KPI strip -->
    <div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">Total users</p>
        <p class="text-2xl font-bold text-primary mt-1">{{ kpis.total }}</p>
      </div>
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">With tenant</p>
        <p class="text-2xl font-bold text-primary mt-1">{{ kpis.withTenant }}</p>
      </div>
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">No tenant</p>
        <p class="text-2xl font-bold text-cyan-400 mt-1">{{ kpis.noTenant }}</p>
      </div>
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">Locked</p>
        <p class="text-2xl font-bold text-amber-400 mt-1">{{ kpis.locked }}</p>
      </div>
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">Total screens</p>
        <p class="text-2xl font-bold text-primary mt-1">{{ kpis.totalScreens }}</p>
      </div>
      <div class="card-base rounded-2xl p-4 border border-border-color/80">
        <p class="text-[11px] font-medium text-muted uppercase tracking-wide">Platform storage</p>
        <p class="text-2xl font-bold text-primary mt-1">{{ formatBytes(kpis.totalStorage) }}</p>
      </div>
    </div>

    <!-- Filters -->
    <Card>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        <div class="lg:col-span-2">
          <label class="label-base block text-sm mb-1">Search</label>
          <input
            v-model="search"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Username, email, full name…"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Tenant</label>
          <select v-model="filters.tenantId" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
            <option value="">All</option>
            <option value="__none__">No tenant</option>
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
        <div>
          <label class="label-base block text-sm mb-1">Status</label>
          <select v-model="filters.status" class="select-base w-full px-3 py-2 rounded-lg">
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="locked">Locked</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
      </div>
    </Card>

    <!-- Error -->
    <div
      v-if="loadError"
      class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 5" :key="i" class="card-base rounded-2xl p-5 animate-pulse h-16" />
    </div>

    <!-- Empty -->
    <div v-else-if="!filteredRows.length" class="text-center py-16 text-muted">
      <p class="text-lg">No users match your filters</p>
    </div>

    <!-- Desktop table -->
    <Card v-else>
      <div class="hidden lg:block overflow-x-auto">
        <table class="min-w-full text-sm">
          <thead>
            <tr class="border-b border-border-color text-left text-muted">
              <th class="py-2 pr-3">User</th>
              <th class="py-2 pr-3">Role</th>
              <th class="py-2 pr-3">Tenant / Org</th>
              <th class="py-2 pr-3">Plan</th>
              <th class="py-2 pr-3 text-center">Screens</th>
              <th class="py-2 pr-3 text-center">Templates</th>
              <th class="py-2 pr-3 text-right">Storage</th>
              <th class="py-2 pr-3">Last seen</th>
              <th class="py-2 pr-3">Status</th>
              <th class="py-2 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in filteredRows"
              :key="row.id"
              class="border-b border-border-color/40 hover:bg-slate-50/50 dark:hover:bg-slate-800/20 cursor-pointer"
              @click="openDrawer(row)"
            >
              <td class="py-2.5 pr-3">
                <p class="font-medium text-primary truncate max-w-[160px]">{{ row.username }}</p>
                <p class="text-xs text-muted truncate max-w-[160px]">{{ row.email }}</p>
              </td>
              <td class="py-2.5 pr-3 text-xs">{{ row.role_display || row.role }}</td>
              <td class="py-2.5 pr-3">
                <p class="text-xs text-primary truncate max-w-[140px]">{{ row.tenant_name || '—' }}</p>
                <p v-if="row.organization_name && !row.tenant_name" class="text-[11px] text-muted">{{ row.organization_name }}</p>
              </td>
              <td class="py-2.5 pr-3">
                <span
                  v-if="row.subscription_plan"
                  class="text-[11px] px-2 py-0.5 rounded-full border"
                  :class="planClass(row.subscription_status)"
                >
                  {{ row.subscription_plan }}
                </span>
                <span v-else class="text-muted text-xs">—</span>
              </td>
              <td class="py-2.5 pr-3 text-center font-mono text-xs">
                <span class="text-emerald-500">{{ row.active_screens_count ?? 0 }}</span>
                <span class="text-muted">/</span>
                <span>{{ row.total_screens_count ?? 0 }}</span>
              </td>
              <td class="py-2.5 pr-3 text-center font-mono text-xs">{{ row.total_templates_count ?? 0 }}</td>
              <td class="py-2.5 pr-3 text-right font-mono text-xs">{{ formatBytes(row.storage_used_bytes) }}</td>
              <td class="py-2.5 pr-3 text-muted text-xs whitespace-nowrap">{{ formatDate(row.last_seen) }}</td>
              <td class="py-2.5 pr-3">
                <span class="text-[11px] px-2 py-0.5 rounded-full border" :class="statusClass(row)">
                  {{ statusLabel(row) }}
                </span>
              </td>
              <td class="py-2.5 text-right" @click.stop>
                <div class="flex flex-wrap justify-end gap-1">
                  <button
                    type="button"
                    class="btn-outline px-2 py-1 rounded-lg text-xs"
                    :disabled="actionBusyId === row.id"
                    @click="toggleLock(row)"
                  >
                    {{ row.is_lock_active ? 'Unlock' : 'Lock' }}
                  </button>
                  <router-link
                    :to="{ name: 'super-admin-user-manage', params: { id: row.id } }"
                    class="btn-primary px-2 py-1 rounded-lg text-xs inline-block text-center"
                    @click.stop
                  >
                    Manage
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile cards -->
      <div class="grid gap-3 lg:hidden">
        <article
          v-for="row in filteredRows"
          :key="`m-${row.id}`"
          class="rounded-xl border border-border-color/70 bg-card/50 p-4 space-y-3"
          @click="openDrawer(row)"
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
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div class="rounded-lg bg-slate-800/30 px-2 py-1.5">
              <p class="text-muted">Screens</p>
              <p class="font-semibold">{{ row.active_screens_count ?? 0 }} / {{ row.total_screens_count ?? 0 }}</p>
            </div>
            <div class="rounded-lg bg-slate-800/30 px-2 py-1.5">
              <p class="text-muted">Storage</p>
              <p class="font-semibold">{{ formatBytes(row.storage_used_bytes) }}</p>
            </div>
            <div class="rounded-lg bg-slate-800/30 px-2 py-1.5">
              <p class="text-muted">Tenant</p>
              <p class="font-semibold truncate">{{ row.tenant_name || '—' }}</p>
            </div>
            <div class="rounded-lg bg-slate-800/30 px-2 py-1.5">
              <p class="text-muted">Plan</p>
              <p class="font-semibold">{{ row.subscription_plan || '—' }}</p>
            </div>
          </div>
          <div class="flex flex-wrap gap-2 justify-end" @click.stop>
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
            <router-link
              :to="{ name: 'super-admin-user-manage', params: { id: row.id } }"
              class="btn-primary px-3 py-1.5 rounded-lg text-xs inline-block text-center"
              @click.stop
            >
              Manage
            </router-link>
          </div>
        </article>
      </div>
    </Card>

    <!-- Detail drawer -->
    <div
      v-if="drawer.open"
      class="fixed inset-0 z-50 flex justify-end"
    >
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="drawer.open = false" />
      <div class="relative w-full max-w-lg bg-card border-l border-border-color overflow-y-auto shadow-2xl">
        <div class="sticky top-0 z-10 bg-card/95 backdrop-blur-sm border-b border-border-color px-5 py-4 flex items-start justify-between gap-3">
          <div class="min-w-0">
            <h2 class="text-lg font-bold text-primary truncate">{{ drawer.user?.username }}</h2>
            <p class="text-xs text-muted truncate">{{ drawer.user?.email }}</p>
          </div>
          <button type="button" class="btn-outline px-3 py-1 rounded-lg text-xs shrink-0" @click="drawer.open = false">Close</button>
        </div>

        <div v-if="drawer.user" class="p-5 space-y-5">
          <!-- Identity -->
          <section class="space-y-2">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-muted">Identity</h3>
            <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <div><dt class="text-muted">Full name</dt><dd class="text-primary">{{ drawer.user.full_name || '—' }}</dd></div>
              <div><dt class="text-muted">Role</dt><dd class="text-primary">{{ drawer.user.role_display || drawer.user.role }}</dd></div>
              <div><dt class="text-muted">Organization</dt><dd class="text-primary">{{ drawer.user.organization_name || '—' }}</dd></div>
              <div><dt class="text-muted">Joined</dt><dd class="text-primary">{{ formatDate(drawer.user.date_joined) }}</dd></div>
              <div><dt class="text-muted">Last seen</dt><dd class="text-primary">{{ formatDate(drawer.user.last_seen) }}</dd></div>
              <div>
                <dt class="text-muted">Status</dt>
                <dd>
                  <span class="text-[11px] px-2 py-0.5 rounded-full border" :class="statusClass(drawer.user)">{{ statusLabel(drawer.user) }}</span>
                </dd>
              </div>
            </dl>
          </section>

          <!-- Tenant & subscription -->
          <section class="space-y-2">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-muted">Tenant & Subscription</h3>
            <dl class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
              <div><dt class="text-muted">Tenant</dt><dd class="text-primary">{{ drawer.user.tenant_name || 'None' }}</dd></div>
              <div><dt class="text-muted">Tenant ID</dt><dd class="text-primary font-mono text-xs">{{ drawer.user.tenant_id || '—' }}</dd></div>
              <div><dt class="text-muted">Plan</dt><dd class="text-primary">{{ drawer.user.subscription_plan || '—' }}</dd></div>
              <div>
                <dt class="text-muted">Sub status</dt>
                <dd>
                  <span
                    v-if="drawer.user.subscription_status"
                    class="text-[11px] px-2 py-0.5 rounded-full border capitalize"
                    :class="planClass(drawer.user.subscription_status)"
                  >
                    {{ drawer.user.subscription_status }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </dd>
              </div>
            </dl>
          </section>

          <!-- Usage metrics -->
          <section class="space-y-2">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-muted">Usage</h3>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
              <div class="rounded-xl border border-border-color/60 bg-card/60 p-3 text-center">
                <p class="text-xl font-bold text-primary">{{ drawer.user.total_screens_count ?? 0 }}</p>
                <p class="text-[11px] text-muted">Screens</p>
              </div>
              <div class="rounded-xl border border-border-color/60 bg-card/60 p-3 text-center">
                <p class="text-xl font-bold text-emerald-400">{{ drawer.user.active_screens_count ?? 0 }}</p>
                <p class="text-[11px] text-muted">Online</p>
              </div>
              <div class="rounded-xl border border-border-color/60 bg-card/60 p-3 text-center">
                <p class="text-xl font-bold text-primary">{{ drawer.user.total_templates_count ?? 0 }}</p>
                <p class="text-[11px] text-muted">Templates</p>
              </div>
              <div class="rounded-xl border border-border-color/60 bg-card/60 p-3 text-center">
                <p class="text-xl font-bold text-primary">{{ formatBytes(drawer.user.storage_used_bytes) }}</p>
                <p class="text-[11px] text-muted">Storage</p>
              </div>
            </div>
          </section>

          <!-- Lock info -->
          <section v-if="drawer.user.is_lock_active" class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 space-y-1">
            <p class="text-sm font-semibold text-amber-200">Account locked</p>
            <p class="text-xs text-amber-100/80">{{ drawer.user.admin_lock_reason || 'No reason provided' }}</p>
          </section>

          <!-- Actions -->
          <section class="space-y-2">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-muted">Actions</h3>
            <div class="flex flex-wrap gap-2">
              <button
                type="button"
                class="btn-outline px-4 py-2 rounded-lg text-sm"
                :class="drawer.user.is_lock_active ? 'text-emerald-400' : 'text-amber-400'"
                :disabled="actionBusyId === drawer.user.id"
                @click="toggleLock(drawer.user)"
              >
                {{ drawer.user.is_lock_active ? 'Unlock account' : 'Lock account' }}
              </button>
              <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="openPasswordModal(drawer.user)">
                Reset password
              </button>
              <button
                type="button"
                class="btn-primary px-4 py-2 rounded-lg text-sm"
                :disabled="actionBusyId === drawer.user.id"
                @click="revokeSessions(drawer.user)"
              >
                Revoke all sessions
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>

    <!-- Password modal -->
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
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="passwordModal.open = false">Cancel</button>
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
const search = ref('')
const filters = ref({ tenantId: '', role: '', status: '' })
const actionBusyId = ref(null)
const passwordModal = ref({ open: false, user: null, value: '' })
const passwordSubmitting = ref(false)
const drawer = ref({ open: false, user: null })
const tenantOptions = ref([])

const roleOptions = ['Developer', 'Manager', 'Employee', 'Visitor']

const kpis = computed(() => {
  const list = rows.value
  return {
    total: list.length,
    withTenant: list.filter(u => u.tenant_id).length,
    noTenant: list.filter(u => !u.tenant_id).length,
    locked: list.filter(u => u.is_lock_active).length,
    totalScreens: list.reduce((s, u) => s + (u.total_screens_count || 0), 0),
    totalStorage: list.reduce((s, u) => s + (u.storage_used_bytes || 0), 0),
  }
})

const filteredRows = computed(() => {
  let list = rows.value
  const q = search.value.trim().toLowerCase()
  if (q) {
    list = list.filter(u =>
      (u.username || '').toLowerCase().includes(q) ||
      (u.email || '').toLowerCase().includes(q) ||
      (u.full_name || '').toLowerCase().includes(q)
    )
  }
  if (filters.value.role) {
    list = list.filter(u => u.role === filters.value.role)
  }
  if (filters.value.status === 'active') list = list.filter(u => u.is_active && !u.is_lock_active)
  else if (filters.value.status === 'locked') list = list.filter(u => u.is_lock_active)
  else if (filters.value.status === 'inactive') list = list.filter(u => !u.is_active)
  return list
})

function statusLabel(row) {
  if (row.is_lock_active) return 'Locked'
  if (row.is_active === false) return 'Inactive'
  return 'Active'
}

function statusClass(row) {
  if (row.is_lock_active) return 'border-amber-500/50 text-amber-700 dark:text-amber-200 bg-amber-500/10'
  if (row.is_active === false) return 'border-slate-500/40 text-muted'
  return 'border-emerald-500/40 text-emerald-700 dark:text-emerald-200 bg-emerald-500/10'
}

function planClass(status) {
  if (status === 'active') return 'border-emerald-500/40 text-emerald-700 dark:text-emerald-200 bg-emerald-500/10'
  if (status === 'trialing') return 'border-cyan-500/40 text-cyan-700 dark:text-cyan-200 bg-cyan-500/10'
  if (status === 'past_due') return 'border-amber-500/40 text-amber-700 dark:text-amber-200 bg-amber-500/10'
  if (status === 'canceled') return 'border-rose-500/40 text-rose-700 dark:text-rose-200 bg-rose-500/10'
  return 'border-slate-500/40 text-muted'
}

function formatDate(iso) {
  if (!iso) return '—'
  try { return new Date(iso).toLocaleString() } catch { return iso }
}

function formatBytes(b) {
  if (!b || b === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.min(Math.floor(Math.log(b) / Math.log(1024)), units.length - 1)
  const val = b / Math.pow(1024, i)
  return `${val < 10 ? val.toFixed(1) : Math.round(val)} ${units[i]}`
}

function openDrawer(row) {
  drawer.value = { open: true, user: row }
}

async function fetchTenants() {
  try {
    const { data } = await platformAPI.tenants.list({ page_size: 500 })
    tenantOptions.value = (data.results || data || []).map(t => ({ id: String(t.id), name: t.name }))
  } catch { /* optional */ }
}

async function fetchAllUsers() {
  const acc = []
  let page = 1
  const params = { page_size: 100 }
  if (filters.value.tenantId === '__none__') {
    params.no_tenant = 'true'
  } else if (filters.value.tenantId) {
    params.tenant_id = filters.value.tenantId
  }
  for (;;) {
    const { data } = await api.get('/users/', { params: { ...params, page } })
    const chunk = data.results || data || []
    acc.push(...chunk)
    if (!data.next || !chunk.length) break
    page += 1
    if (page > 200) break
  }
  return acc
}

async function load() {
  loading.value = true
  loadError.value = null
  try {
    await fetchTenants()
    rows.value = await fetchAllUsers()
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
      await usersAPI.lock(row.id, { reason: 'Locked by Super Admin' })
    }
    const { data } = await usersAPI.detail(row.id)
    const idx = rows.value.findIndex(r => r.id === row.id)
    if (idx >= 0) rows.value[idx] = { ...rows.value[idx], ...data }
    if (drawer.value.user?.id === row.id) drawer.value.user = { ...drawer.value.user, ...data }
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
