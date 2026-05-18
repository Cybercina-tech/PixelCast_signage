<template>
  <div class="space-y-8">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Pricing catalog</h1>
        <p class="text-sm text-muted mt-1">Stripe price IDs, plan copy, and checkout defaults</p>
      </div>
      <div class="flex flex-wrap gap-2">
        <router-link to="/super-admin/billing" class="btn-outline px-4 py-2 rounded-lg text-sm">
          Billing center
        </router-link>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="openCreatePlan">Add plan</button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="loadAll">
          Refresh
        </button>
      </div>
    </div>

    <div
      v-if="bannerError"
      class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-900 dark:text-amber-100"
    >
      {{ bannerError }}
    </div>

    <Card title="Stripe runtime configuration">
      <div v-if="stripeStatusLoading" class="text-sm text-muted py-4">Loading…</div>
      <div v-else-if="stripeStatus" class="space-y-4">
        <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div
            v-for="item in stripeStatusItems"
            :key="item.key"
            class="rounded-xl border px-3 py-2"
            :class="item.ok ? 'border-emerald-500/40 bg-emerald-500/5' : 'border-amber-500/40 bg-amber-500/10'"
          >
            <p class="text-[10px] font-semibold uppercase tracking-wider text-muted">{{ item.label }}</p>
            <p class="text-sm font-medium mt-1" :class="item.ok ? 'text-emerald-500' : 'text-amber-600 dark:text-amber-300'">
              {{ item.ok ? 'Configured' : 'Missing' }}
            </p>
          </div>
        </div>
        <div class="grid sm:grid-cols-2 gap-4 max-w-4xl">
          <div>
            <label class="label-base block text-sm mb-1">Publishable key</label>
            <input
              v-model.trim="settingsForm.stripe_publishable_key"
              type="text"
              class="input-base w-full px-3 py-2 rounded-lg font-mono text-xs"
              placeholder="pk_live_..."
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Default currency</label>
            <input
              v-model.trim="settingsForm.stripe_default_currency"
              type="text"
              class="input-base w-full px-3 py-2 rounded-lg"
              placeholder="usd"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Secret key</label>
            <input
              v-model.trim="settingsForm.stripe_secret_key"
              type="password"
              class="input-base w-full px-3 py-2 rounded-lg font-mono text-xs"
              :placeholder="settingsForm.stripe_secret_key_masked || 'sk_live_...'"
              autocomplete="new-password"
            />
            <p class="text-xs text-muted mt-1">Leave empty to keep current value. Enter `clear` to remove.</p>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Webhook signing secret</label>
            <input
              v-model.trim="settingsForm.stripe_webhook_secret"
              type="password"
              class="input-base w-full px-3 py-2 rounded-lg font-mono text-xs"
              :placeholder="settingsForm.stripe_webhook_secret_masked || 'whsec_...'"
              autocomplete="new-password"
            />
            <p class="text-xs text-muted mt-1">Leave empty to keep current value. Enter `clear` to remove.</p>
          </div>
          <div class="sm:col-span-2">
            <label class="flex items-center gap-2 text-sm text-secondary">
              <input v-model="settingsForm.stripe_customer_portal_enabled" type="checkbox" class="rounded border-border-color" />
              Enable Stripe customer portal for tenant billing self-service
            </label>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="settingsSaving" @click="saveSettings">
            {{ settingsSaving ? 'Saving…' : 'Save Stripe configuration' }}
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="stripeHealthLoading" @click="runStripeHealthCheck">
            {{ stripeHealthLoading ? 'Checking…' : 'Run health check' }}
          </button>
        </div>
        <div v-if="stripeHealth" class="rounded-xl border border-border-color/60 px-4 py-3 bg-surface-inset/40 text-sm">
          <p class="font-medium" :class="stripeHealth.ready ? 'text-emerald-500' : 'text-amber-500'">
            {{ stripeHealth.ready ? 'Live readiness: ready' : 'Live readiness: blocked' }}
          </p>
          <p class="text-muted mt-1">{{ stripeHealth.message || 'No message' }}</p>
          <p class="text-xs text-muted mt-2">
            Mode: {{ stripeHealth.mode || 'unknown' }} · Account: {{ stripeHealth.account_id || 'n/a' }} · Charges enabled:
            {{ stripeHealth.charges_enabled ? 'yes' : 'no' }}
          </p>
          <ul v-if="Array.isArray(stripeHealth.blocking_reasons) && stripeHealth.blocking_reasons.length" class="mt-2 space-y-1">
            <li v-for="(reason, idx) in stripeHealth.blocking_reasons" :key="idx" class="text-xs text-amber-400">
              - {{ reason }}
            </li>
          </ul>
        </div>
        <p class="text-xs text-muted max-w-3xl">
          Stripe credentials are stored encrypted in the database and managed from this panel. Map Stripe Price IDs in
          the plans table below; trial logic remains in Stripe Dashboard.
        </p>
      </div>
      <p v-else class="text-sm text-muted py-4">Could not load Stripe status.</p>
    </Card>

    <Card title="Platform defaults">
      <div v-if="settingsLoading" class="text-sm text-muted py-4">Loading…</div>
      <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-3xl">
        <div>
          <label class="label-base block text-sm mb-1">Default free screen limit</label>
          <input
            v-model.number="settingsForm.default_free_screen_limit"
            type="number"
            min="0"
            class="input-base w-full px-3 py-2 rounded-lg"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Trial days (display)</label>
          <input
            v-model.number="settingsForm.trial_days_display"
            type="number"
            min="1"
            class="input-base w-full px-3 py-2 rounded-lg"
          />
        </div>
        <div class="flex items-end">
          <label class="flex items-center gap-2 text-sm text-secondary">
            <input v-model="settingsForm.checkout_allow_promotion_codes" type="checkbox" class="rounded border-border-color" />
            Allow promotion codes at Stripe Checkout
          </label>
        </div>
      </div>
      <div class="mt-4">
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="settingsSaving" @click="saveSettings">
          {{ settingsSaving ? 'Saving…' : 'Save defaults' }}
        </button>
      </div>
      <p class="text-xs text-muted mt-3 max-w-2xl">
        Create coupons and promotion codes in Stripe; customers can enter codes at Checkout when this is enabled. You can
        also store preset promotion code IDs below for optional server-side application.
      </p>
    </Card>

    <Card title="Subscription plans">
      <div v-if="loading" class="text-sm text-muted py-6">Loading plans…</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm text-left border-collapse">
          <thead>
            <tr class="border-b border-border-color">
              <th class="py-2 pr-3 font-semibold text-primary">Key</th>
              <th class="py-2 pr-3 font-semibold text-primary">Label</th>
              <th class="py-2 pr-3 font-semibold text-primary">Kind</th>
              <th class="py-2 pr-3 font-semibold text-primary">Stripe price ID</th>
              <th class="py-2 pr-3 font-semibold text-primary">Active</th>
              <th class="py-2 pr-3 font-semibold text-primary"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in plans" :key="p.key" class="border-b border-border-color/60">
              <td class="py-2 pr-3 font-mono text-xs">{{ p.key }}</td>
              <td class="py-2 pr-3">{{ p.label }}</td>
              <td class="py-2 pr-3">{{ p.kind }}</td>
              <td class="py-2 pr-3 font-mono text-xs max-w-[12rem] truncate" :title="p.stripe_price_id">{{ p.stripe_price_id || '—' }}</td>
              <td class="py-2 pr-3">{{ p.is_active ? 'Yes' : 'No' }}</td>
              <td class="py-2 pr-2 text-right">
                <button type="button" class="btn-outline px-3 py-1 rounded-lg text-xs" @click="openEdit(p)">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>

    <Card title="Promotion codes (optional)">
      <p class="text-sm text-muted mb-4">Map Stripe Promotion Code ids (<code class="text-xs">promo_…</code>) for reference or future automation.</p>
      <div v-if="promoLoading" class="text-sm text-muted py-4">Loading…</div>
      <div v-else class="space-y-3">
        <div v-for="pr in promotions" :key="pr.id" class="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border-color/60 px-3 py-2">
          <div>
            <span class="font-medium text-primary">{{ pr.label }}</span>
            <span class="text-xs font-mono text-muted ml-2">{{ pr.stripe_promotion_code_id }}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs" :class="pr.is_active ? 'text-emerald-500' : 'text-muted'">{{ pr.is_active ? 'Active' : 'Off' }}</span>
            <button type="button" class="btn-outline px-2 py-1 rounded text-xs" @click="editPromo(pr)">Edit</button>
          </div>
        </div>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="addPromo">Add promotion</button>
      </div>
    </Card>

    <!-- Edit plan modal -->
    <div
      v-if="editPlan"
      class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60"
      role="dialog"
      aria-modal="true"
      @click.self="editPlan = null"
    >
      <div class="card-base rounded-2xl p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto space-y-3" @click.stop>
        <h3 class="text-lg font-bold text-primary">{{ editPlan._isNew ? 'New plan' : `Edit plan — ${editPlan.key}` }}</h3>
        <div v-if="editPlan._isNew">
          <label class="label-base text-xs">Key (slug)</label>
          <input v-model="editPlan.key" type="text" required class="input-base w-full px-3 py-2 rounded-lg font-mono text-sm" />
        </div>
        <div>
          <label class="label-base text-xs">Label</label>
          <input v-model="editPlan.label" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <div>
          <label class="label-base text-xs">Description</label>
          <textarea v-model="editPlan.description" rows="3" class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label-base text-xs">Kind</label>
            <select v-model="editPlan.kind" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="free">free</option>
              <option value="bundle">bundle</option>
              <option value="per_screen">per_screen</option>
              <option value="vip">vip</option>
            </select>
          </div>
          <div>
            <label class="label-base text-xs">Sort order</label>
            <input v-model.number="editPlan.sort_order" type="number" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label-base text-xs">Included screens (bundle)</label>
            <input v-model.number="editPlan.included_screens" type="number" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base text-xs">Min quantity (per_screen)</label>
            <input v-model.number="editPlan.min_quantity" type="number" min="1" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="editPlan.is_unlimited" type="checkbox" />
          Unlimited (VIP)
        </label>
        <div>
          <label class="label-base text-xs">Stripe price ID</label>
          <input v-model="editPlan.stripe_price_id" type="text" class="input-base w-full px-3 py-2 rounded-lg font-mono text-xs" placeholder="price_…" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label-base text-xs">Display amount (cents, optional)</label>
            <input v-model.number="editPlan.display_amount_cents" type="number" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base text-xs">Currency</label>
            <input v-model="editPlan.currency" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </div>
        <div>
          <label class="label-base text-xs">Badge</label>
          <input v-model="editPlan.badge" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="editPlan.is_active" type="checkbox" />
          Active
        </label>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="editPlan.highlight" type="checkbox" />
          Highlight on marketing pages
        </label>
        <div class="flex gap-2 pt-2 flex-wrap">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="planSaving" @click="savePlan">
            {{ planSaving ? 'Saving…' : 'Save' }}
          </button>
          <button
            v-if="editPlan?.key && !editPlan._isNew"
            type="button"
            class="btn-outline px-4 py-2 rounded-lg text-sm text-rose-400"
            :disabled="planSaving"
            @click="deletePlan"
          >
            Delete plan
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="editPlan = null">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Edit promo modal -->
    <div
      v-if="editPromoRow"
      class="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/60"
      role="dialog"
      aria-modal="true"
      @click.self="editPromoRow = null"
    >
      <div class="card-base rounded-2xl p-6 max-w-md w-full space-y-3" @click.stop>
        <h3 class="text-lg font-bold text-primary">{{ editPromoRow.id ? 'Edit promotion' : 'New promotion' }}</h3>
        <div>
          <label class="label-base text-xs">Label</label>
          <input v-model="editPromoRow.label" type="text" class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <div>
          <label class="label-base text-xs">Stripe promotion code id</label>
          <input v-model="editPromoRow.stripe_promotion_code_id" type="text" class="input-base w-full px-3 py-2 rounded-lg font-mono text-xs" placeholder="promo_…" />
        </div>
        <div>
          <label class="label-base text-xs">Sort order</label>
          <input v-model.number="editPromoRow.sort_order" type="number" class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <label class="flex items-center gap-2 text-sm">
          <input v-model="editPromoRow.is_active" type="checkbox" />
          Active
        </label>
        <div class="flex gap-2 pt-2 flex-wrap">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="promoSaving" @click="savePromo">
            {{ promoSaving ? 'Saving…' : 'Save' }}
          </button>
          <button
            v-if="editPromoRow.id"
            type="button"
            class="btn-outline px-4 py-2 rounded-lg text-sm text-rose-400"
            :disabled="promoSaving"
            @click="deletePromo"
          >
            Delete
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="editPromoRow = null">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const settingsLoading = ref(true)
const promoLoading = ref(true)
const stripeStatusLoading = ref(true)
const stripeHealthLoading = ref(false)
const bannerError = ref(null)
const stripeStatus = ref(null)
const stripeHealth = ref(null)

