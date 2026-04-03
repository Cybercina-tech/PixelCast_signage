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
            <div><span class="text-muted">Trial end</span> — {{ fmt(tenant.trial_end) }}</div>
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
    await load()
    await Promise.all([loadUsers(), loadFlags(), loadAuditLog()])
  }
)
</script>
