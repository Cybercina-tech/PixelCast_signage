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
        <h3 class="text-lg font-bold text-primary">Edit plan — {{ editPlan.key }}</h3>
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
        <div class="flex gap-2 pt-2">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="planSaving" @click="savePlan">
            {{ planSaving ? 'Saving…' : 'Save' }}
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
        <div class="flex gap-2 pt-2">
          <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="promoSaving" @click="savePromo">
            {{ promoSaving ? 'Saving…' : 'Save' }}
          </button>
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" @click="editPromoRow = null">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const loading = ref(true)
const settingsLoading = ref(true)
const promoLoading = ref(true)
const bannerError = ref(null)

const plans = ref([])
const promotions = ref([])

const settingsForm = ref({
  default_free_screen_limit: 1,
  trial_days_display: 14,
  checkout_allow_promotion_codes: true,
})

const settingsSaving = ref(false)
const planSaving = ref(false)
const promoSaving = ref(false)

const editPlan = ref(null)
const editPromoRow = ref(null)

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
    await platformAPI.pricingSettings.patch(settingsForm.value)
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
  } finally {
    settingsSaving.value = false
  }
}

function openEdit(p) {
  editPlan.value = {
    ...p,
    included_screens: p.included_screens ?? '',
    description: p.description ?? '',
  }
}

async function savePlan() {
  if (!editPlan.value) return
  planSaving.value = true
  bannerError.value = null
  try {
    const payload = { ...editPlan.value }
    delete payload.id
    if (payload.included_screens === '' || payload.included_screens === undefined) {
      payload.included_screens = null
    }
    if (payload.display_amount_cents === '') {
      payload.display_amount_cents = null
    }
    await platformAPI.pricingPlans.patch(editPlan.value.key, payload)
    editPlan.value = null
    await loadPlans()
  } catch (e) {
    bannerError.value = normalizeApiError(e).userMessage || 'Save failed'
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
