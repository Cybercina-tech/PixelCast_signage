<template>
  <component :is="embedded ? 'div' : AppLayout">
    <div class="space-y-6" v-if="tenant">
      <section class="rounded-2xl border border-border-color/70 bg-card/60 p-4 md:p-5">
        <div class="flex flex-wrap justify-between items-start gap-4">
        <div>
          <button type="button" class="btn-outline px-3 py-1 rounded-lg text-sm mb-2" @click="$router.push('/super-admin/customers')">
            ← Customers
          </button>
          <h1 v-if="!embedded" class="text-2xl font-bold text-primary">{{ tenant.name }}</h1>
          <p v-if="!embedded" class="text-sm text-muted">{{ tenant.slug }} · {{ tenant.subscription_status }}</p>
          <p v-else class="text-sm text-muted">{{ tenant.slug }} · {{ tenant.subscription_status }}</p>
          <p v-if="tenant.access_locked" class="text-xs text-rose-300 mt-1">
            Access locked {{ tenant.access_lock_reason ? `- ${tenant.access_lock_reason}` : '' }}
          </p>
        </div>
        <div class="flex gap-2 flex-wrap">
          <button
            type="button"
            class="btn-outline px-4 py-2 rounded-lg text-sm"
            :class="tenant.access_locked ? 'text-emerald-300' : 'text-rose-300'"
            @click="toggleTenantLock"
          >
            {{ tenant.access_locked ? 'Unlock access' : 'Lock access' }}
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="busy" @click="syncStripe">
            Sync Stripe
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="load">Refresh</button>
        </div>
        </div>
      </section>

      <nav class="flex flex-wrap gap-2 border-b border-border-color/60 pb-3" aria-label="Tenant sections">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          type="button"
          class="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
          :class="
            activeTab === tab.id
              ? 'bg-cyan-500/15 text-cyan-700 dark:text-cyan-300 border border-cyan-500/30'
              : 'text-muted hover:bg-slate-100 dark:hover:bg-slate-800/80 border border-transparent'
          "
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>

      <template v-if="activeTab === 'license'">
        <Card title="SaaS tenant license">
          <div v-if="licenseLoading" class="text-sm text-muted py-4">Loading…</div>
          <form v-else-if="licenseState" class="grid gap-3 max-w-lg" @submit.prevent="saveLicense">
            <div>
              <label class="label-base block text-sm mb-1">License key</label>
              <input v-model="licenseForm.license_key" type="text" class="input-base w-full px-3 py-2 rounded-lg font-mono text-sm" />
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Status</label>
              <select v-model="licenseForm.license_status" class="select-base w-full px-3 py-2 rounded-lg">
                <option value="inactive">inactive</option>
                <option value="active">active</option>
                <option value="invalid">invalid</option>
                <option value="grace">grace</option>
              </select>
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Offline grace (hours)</label>
              <input v-model.number="licenseForm.offline_grace_hours" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
            <p class="text-xs text-muted">Entitled: {{ licenseState.is_entitled ? 'Yes' : 'No' }}</p>
            <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm w-fit" :disabled="licenseSaving">
              {{ licenseSaving ? 'Saving…' : 'Save license' }}
            </button>
          </form>
        </Card>
        <Card title="Enforcement logs">
          <div v-if="enforcementLoading" class="text-sm text-muted py-4">Loading…</div>
          <div v-else class="overflow-x-auto max-h-64">
            <table v-if="enforcementLogs.length" class="min-w-full text-xs">
              <thead>
                <tr class="text-left text-muted border-b border-border-color">
                  <th class="py-2 pr-2">Time</th>
                  <th class="py-2 pr-2">Action</th>
                  <th class="py-2 pr-2">Decision</th>
                  <th class="py-2">Details</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in enforcementLogs" :key="log.id" class="border-b border-border-color/30">
                  <td class="py-1.5 pr-2 whitespace-nowrap">{{ fmt(log.created_at) }}</td>
                  <td class="py-1.5 pr-2">{{ log.action }}</td>
                  <td class="py-1.5 pr-2">{{ log.decision }}</td>
                  <td class="py-1.5 text-muted break-all">{{ JSON.stringify(log.details || {}) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-else class="text-sm text-muted">No enforcement logs.</p>
          </div>
        </Card>
      </template>

      <template v-else-if="activeTab === 'integrations'">
        <Card title="API keys">
          <div class="flex flex-wrap gap-2 mb-3">
            <input v-model="newKeyLabel" type="text" placeholder="Label (optional)" class="input-base px-3 py-2 rounded-lg text-sm flex-1 min-w-[12rem]" />
            <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="keysBusy" @click="createApiKey">
              Create key
            </button>
          </div>
          <p v-if="newKeySecret" class="text-xs font-mono p-3 rounded-lg bg-amber-500/10 border border-amber-500/40 mb-3 break-all">
            Secret (copy now): {{ newKeySecret }}
          </p>
          <ul v-if="apiKeys.length" class="divide-y divide-border-color/60 text-sm">
            <li v-for="k in apiKeys" :key="k.id" class="py-2 flex justify-between gap-2 items-center">
              <span>{{ k.label || k.prefix }} <span class="text-muted font-mono text-xs">{{ k.prefix }}…</span></span>
              <button type="button" class="btn-outline px-2 py-1 rounded text-xs text-rose-400" @click="revokeKey(k.id)">Revoke</button>
            </li>
          </ul>
          <p v-else class="text-sm text-muted">No active API keys.</p>
        </Card>
        <Card title="Outbound webhooks">
          <form class="flex flex-wrap gap-2 mb-3" @submit.prevent="createWebhook">
            <input v-model="newWebhookUrl" type="url" required placeholder="https://…" class="input-base px-3 py-2 rounded-lg text-sm flex-1 min-w-[14rem]" />
            <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="webhooksBusy">Add webhook</button>
          </form>
          <p v-if="newWebhookSecret" class="text-xs font-mono p-3 rounded-lg bg-amber-500/10 border border-amber-500/40 mb-3 break-all">
            Signing secret (copy now): {{ newWebhookSecret }}
          </p>
          <ul v-if="webhooks.length" class="divide-y divide-border-color/60 text-sm">
            <li v-for="w in webhooks" :key="w.id" class="py-2 flex flex-wrap justify-between gap-2 items-center">
              <span class="font-mono text-xs break-all">{{ w.url }}</span>
              <div class="flex items-center gap-2 shrink-0">
                <label class="flex items-center gap-1 text-xs">
                  <input type="checkbox" :checked="w.is_active" @change="toggleWebhook(w, $event.target.checked)" />
                  Active
                </label>
                <button type="button" class="btn-outline px-2 py-1 rounded text-xs text-rose-400" @click="removeWebhook(w.id)">Delete</button>
              </div>
            </li>
          </ul>
          <p v-else class="text-sm text-muted">No webhooks configured.</p>
        </Card>
      </template>

      <template v-else>
      <Card v-if="tenant.health" title="Tenant health">
        <div class="flex flex-wrap items-end gap-4">
          <div>
            <p class="text-4xl font-bold text-primary">{{ tenant.health.score }}</p>
            <p class="text-xs text-muted">Composite score (0–100)</p>
          </div>
          <dl class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs flex-1">
            <div v-for="(v, k) in tenant.health.components || {}" :key="k" class="rounded-lg bg-slate-800/30 px-2 py-1">
              <dt class="text-muted capitalize">{{ String(k).replaceAll('_', ' ') }}</dt>
              <dd class="font-mono text-primary">{{ v }}</dd>
            </div>
          </dl>
        </div>
      </Card>

      <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <Card title="Users">
          <p class="text-3xl font-bold text-primary">{{ tenant.engagement?.user_count ?? 0 }}</p>
          <p class="text-xs text-muted mt-1">Active accounts in this tenant</p>
        </Card>
        <Card title="Connected users">
          <p class="text-3xl font-bold text-primary">{{ tenant.session_metrics?.active_user_count ?? 0 }}</p>
          <p class="text-xs text-muted mt-1">Users with at least one active session</p>
        </Card>
        <Card title="Active sessions">
          <p class="text-3xl font-bold text-primary">{{ tenant.session_metrics?.active_session_count ?? 0 }}</p>
          <p class="text-xs text-muted mt-1">Unexpired and non-revoked login sessions</p>
        </Card>
        <Card title="Screens">
          <p class="text-3xl font-bold text-primary">{{ tenant.engagement?.screen_count ?? 0 }}</p>
          <p class="text-xs text-muted mt-1">Registered display endpoints</p>
        </Card>
        <Card title="Offline screens">
          <p class="text-3xl font-bold text-primary">{{ tenant.engagement?.offline_screen_count ?? 0 }}</p>
          <p class="text-xs text-muted mt-1">Need operational follow-up</p>
        </Card>
        <Card title="Device utilization">
          <p class="text-3xl font-bold text-primary">{{ deviceUtilization }}</p>
          <p class="text-xs text-muted mt-1">
            {{ tenant.device_limit == null ? 'Unlimited plan (no cap)' : `Limit ${tenant.device_limit}` }}
          </p>
        </Card>
      </div>

      <div class="grid gap-4 xl:grid-cols-2">
        <Card title="Subscription">
          <dl class="grid grid-cols-1 gap-2 text-sm">
            <div><span class="text-muted">Plan</span> — {{ tenant.plan_name || '—' }} {{ tenant.plan_interval || '' }}</div>
            <div><span class="text-muted">Tenant ID</span> — <span class="font-mono text-xs">{{ tenant.id }}</span></div>
            <div><span class="text-muted">Period end</span> — {{ fmt(tenant.current_period_end) }}</div>
            <div><span class="text-muted">Period left</span> — {{ tenant.billing_days_remaining ?? '—' }} days</div>
            <div><span class="text-muted">Trial end</span> — {{ fmt(tenant.trial_end) }}</div>
            <div><span class="text-muted">Trial left</span> — {{ tenant.trial_days_remaining ?? '—' }} days</div>
            <div><span class="text-muted">Device limit</span> — {{ tenant.device_limit ?? '∞' }}</div>
            <div><span class="text-muted">Payment failures</span> — {{ tenant.payment_failed_count ?? 0 }}</div>
            <div><span class="text-muted">Billing grace until</span> — {{ fmt(tenant.billing_grace_until) }}</div>
            <div><span class="text-muted">Manual access until</span> — {{ fmt(tenant.manual_access_until) }}</div>
            <div><span class="text-muted">Tenant lock until</span> — {{ fmt(tenant.access_lock_until) }}</div>
            <div><span class="text-muted">Created</span> — {{ fmt(tenant.created_at) }}</div>
            <div><span class="text-muted">Updated</span> — {{ fmt(tenant.updated_at) }}</div>
          </dl>
        </Card>
        <Card title="Churn & usage">
          <dl class="grid grid-cols-1 gap-2 text-sm">
            <div><span class="text-muted">Risk</span> — {{ tenant.churn?.churn_risk_level }}</div>
            <div><span class="text-muted">Flags</span> — {{ (tenant.churn?.flags || []).join(', ') || '—' }}</div>
            <div><span class="text-muted">Users / screens / offline</span> — {{ tenant.engagement?.user_count }} / {{ tenant.engagement?.screen_count }} / {{ tenant.engagement?.offline_screen_count }}</div>
          </dl>
        </Card>
      </div>

      <Card title="Manual override">
        <form class="grid gap-3 max-w-lg" @submit.prevent="saveOverride">
          <div>
            <label class="label-base block text-sm mb-1">Manual access until (ISO datetime)</label>
            <input v-model="overrideForm.manual_access_until" type="datetime-local" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Device limit</label>
            <input v-model.number="overrideForm.device_limit" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Notes</label>
            <textarea v-model="overrideForm.notes" rows="2" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm w-fit" :disabled="busy">Save</button>
        </form>
      </Card>

      <Card title="Team (impersonate)">
        <div v-if="usersLoading" class="text-muted text-sm">Loading users…</div>
        <ul v-else class="divide-y divide-border-color/60">
          <li v-for="u in users" :key="u.id" class="py-2 flex flex-wrap justify-between gap-2 items-center">
            <span>{{ u.username }} <span class="text-muted">({{ u.role }})</span></span>
            <button
              type="button"
              class="btn-outline px-3 py-1 rounded-lg text-xs"
              :disabled="impBusy || u.role === 'Developer'"
              @click="impersonate(u.id)"
            >
              View as
            </button>
          </li>
        </ul>
      </Card>

      <Card title="Recent invoices">
        <div class="overflow-x-auto rounded-xl border border-border-color/50">
          <table class="min-w-full text-sm">
            <thead>
              <tr class="text-left text-muted border-b border-border-color">
                <th class="py-2 pr-2">ID</th>
                <th class="py-2 pr-2">Status</th>
                <th class="py-2 pr-2">Amount</th>
                <th class="py-2">Link</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="inv in tenant.invoices || []" :key="inv.stripe_invoice_id" class="border-b border-border-color/40">
                <td class="py-2 pr-2 font-mono text-xs">{{ inv.number || inv.stripe_invoice_id?.slice(0, 12) }}</td>
                <td class="py-2 pr-2">{{ inv.status }}</td>
                <td class="py-2 pr-2">{{ inv.amount_paid / 100 }} {{ inv.currency }}</td>
                <td class="py-2">
                  <a v-if="inv.hosted_invoice_url" :href="inv.hosted_invoice_url" target="_blank" rel="noopener" class="text-indigo-600 dark:text-indigo-400">Open</a>
                  <span v-else class="text-muted">—</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <Card title="Stripe webhook events">
        <ul class="text-sm space-y-1 font-mono">
          <li v-for="ev in tenant.recent_events || []" :key="ev.stripe_event_id" class="flex flex-wrap gap-2">
            <span>{{ ev.created_at }}</span>
            <span>{{ ev.event_type }}</span>
            <span :class="ev.processed_ok ? 'text-green-600' : 'text-red-600'">{{ ev.processed_ok ? 'ok' : 'fail' }}</span>
          </li>
        </ul>
      </Card>

      <Card title="Feature flags">
        <div v-if="flagsLoading" class="text-muted text-sm">Loading…</div>
        <div v-else>
          <div v-if="Object.keys(tenantFlags).length" class="space-y-2">
            <div v-for="(val, key) in tenantFlags" :key="key" class="flex items-center gap-3 text-sm">
              <span class="font-mono text-xs text-muted flex-1">{{ key }}</span>
              <span :class="val ? 'text-emerald-600' : 'text-red-600'" class="font-semibold">{{ val ? 'ON' : 'OFF' }}</span>
            </div>
          </div>
          <p v-else class="text-muted text-sm">No feature flags set for this tenant.</p>
          <router-link :to="`/super-admin/flags`" class="inline-block mt-3 text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
            Edit flags →
          </router-link>
        </div>
      </Card>

      <Card title="Tenant audit log">
        <div v-if="auditLoading" class="text-muted text-sm">Loading…</div>
        <div v-else class="overflow-x-auto max-h-80 rounded-xl border border-border-color/50">
          <table v-if="auditRows.length" class="min-w-full text-xs font-mono">
            <thead class="sticky top-0 bg-card">
              <tr class="text-left text-muted border-b border-border-color">
                <th class="py-2 pr-2">Time</th>
                <th class="py-2 pr-2">Actor</th>
                <th class="py-2 pr-2">Action</th>
                <th class="py-2">Details</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in auditRows" :key="row.id || row.created_at" class="border-b border-border-color/30">
                <td class="py-1.5 pr-2 whitespace-nowrap">{{ fmt(row.created_at) }}</td>
                <td class="py-1.5 pr-2">{{ row.actor_username || row.actor || '—' }}</td>
                <td class="py-1.5 pr-2 capitalize">{{ (row.action || '').replace(/_/g, ' ') }}</td>
                <td class="py-1.5 text-muted break-all">{{ JSON.stringify(row.details || {}).slice(0, 200) }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else class="text-muted text-sm">No audit log entries for this tenant.</p>
        </div>
      </Card>
      </template>
    </div>
    <div v-else-if="loadError" class="text-center py-12 text-red-600">{{ loadError }}</div>
    <div v-else class="text-center py-12 text-muted">Loading…</div>
  </component>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import { platformAPI, usersAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'

defineProps({
  embedded: { type: Boolean, default: false },
})

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notify = useNotification()

const tenant = ref(null)
const loadError = ref(null)
const busy = ref(false)
const impBusy = ref(false)
const users = ref([])
const usersLoading = ref(false)

const overrideForm = ref({
  manual_access_until: '',
  device_limit: null,
  notes: '',
})

const tenantFlags = ref({})
const flagsLoading = ref(false)
const auditRows = ref([])
const auditLoading = ref(false)

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'license', label: 'License' },
  { id: 'integrations', label: 'Integrations' },
]
const activeTab = ref('overview')

const licenseState = ref(null)
const licenseForm = ref({ license_key: '', license_status: 'inactive', offline_grace_hours: 72 })
const licenseLoading = ref(false)
const licenseSaving = ref(false)
const enforcementLogs = ref([])
const enforcementLoading = ref(false)

const apiKeys = ref([])
const webhooks = ref([])
const keysBusy = ref(false)
const webhooksBusy = ref(false)
const newKeyLabel = ref('')
const newKeySecret = ref('')
const newWebhookUrl = ref('')
const newWebhookSecret = ref('')

const deviceUtilization = computed(() => {
  const screens = Number(tenant.value?.engagement?.screen_count || 0)
  const limit = tenant.value?.device_limit
  if (limit == null || limit === 0) return '—'
  return `${Math.min(999, Math.round((screens / limit) * 100))}%`
})

function fmt(v) {
  if (!v) return '—'
  try {
    return new Date(v).toLocaleString()
  } catch {
    return String(v)
  }
}

async function load() {
  loadError.value = null
  try {
    const { data } = await platformAPI.tenants.retrieve(route.params.id)
    tenant.value = data
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Failed to load tenant'
  }
}

async function loadUsers() {
  usersLoading.value = true
  try {
    const { data } = await usersAPI.list({ tenant_id: route.params.id })
    users.value = data.results ?? data
  } catch {
    users.value = []
  } finally {
    usersLoading.value = false
  }
}

async function syncStripe() {
  busy.value = true
  try {
    const { data } = await platformAPI.tenants.syncStripe(route.params.id)
    tenant.value = data
    notify.success('Synced from Stripe')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Sync failed')
  } finally {
    busy.value = false
  }
}

async function saveOverride() {
  busy.value = true
  try {
    const payload = {}
    if (overrideForm.value.manual_access_until) {
      payload.manual_access_until = new Date(overrideForm.value.manual_access_until).toISOString()
    } else {
      payload.manual_access_until = null
    }
    if (overrideForm.value.device_limit !== null && overrideForm.value.device_limit !== '') {
      payload.device_limit = overrideForm.value.device_limit
    }
    if (overrideForm.value.notes) payload.notes = overrideForm.value.notes
    const { data } = await platformAPI.tenants.manualOverride(route.params.id, payload)
    tenant.value = data
    notify.success('Override saved')
    overrideForm.value.notes = ''
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Save failed')
  } finally {
    busy.value = false
  }
}

async function toggleTenantLock() {
  if (!tenant.value) return
  busy.value = true
  try {
    if (tenant.value.access_locked) {
      const { data } = await platformAPI.tenants.accessUnlock(route.params.id)
      tenant.value = data
      notify.success('Tenant access unlocked.')
    } else {
      const reason = window.prompt('Lock reason (optional):', '') || ''
      const { data } = await platformAPI.tenants.accessLock(route.params.id, { reason: reason.trim() })
      tenant.value = data
      notify.success('Tenant access locked.')
    }
    await Promise.all([loadUsers(), loadAuditLog()])
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Failed to update tenant lock')
  } finally {
    busy.value = false
  }
}

async function loadFlags() {
  flagsLoading.value = true
  try {
    const { data } = await platformAPI.tenantFeatureFlags.get(route.params.id)
    tenantFlags.value = data || {}
  } catch {
    tenantFlags.value = {}
  } finally {
    flagsLoading.value = false
  }
}

async function loadAuditLog() {
  auditLoading.value = true
  try {
    const { data } = await platformAPI.tenants.auditLog(route.params.id)
    auditRows.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    auditRows.value = []
  } finally {
    auditLoading.value = false
  }
}

async function loadLicense() {
  licenseLoading.value = true
  try {
    const { data } = await platformAPI.tenantLicense.get(route.params.id)
    licenseState.value = data
    licenseForm.value = {
      license_key: data.license_key || '',
      license_status: data.license_status || 'inactive',
      offline_grace_hours: data.offline_grace_hours ?? 72,
    }
  } catch {
    licenseState.value = null
  } finally {
    licenseLoading.value = false
  }
}

async function loadEnforcementLogs() {
  enforcementLoading.value = true
  try {
    const { data } = await platformAPI.tenantLicense.enforcementLogs(route.params.id)
    enforcementLogs.value = data.results || []
  } catch {
    enforcementLogs.value = []
  } finally {
    enforcementLoading.value = false
  }
}

async function saveLicense() {
  licenseSaving.value = true
  try {
    const { data } = await platformAPI.tenantLicense.update(route.params.id, licenseForm.value)
    licenseState.value = data
    notify.success('License updated')
    await loadEnforcementLogs()
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Save failed')
  } finally {
    licenseSaving.value = false
  }
}

async function loadIntegrations() {
  try {
    const [keysRes, whRes] = await Promise.all([
      platformAPI.tenantIntegrations.apiKeys.list(route.params.id),
      platformAPI.tenantIntegrations.webhooks.list(route.params.id),
    ])
    apiKeys.value = keysRes.data?.keys || []
    webhooks.value = whRes.data?.webhooks || []
  } catch {
    apiKeys.value = []
    webhooks.value = []
  }
}

async function createApiKey() {
  keysBusy.value = true
  newKeySecret.value = ''
  try {
    const { data } = await platformAPI.tenantIntegrations.apiKeys.create(route.params.id, {
      label: newKeyLabel.value,
    })
    newKeySecret.value = data.secret
    newKeyLabel.value = ''
    await loadIntegrations()
    notify.success('API key created')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Failed to create key')
  } finally {
    keysBusy.value = false
  }
}

async function revokeKey(keyId) {
  if (!window.confirm('Revoke this API key?')) return
  keysBusy.value = true
  try {
    await platformAPI.tenantIntegrations.apiKeys.revoke(route.params.id, keyId)
    await loadIntegrations()
    notify.success('Key revoked')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Revoke failed')
  } finally {
    keysBusy.value = false
  }
}

async function createWebhook() {
  webhooksBusy.value = true
  newWebhookSecret.value = ''
  try {
    const { data } = await platformAPI.tenantIntegrations.webhooks.create(route.params.id, {
      url: newWebhookUrl.value,
    })
    newWebhookSecret.value = data.signing_secret
    newWebhookUrl.value = ''
    await loadIntegrations()
    notify.success('Webhook created')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Failed to create webhook')
  } finally {
    webhooksBusy.value = false
  }
}

async function toggleWebhook(w, active) {
  try {
    await platformAPI.tenantIntegrations.webhooks.patch(route.params.id, w.id, { is_active: active })
    w.is_active = active
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Update failed')
    await loadIntegrations()
  }
}

async function removeWebhook(id) {
  if (!window.confirm('Delete this webhook endpoint?')) return
  try {
    await platformAPI.tenantIntegrations.webhooks.remove(route.params.id, id)
    await loadIntegrations()
    notify.success('Webhook deleted')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Delete failed')
  }
}

watch(activeTab, (tab) => {
  if (tab === 'license') {
    loadLicense()
    loadEnforcementLogs()
  } else if (tab === 'integrations') {
    loadIntegrations()
  }
})

async function impersonate(userId) {
  impBusy.value = true
  try {
    await authStore.startPlatformImpersonation(userId)
    notify.success('Impersonation started')
    await router.push('/dashboard')
  } catch (e) {
    notify.error(normalizeApiError(e).userMessage || 'Impersonation failed')
  } finally {
    impBusy.value = false
  }
}

onMounted(async () => {
  await load()
  await Promise.all([loadUsers(), loadFlags(), loadAuditLog()])
})

watch(
  () => route.params.id,
  async () => {
    activeTab.value = 'overview'
    await load()
    await Promise.all([loadUsers(), loadFlags(), loadAuditLog()])
  }
)
</script>
