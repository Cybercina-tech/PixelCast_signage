<template>
  <div class="space-y-6 max-w-4xl">
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <button
          type="button"
          class="btn-outline px-3 py-1.5 rounded-lg text-xs mb-3"
          @click="$router.push({ name: 'super-admin-users' })"
        >
          ← Global Users
        </button>
        <h1 class="text-2xl font-bold text-primary">{{ user?.username || 'User' }}</h1>
        <p class="text-sm text-muted mt-1">{{ user?.email }}</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          v-if="user?.tenant_id"
          type="button"
          class="btn-outline px-4 py-2 rounded-lg text-sm"
          @click="goTenant"
        >
          Open customer
        </button>
        <button
          type="button"
          class="btn-outline px-4 py-2 rounded-lg text-sm"
          @click="goNewTicket"
        >
          New ticket for user
        </button>
      </div>
    </div>

    <div
      v-if="loadError"
      class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ loadError }}
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="card-base rounded-2xl p-6 animate-pulse h-32" />
    </div>

    <template v-else-if="user">
      <!-- Profile -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-muted mb-4">Profile & access</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="label-base block text-sm mb-1">Username</label>
            <input v-model="form.username" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Email</label>
            <input v-model="form.email" type="email" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Full name</label>
            <input v-model="form.full_name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Phone</label>
            <input v-model="form.phone_number" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div class="sm:col-span-2">
            <label class="label-base block text-sm mb-1">Organization</label>
            <input v-model="form.organization_name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div class="flex items-center gap-2 sm:col-span-2">
            <input id="ua" v-model="form.is_active" type="checkbox" class="rounded border-border-color" />
            <label for="ua" class="text-sm text-primary">Account active</label>
          </div>
        </div>
        <div class="mt-4 flex justify-end">
          <button
            type="button"
            class="btn-primary px-4 py-2 rounded-lg text-sm"
            :disabled="savingProfile"
            @click="saveProfile"
          >
            {{ savingProfile ? 'Saving…' : 'Save profile' }}
          </button>
        </div>
      </Card>

      <!-- Role -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-muted mb-4">Role</h2>
        <div class="flex flex-wrap items-end gap-3">
          <div class="min-w-[200px]">
            <label class="label-base block text-sm mb-1">Product role</label>
            <select v-model="roleDraft" class="select-base w-full px-3 py-2 rounded-lg">
              <option v-for="r in roleOptions" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <button
            type="button"
            class="btn-primary px-4 py-2 rounded-lg text-sm"
            :disabled="savingRole || roleDraft === user.role"
            @click="saveRole"
          >
            {{ savingRole ? 'Updating…' : 'Update role' }}
          </button>
        </div>
        <p class="text-xs text-muted mt-2">Changing role updates staff/superuser flags server-side.</p>
      </Card>

      <!-- Tenant -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-muted mb-4">Tenant (customer)</h2>
        <div class="flex flex-wrap items-end gap-3">
          <div class="min-w-[240px] flex-1">
            <label class="label-base block text-sm mb-1">Linked tenant</label>
            <select v-model="tenantDraft" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">No tenant</option>
              <option v-for="t in tenantOptions" :key="t.id" :value="t.id">{{ t.name }}</option>
            </select>
          </div>
          <button
            type="button"
            class="btn-primary px-4 py-2 rounded-lg text-sm"
            :disabled="savingTenant || tenantDraft === (user.tenant_id || '')"
            @click="saveTenant"
          >
            {{ savingTenant ? 'Saving…' : 'Update tenant' }}
          </button>
        </div>
        <p v-if="user.tenant_restriction" class="text-xs text-amber-300 mt-2">
          Tenant restriction: {{ user.tenant_restriction.kind }} — {{ user.tenant_restriction.reason || '—' }}
        </p>
      </Card>

      <!-- Usage -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-muted mb-4">Usage</h2>
        <dl class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
          <div class="rounded-xl border border-border-color/60 bg-card/60 p-3">
            <dt class="text-muted text-xs">Screens</dt>
            <dd class="font-semibold text-primary">{{ user.total_screens_count ?? 0 }} ({{ user.active_screens_count ?? 0 }} online)</dd>
          </div>
          <div class="rounded-xl border border-border-color/60 bg-card/60 p-3">
            <dt class="text-muted text-xs">Templates</dt>
            <dd class="font-semibold text-primary">{{ user.total_templates_count ?? 0 }}</dd>
          </div>
          <div class="rounded-xl border border-border-color/60 bg-card/60 p-3">
            <dt class="text-muted text-xs">Storage</dt>
            <dd class="font-semibold text-primary">{{ formatBytes(user.storage_used_bytes) }}</dd>
          </div>
          <div class="rounded-xl border border-border-color/60 bg-card/60 p-3">
            <dt class="text-muted text-xs">Plan</dt>
            <dd class="font-semibold text-primary">{{ user.subscription_plan || '—' }}</dd>
          </div>
        </dl>
        <p class="text-xs text-muted mt-2">Last seen: {{ formatDate(user.last_seen) }} · Joined: {{ formatDate(user.date_joined) }}</p>
      </Card>

      <!-- Security -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-muted mb-4">Security</h2>
        <div v-if="user.is_lock_active" class="rounded-xl border border-amber-500/30 bg-amber-500/10 p-3 mb-4 text-sm">
          <p class="font-semibold text-amber-200">Account locked</p>
          <p class="text-xs text-amber-100/80 mt-1">{{ user.admin_lock_reason || 'No reason provided' }}</p>
        </div>
        <div class="flex flex-wrap gap-2 mb-6">
          <button
            type="button"
            class="btn-outline px-4 py-2 rounded-lg text-sm"
            :class="user.is_lock_active ? 'text-emerald-400' : 'text-amber-400'"
            :disabled="actionBusy"
            @click="toggleLock"
          >
            {{ user.is_lock_active ? 'Unlock account' : 'Lock account' }}
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="actionBusy" @click="revokeSessions">
            Revoke all sessions
          </button>
          <button
            type="button"
            class="btn-primary px-4 py-2 rounded-lg text-sm"
            :disabled="impersonating || !canImpersonate"
            :title="!canImpersonate ? 'Cannot impersonate another Developer account' : ''"
            @click="startImpersonation"
          >
            {{ impersonating ? 'Starting…' : 'View as this user' }}
          </button>
        </div>
        <div class="border-t border-border-color/60 pt-4 space-y-3">
          <p class="text-sm text-muted">Set a new password (invalidates refresh tokens).</p>
          <div class="flex flex-wrap gap-2 max-w-md">
            <input
              v-model="newPassword"
              type="password"
              class="input-base flex-1 min-w-[180px] px-3 py-2 rounded-lg"
              placeholder="New password"
              autocomplete="new-password"
            />
            <button
              type="button"
              class="btn-primary px-4 py-2 rounded-lg text-sm"
              :disabled="passwordBusy || !newPassword"
              @click="submitPassword"
            >
              {{ passwordBusy ? 'Saving…' : 'Set password' }}
            </button>
          </div>
        </div>
      </Card>

      <!-- Danger -->
      <Card>
        <h2 class="text-sm font-semibold uppercase tracking-wider text-rose-400 mb-2">Danger zone</h2>
        <p class="text-xs text-muted mb-3">Permanently delete this user. You cannot delete your own account.</p>
        <button
          type="button"
          class="btn-outline border-rose-500/40 text-rose-300 px-4 py-2 rounded-lg text-sm"
          :disabled="deleting || isSelf"
          @click="confirmDelete"
        >
          {{ deleting ? 'Deleting…' : 'Delete user' }}
        </button>
      </Card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Card from '@/components/common/Card.vue'
