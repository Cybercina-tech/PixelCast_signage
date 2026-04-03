<template>
  <component :is="embedded ? 'div' : AppLayout">
    <div class="space-y-6">
      <div v-if="!embedded" class="flex flex-wrap justify-between items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold text-primary">Customers</h1>
          <p class="text-sm text-muted mt-1">Tenant accounts, billing signals, and engagement</p>
        </div>
        <div class="flex gap-2 flex-wrap">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" @click="openCreateModal">
            Add tenant
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="load" :disabled="loading">
            Refresh
          </button>
        </div>
      </div>
      <div v-else class="flex justify-end gap-2 flex-wrap">
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" @click="openCreateModal">
          Add tenant
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="load" :disabled="loading">
          Refresh
        </button>
      </div>

      <Card>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
          <div>
            <label class="label-base block text-sm mb-1">Search</label>
            <input
              v-model="filters.search"
              type="text"
              class="input-base w-full px-3 py-2 rounded-lg"
              placeholder="Name, slug…"
              @keyup.enter="load"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Subscription status</label>
            <select v-model="filters.status" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
              <option value="">All</option>
              <option value="active">Active</option>
              <option value="trialing">Trialing</option>
              <option value="past_due">Past due</option>
              <option value="canceled">Canceled</option>
              <option value="none">None</option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Alert</label>
            <select v-model="filters.alert" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
              <option value="">Any</option>
              <option value="payment_failed">Payment failed</option>
            </select>
          </div>
        </div>

        <div v-if="loading" class="text-center py-8 text-muted">Loading…</div>
        <div v-else-if="error" class="text-center py-8 text-red-600">{{ error }}</div>
        <div v-else class="space-y-4">
          <div class="grid gap-3 lg:hidden">
            <article
              v-for="row in rows"
              :key="`card-${row.id}`"
              class="rounded-xl border border-border-color/70 bg-card/50 p-4"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="min-w-0">
                  <h3 class="font-semibold text-primary truncate">{{ row.name }}</h3>
                  <p class="text-xs text-muted truncate">{{ row.plan_name || 'No plan' }} {{ row.plan_interval ? `(${row.plan_interval})` : '' }}</p>
                </div>
                <span class="text-[11px] px-2 py-1 rounded-full border capitalize" :class="statusClass(row.subscription_status)">
                  {{ row.subscription_status }}
                </span>
                <span
                  v-if="row.access_locked"
                  class="text-[11px] px-2 py-1 rounded-full border border-rose-500/40 bg-rose-500/10 text-rose-300"
                >
                  Locked
                </span>
              </div>
              <div class="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div class="rounded-lg bg-slate-800/30 px-2 py-1">
                  <p class="text-muted">Health</p>
                  <p class="font-semibold">{{ row.health?.score != null ? row.health.score : '—' }}</p>
                </div>
                <div class="rounded-lg bg-slate-800/30 px-2 py-1">
                  <p class="text-muted">Screens</p>
                  <p class="font-semibold">{{ row.engagement?.screen_count ?? '—' }}</p>
                </div>
              </div>
              <div class="mt-3 flex items-center justify-between text-xs">
                <span class="text-muted capitalize">Risk: {{ row.churn?.churn_risk_level || '—' }}</span>
                <div class="flex items-center gap-3">
                  <button
                    type="button"
                    :class="actionBtnClass(row.access_locked ? 'unlock' : 'lock')"
                    @click="toggleTenantLock(row)"
                  >
                    {{ row.access_locked ? 'Unlock' : 'Lock' }}
                  </button>
                  <button type="button" :class="actionBtnClass('edit')" @click="openEditModal(row)">
                    Edit
                  </button>
                  <button type="button" :class="actionBtnClass('delete')" @click="removeTenant(row)">
                    Delete
                  </button>
                  <router-link :to="`/super-admin/customers/${row.id}`" :class="actionBtnClass('open')">
                    Open
                  </router-link>
                </div>
              </div>
            </article>
          </div>

          <div class="hidden lg:block overflow-x-auto">
            <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-border-color text-left text-muted">
                <th class="py-2 pr-4">Customer</th>
                <th class="py-2 pr-4">Status</th>
                <th class="py-2 pr-4">Plan</th>
                <th class="py-2 pr-4">Alerts</th>
                <th class="py-2 pr-4">Health</th>
                <th class="py-2 pr-4">Churn</th>
                <th class="py-2 pr-4">Screens</th>
                <th class="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in rows" :key="row.id" class="border-b border-border-color/60 hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                <td class="py-2 pr-4 font-medium text-primary">{{ row.name }}</td>
                <td class="py-2 pr-4 capitalize">{{ row.subscription_status }}</td>
                <td class="py-2 pr-4">{{ row.plan_name || '—' }} {{ row.plan_interval ? `(${row.plan_interval})` : '' }}</td>
                <td class="py-2 pr-4">
                  <span
                    v-for="a in row.billing_alerts || []"
                    :key="a"
                    class="inline-block mr-1 mb-1 px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100"
                  >
                    {{ a }}
                  </span>
                  <span v-if="!(row.billing_alerts || []).length" class="text-muted">—</span>
                </td>
                <td class="py-2 pr-4">
                  <span
                    class="inline-flex items-center justify-center min-w-[2.5rem] px-2 py-0.5 rounded-lg text-xs font-semibold"
                    :class="healthClass(row.health?.score)"
                  >
                    {{ row.health?.score != null ? row.health.score : '—' }}
                  </span>
                </td>
                <td class="py-2 pr-4">
                  <span class="capitalize">{{ row.churn?.churn_risk_level || '—' }}</span>
                </td>
                <td class="py-2 pr-4">{{ row.engagement?.screen_count ?? '—' }}</td>
                <td class="py-2 text-right">
                  <button
                    type="button"
                    :class="`${actionBtnClass(row.access_locked ? 'unlock' : 'lock')} mr-2`"
                    @click="toggleTenantLock(row)"
                  >
                    {{ row.access_locked ? 'Unlock' : 'Lock' }}
                  </button>
                  <button
                    type="button"
                    :class="`${actionBtnClass('edit')} mr-2`"
                    @click="openEditModal(row)"
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    :class="`${actionBtnClass('delete')} mr-2`"
                    @click="removeTenant(row)"
                  >
                    Delete
                  </button>
                  <router-link :to="`/super-admin/customers/${row.id}`" :class="actionBtnClass('open')">
                    Open
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
          </div>
        </div>
      </Card>
    </div>

    <div
      v-if="showModal"
      class="fixed inset-0 z-50 bg-black/55 backdrop-blur-sm p-4 flex items-center justify-center"
      @click.self="closeModal"
    >
      <div class="w-full max-w-2xl rounded-2xl border border-border-color bg-card p-5 space-y-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-primary">
              {{ editingTenant ? 'Edit tenant' : 'Create tenant' }}
            </h2>
            <p class="text-xs text-muted mt-1">
              Manage tenant identity, plan, and subscription status.
            </p>
          </div>
          <button type="button" class="btn-outline px-3 py-1 text-xs rounded-lg" @click="closeModal">Close</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label class="label-base block text-sm mb-1">Name *</label>
            <input v-model="form.name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Slug</label>
            <input v-model="form.slug" type="text" class="input-base w-full px-3 py-2 rounded-lg" placeholder="auto-from-name" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Organization key</label>
            <input v-model="form.organization_name_key" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Subscription status</label>
            <select v-model="form.subscription_status" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="none">none</option>
              <option value="trialing">trialing</option>
              <option value="active">active</option>
              <option value="past_due">past_due</option>
              <option value="canceled">canceled</option>
              <option value="unpaid">unpaid</option>
              <option value="incomplete">incomplete</option>
              <option value="incomplete_expired">incomplete_expired</option>
              <option value="paused">paused</option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Plan name</label>
            <input v-model="form.plan_name" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Plan interval</label>
            <input v-model="form.plan_interval" type="text" class="input-base w-full px-3 py-2 rounded-lg" placeholder="month / year" />
          </div>
          <div class="md:col-span-2">
            <label class="label-base block text-sm mb-1">Device limit</label>
            <input v-model.number="form.device_limit" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" placeholder="leave empty for unlimited" />
          </div>
        </div>

        <div class="flex items-center justify-end gap-2">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="closeModal">Cancel</button>
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="saving" @click="submitTenant">
            {{ saving ? 'Saving...' : (editingTenant ? 'Save changes' : 'Create tenant') }}
          </button>
        </div>
      </div>
    </div>
  </component>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'