const plans = ref([])
const promotions = ref([])

const settingsForm = ref({
  default_free_screen_limit: 1,
  trial_days_display: 14,
  checkout_allow_promotion_codes: true,
  stripe_publishable_key: '',
  stripe_secret_key: '',
  stripe_secret_key_masked: '',
  stripe_webhook_secret: '',
  stripe_webhook_secret_masked: '',
  stripe_default_currency: 'usd',
  stripe_customer_portal_enabled: true,
})

const settingsSaving = ref(false)
const planSaving = ref(false)
const promoSaving = ref(false)

const editPlan = ref(null)
const editPromoRow = ref(null)

const stripeStatusItems = computed(() => {
  const s = stripeStatus.value
  if (!s) return []
  return [
    { key: 'secret', label: 'Secret key', ok: s.stripe_secret_key_configured },
    { key: 'webhook', label: 'Webhook secret', ok: s.stripe_webhook_secret_configured },
    { key: 'publishable', label: 'Publishable key', ok: s.stripe_publishable_key_configured },
    { key: 'checkout', label: 'Checkout ready', ok: s.checkout_ready },
  ]
})

async function loadStripeStatus() {
  stripeStatusLoading.value = true
  try {
    const { data } = await platformAPI.stripeStatus()
    stripeStatus.value = data
  } catch {
    stripeStatus.value = null
  } finally {
    stripeStatusLoading.value = false
  }
}