import { platformAPI, usersAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { normalizeApiError } from '@/utils/apiError'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const loadError = ref(null)
const user = ref(null)
const tenantOptions = ref([])

const form = ref({
  username: '',
  email: '',
  full_name: '',
  phone_number: '',
  organization_name: '',
  is_active: true,
})
const roleDraft = ref('Employee')
const tenantDraft = ref('')
const roleOptions = ['Developer', 'Manager', 'Employee', 'Visitor']

const savingProfile = ref(false)
const savingRole = ref(false)
const savingTenant = ref(false)
const actionBusy = ref(false)
const newPassword = ref('')
const passwordBusy = ref(false)
const impersonating = ref(false)
const deleting = ref(false)

const userId = computed(() => route.params.id)
const currentUserId = computed(() => authStore.user?.id && String(authStore.user.id))
const isSelf = computed(() => currentUserId.value && String(user.value?.id) === currentUserId.value)
const canImpersonate = computed(() => {
  if (!user.value) return false
  if (isSelf.value) return false
  if (user.value.role === 'Developer') return false
  return true
})

function formatDate(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function formatBytes(b) {
  if (!b || b === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.min(Math.floor(Math.log(b) / Math.log(1024)), units.length - 1)
  const val = b / Math.pow(1024, i)
  return `${val < 10 ? val.toFixed(1) : Math.round(val)} ${units[i]}`
}

function applyUserToForm(u) {
  user.value = u
  form.value = {
    username: u.username || '',
    email: u.email || '',
    full_name: u.full_name || '',
    phone_number: u.phone_number || '',
    organization_name: u.organization_name || '',
    is_active: u.is_active !== false,
  }
  roleDraft.value = u.role || 'Employee'
  tenantDraft.value = u.tenant_id ? String(u.tenant_id) : ''
}

async function loadTenants() {
  try {
    const { data } = await platformAPI.tenants.list({ page_size: 500 })
    tenantOptions.value = (data.results || data || []).map((t) => ({ id: String(t.id), name: t.name }))
  } catch {
    tenantOptions.value = []
  }
}

async function load() {
  loading.value = true
  loadError.value = null
  try {
    await loadTenants()
    const { data } = await usersAPI.detail(userId.value)
    applyUserToForm(data)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load user'
    user.value = null
  } finally {
    loading.value = false
  }
}

async function saveProfile() {
  savingProfile.value = true
  try {
    const { data } = await usersAPI.patch(userId.value, {
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name,
      phone_number: form.value.phone_number || '',
      organization_name: form.value.organization_name || '',
      is_active: form.value.is_active,
    })
    applyUserToForm(data)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    savingProfile.value = false
  }
}

async function saveRole() {
  savingRole.value = true
  try {
    await usersAPI.changeRole(userId.value, { role: roleDraft.value })
    const { data } = await usersAPI.detail(userId.value)
    applyUserToForm(data)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Role update failed'
  } finally {
    savingRole.value = false
  }
}

async function saveTenant() {
  savingTenant.value = true
  try {
    const payload = { tenant_id: tenantDraft.value || null }
    const { data } = await usersAPI.setTenant(userId.value, payload)
    applyUserToForm(data)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Tenant update failed'
  } finally {
    savingTenant.value = false
  }
}

async function toggleLock() {
  actionBusy.value = true
  try {
    if (user.value.is_lock_active) {
      await usersAPI.unlock(userId.value)
    } else {
      await usersAPI.lock(userId.value, { reason: 'Locked from Global User manage' })
    }
    const { data } = await usersAPI.detail(userId.value)
    applyUserToForm(data)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Lock action failed'
  } finally {
    actionBusy.value = false
  }
}

async function revokeSessions() {
  actionBusy.value = true
  try {
    await usersAPI.revokeSessions(userId.value)
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not revoke sessions'
  } finally {
    actionBusy.value = false
  }
}

async function submitPassword() {
  if (!newPassword.value) return
  passwordBusy.value = true
  try {
    await usersAPI.adminSetPassword(userId.value, { new_password: newPassword.value })
    newPassword.value = ''
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Password reset failed'
  } finally {
    passwordBusy.value = false
  }
}

async function startImpersonation() {
  if (!canImpersonate.value) return
  impersonating.value = true
  try {
    await authStore.startPlatformImpersonation(userId.value)
    await router.push({ name: 'dashboard' })
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Impersonation failed'
  } finally {
    impersonating.value = false
  }
}

function goTenant() {
  if (!user.value?.tenant_id) return
  router.push({ name: 'super-admin-customer-detail', params: { id: user.value.tenant_id } })
}

function goNewTicket() {
  const q = { new: '1', requester_id: String(userId.value) }
  if (user.value?.tenant_id) q.tenant_id = String(user.value.tenant_id)
  router.push({ name: 'super-admin-tickets', query: q })
}

function confirmDelete() {
  if (isSelf.value) return
  if (!window.confirm('Delete this user permanently? This cannot be undone.')) return
  deleteUser()
}

async function deleteUser() {
  deleting.value = true
  try {
    await usersAPI.delete(userId.value)
    await router.push({ name: 'super-admin-users' })
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Delete failed'
  } finally {
    deleting.value = false
  }
}

watch(
  () => route.params.id,
  () => {
    load()
  }
)

onMounted(load)
</script>