defineProps({
  /** When true, render without main app chrome (used inside Super Admin shell). */
  embedded: { type: Boolean, default: false },
})

function healthClass(score) {
  if (score == null) return 'bg-slate-700/40 text-muted'
  if (score >= 71) return 'bg-emerald-500/20 text-emerald-700 dark:text-emerald-300'
  if (score >= 41) return 'bg-amber-500/20 text-amber-800 dark:text-amber-200'
  return 'bg-red-500/20 text-red-800 dark:text-red-200'
}

function statusClass(status) {
  if (status === 'active') return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300'
  if (status === 'trialing') return 'border-cyan-500/30 bg-cyan-500/10 text-cyan-300'
  if (status === 'past_due') return 'border-amber-500/30 bg-amber-500/10 text-amber-300'
  if (status === 'canceled') return 'border-red-500/30 bg-red-500/10 text-red-300'
  return 'border-border-color/70 bg-card text-muted'
}

function actionBtnClass(kind) {
  const base =
    'inline-flex items-center justify-center rounded-lg border px-2.5 py-1 text-xs font-medium transition-colors'
  if (kind === 'edit') return `${base} border-cyan-500/40 bg-cyan-500/10 text-cyan-300 hover:bg-cyan-500/20`
  if (kind === 'open') return `${base} border-indigo-500/40 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20`
  if (kind === 'delete') return `${base} border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20`
  if (kind === 'unlock') return `${base} border-emerald-500/40 bg-emerald-500/10 text-emerald-300 hover:bg-emerald-500/20`
  if (kind === 'lock') return `${base} border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20`
  return `${base} border-border-color/70 text-muted hover:bg-card`
}