async function runStripeHealthCheck() {
  stripeHealthLoading.value = true
  try {
    const { data } = await platformAPI.stripeConnectionHealth()
    stripeHealth.value = data
  } catch (e) {
    stripeHealth.value = {
      api_reachable: false,
      message: normalizeApiError(e).userMessage || 'Could not run health check',
    }
  } finally {
    stripeHealthLoading.value = false
  }
}

async function loadPlans() {
  const { data } = await platformAPI.pricingPlans.list()
  plans.value = data.results || data || []
}

async function loadSettings() {
  const { data } = await platformAPI.pricingSettings.get()
  settingsForm.value = {
    default_free_screen_limit: data.default_free_screen_limit ?? 1,
    trial_days_display: data.trial_days_display ?? 14,
    checkout_allow_promotion_codes: data.checkout_allow_promotion_codes !== false,
    stripe_publishable_key: data.stripe_publishable_key ?? '',
    stripe_secret_key: '',
    stripe_secret_key_masked: data.stripe_secret_key_masked ?? '',
    stripe_webhook_secret: '',
    stripe_webhook_secret_masked: data.stripe_webhook_secret_masked ?? '',
    stripe_default_currency: data.stripe_default_currency ?? 'usd',
    stripe_customer_portal_enabled: data.stripe_customer_portal_enabled !== false,
  }
}

async function loadPromotions() {
  const { data } = await platformAPI.pricingPromotions.list()
  promotions.value = data.results || data || []
}

async function loadAll() {
  bannerError.value = null
  loading.value = true
  settingsLoading.value = true
  promoLoading.value = true
  await loadStripeStatus()
  try {
    await loadSettings()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Could not load settings'
  } finally {
    settingsLoading.value = false
  }
  try {
    await loadPlans()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Could not load plans'
  } finally {
    loading.value = false
  }
  try {
    await loadPromotions()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Could not load promotions'
  } finally {
    promoLoading.value = false
  }
}

async function saveSettings() {
  settingsSaving.value = true
  bannerError.value = null
  try {
    const payload = {
      default_free_screen_limit: settingsForm.value.default_free_screen_limit,
      trial_days_display: settingsForm.value.trial_days_display,
      checkout_allow_promotion_codes: settingsForm.value.checkout_allow_promotion_codes,
      stripe_publishable_key: settingsForm.value.stripe_publishable_key,
      stripe_default_currency: settingsForm.value.stripe_default_currency,
      stripe_customer_portal_enabled: settingsForm.value.stripe_customer_portal_enabled,
    }
    const secret = (settingsForm.value.stripe_secret_key || '').trim()
    if (secret) {
      payload.stripe_secret_key = secret.toLowerCase() === 'clear' ? '' : secret
    }
    const webhook = (settingsForm.value.stripe_webhook_secret || '').trim()
    if (webhook) {
      payload.stripe_webhook_secret = webhook.toLowerCase() === 'clear' ? '' : webhook
    }
    await platformAPI.pricingSettings.patch(payload)
    await loadSettings()
    await loadStripeStatus()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    settingsSaving.value = false
  }
}