const loading = ref(false)
const error = ref(null)
const rows = ref([])
const filters = ref({ search: '', status: '', alert: '' })
const notify = useNotification()
const showModal = ref(false)
const saving = ref(false)
const editingTenant = ref(null)
const form = ref({
  name: '',
  slug: '',
  organization_name_key: '',
  subscription_status: 'none',
  plan_name: '',
  plan_interval: '',
  device_limit: null,
})

function resetForm() {
  form.value = {
    name: '',
    slug: '',
    organization_name_key: '',
    subscription_status: 'none',
    plan_name: '',
    plan_interval: '',
    device_limit: null,
  }
}

function openCreateModal() {
  editingTenant.value = null
  resetForm()
  showModal.value = true
}

function openEditModal(row) {
  editingTenant.value = row
  form.value = {
    name: row.name || '',
    slug: row.slug || '',
    organization_name_key: row.organization_name_key || '',
    subscription_status: row.subscription_status || 'none',
    plan_name: row.plan_name || '',
    plan_interval: row.plan_interval || '',
    device_limit: row.device_limit ?? null,
  }
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  editingTenant.value = null
}

async function submitTenant() {
  if (!form.value.name?.trim()) {
    notify.error('Tenant name is required.')
    return
  }
  saving.value = true
  try {
    const payload = {
      name: form.value.name,
      slug: form.value.slug || undefined,
      organization_name_key: form.value.organization_name_key || '',
      subscription_status: form.value.subscription_status || 'none',
      plan_name: form.value.plan_name || '',
      plan_interval: form.value.plan_interval || '',
      device_limit:
        form.value.device_limit === '' || form.value.device_limit == null
          ? null
          : Number(form.value.device_limit),
    }
    if (editingTenant.value?.id) {
      await platformAPI.tenants.update(editingTenant.value.id, payload)
      notify.success('Tenant updated.')
    } else {
      await platformAPI.tenants.create(payload)
      notify.success('Tenant created.')
    }
    closeModal()
    await load()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function removeTenant(row) {
  const ok = window.confirm(
    `Delete tenant "${row.name}"?\n\nThis removes tenant invoices, API keys, webhooks, and tenant audit logs.`
  )
  if (!ok) return
  try {
    await platformAPI.tenants.remove(row.id)
    notify.success('Tenant deleted.')
    await load()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Delete failed')
  }
}

async function toggleTenantLock(row) {
  try {
    if (row.access_locked) {
      await platformAPI.tenants.accessUnlock(row.id)
      notify.success('Tenant unlocked.')
    } else {
      const reason = window.prompt('Lock reason (optional):', '') || ''
      await platformAPI.tenants.accessLock(row.id, { reason: reason.trim() })
      notify.success('Tenant locked.')
    }
    await load()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Tenant lock update failed')
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.alert) params.alert = filters.value.alert
    const { data } = await platformAPI.tenants.list(params)
    rows.value = data.results ?? data
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Failed to load tenants'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