function openEdit(p) {
  editPlan.value = {
    ...p,
    _isNew: false,
    included_screens: p.included_screens ?? '',
    description: p.description ?? '',
  }
}

function openCreatePlan() {
  editPlan.value = {
    _isNew: true,
    key: '',
    label: '',
    kind: 'per_screen',
    description: '',
    sort_order: 0,
    included_screens: '',
    min_quantity: 1,
    is_unlimited: false,
    stripe_price_id: '',
    display_amount_cents: '',
    currency: 'usd',
    badge: '',
    is_active: true,
    highlight: false,
  }
}

async function savePlan() {
  if (!editPlan.value) return
  planSaving.value = true
  bannerError.value = null
  try {
    const isNew = !!editPlan.value._isNew
    const payload = { ...editPlan.value }
    delete payload.id
    delete payload._isNew
    if (payload.included_screens === '' || payload.included_screens === undefined) {
      payload.included_screens = null
    }
    if (payload.display_amount_cents === '') {
      payload.display_amount_cents = null
    }
    if (isNew) {
      await platformAPI.pricingPlans.create(payload)
    } else {
      await platformAPI.pricingPlans.patch(editPlan.value.key, payload)
    }
    editPlan.value = null
    await loadPlans()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    planSaving.value = false
  }
}

async function deletePlan() {
  if (!editPlan.value?.key || editPlan.value._isNew) return
  if (!window.confirm(`Delete plan "${editPlan.value.key}"?`)) return
  planSaving.value = true
  try {
    await platformAPI.pricingPlans.remove(editPlan.value.key)
    editPlan.value = null
    await loadPlans()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Delete failed'
  } finally {
    planSaving.value = false
  }
}

function addPromo() {
  editPromoRow.value = {
    id: null,
    label: '',
    stripe_promotion_code_id: '',
    sort_order: 0,
    is_active: true,
  }
}

function editPromo(pr) {
  editPromoRow.value = { ...pr }
}

async function deletePromo() {
  if (!editPromoRow.value?.id) return
  if (!window.confirm('Delete this promotion?')) return
  promoSaving.value = true
  try {
    await platformAPI.pricingPromotions.remove(editPromoRow.value.id)
    editPromoRow.value = null
    await loadPromotions()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Delete failed'
  } finally {
    promoSaving.value = false
  }
}

async function savePromo() {
  if (!editPromoRow.value) return
  promoSaving.value = true
  bannerError.value = null
  try {
    const row = editPromoRow.value
    if (row.id) {
      await platformAPI.pricingPromotions.patch(row.id, {
        label: row.label,
        stripe_promotion_code_id: row.stripe_promotion_code_id,
        sort_order: row.sort_order,
        is_active: row.is_active,
      })
    } else {
      await platformAPI.pricingPromotions.create({
        label: row.label,
        stripe_promotion_code_id: row.stripe_promotion_code_id,
        sort_order: row.sort_order,
        is_active: row.is_active,
      })
    }
    editPromoRow.value = null
    await loadPromotions()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    promoSaving.value = false
  }
}

onMounted(() => {
  loadAll()
})
</script>
