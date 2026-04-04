<template>
  <div class="pricing-page min-h-screen min-h-[100dvh] bg-slate-950 text-white relative overflow-hidden">
    <div class="fixed inset-0 starfield-background pointer-events-none opacity-90 z-0" aria-hidden="true" />

    <header class="sticky top-0 z-40 border-b border-white/10 bg-slate-950/85 backdrop-blur-md safe-area-pt">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div class="flex items-center gap-3 min-w-0">
          <router-link to="/" class="flex items-center gap-2 shrink-0">
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center">
              <svg class="w-[1.125rem] h-[1.125rem] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span class="font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent truncate">
              PixelCast
            </span>
          </router-link>
          <span class="text-white/40 hidden sm:inline">/</span>
          <h1 class="text-lg font-semibold text-white truncate">Plans &amp; pricing</h1>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link
            to="/"
            class="px-4 py-2 rounded-lg text-sm border border-white/15 hover:border-cyan-400/40 transition-colors"
          >
            Home
          </router-link>
          <router-link
            to="/docs"
            class="px-4 py-2 rounded-lg text-sm border border-white/15 hover:border-white/35 transition-colors"
          >
            Docs
          </router-link>
        </div>
      </div>
    </header>

    <main class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 pb-24">
      <div
        v-if="loadError"
        class="rounded-xl border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100 mb-8"
      >
        {{ loadError }}
      </div>

      <div v-if="!saasEnabled" class="glass-card rounded-2xl p-8 border border-white/10 mb-10">
        <h2 class="text-xl font-bold text-white mb-2">Self-hosted deployment</h2>
        <p class="text-on-starfield text-sm leading-relaxed mb-4">
          Cloud subscriptions are not enabled on this instance. Purchase a self-hosted license on CodeCanyon and use
          license activation, or see documentation for your setup path.
        </p>
        <div class="flex flex-wrap gap-3">
          <router-link to="/" class="neon-button px-5 py-2.5 rounded-lg text-sm font-semibold text-white">
            Back to home
          </router-link>
          <router-link
            to="/install"
            class="px-5 py-2.5 rounded-lg text-sm font-semibold border border-white/20 hover:border-white/40"
          >
            Installation
          </router-link>
        </div>
      </div>

      <template v-else>
        <p class="text-center text-white max-w-2xl mx-auto mb-10 text-sm sm:text-base leading-relaxed">
          Start with a full-featured {{ trialDays }}-day trial (see signup flow), then scale with subscriptions sized to your
          fleet. Checkout and invoices run on Stripe. Promotional codes can be applied when enabled by the platform.
        </p>

        <div v-if="loading" class="grid sm:grid-cols-2 lg:grid-cols-2 gap-5 animate-pulse">
          <div v-for="n in 4" :key="n" class="h-64 rounded-2xl bg-white/5 border border-white/10" />
        </div>

        <div v-else class="grid md:grid-cols-2 gap-5 lg:gap-6">
          <article
            v-for="plan in sortedPlans"
            :key="plan.key"
            class="glass-card rounded-2xl p-6 lg:p-7 border flex flex-col"
            :class="plan.highlight ? 'border-cyan-400/35 shadow-[0_0_24px_rgba(34,211,238,0.12)]' : 'border-white/10'"
          >
            <div class="flex items-start justify-between gap-3 mb-3">
              <div>
                <h2 class="text-xl font-bold text-white">{{ plan.label }}</h2>
                <p v-if="plan.badge" class="text-xs font-semibold text-cyan-300/90 mt-1">{{ plan.badge }}</p>
              </div>
              <span
                class="text-xs uppercase tracking-wide font-semibold px-2 py-1 rounded-md"
                :class="kindBadgeClass(plan.kind)"
              >
                {{ kindLabel(plan.kind) }}
              </span>
            </div>
            <p class="text-on-starfield text-sm leading-relaxed flex-1 mb-5">
              {{ plan.description || defaultDescription(plan) }}
            </p>
            <div class="mb-5">
              <p class="text-3xl font-bold text-white">{{ priceLine(plan) }}</p>
              <p v-if="plan.kind === 'per_screen' && plan.display_amount_cents != null" class="text-slate-500 text-xs mt-1">
                Per screen, per billing period (before discounts). Configure the Stripe price in the admin catalog.
              </p>
            </div>
            <div v-if="plan.kind === 'per_screen'" class="mb-5">
              <label class="block text-xs font-medium text-on-starfield-muted mb-1">Screens (quantity)</label>
              <input
                v-model.number="quantities[plan.key]"
                type="number"
                :min="Math.max(1, plan.min_quantity || 1)"
                class="w-full rounded-lg bg-slate-900/80 border border-white/15 px-3 py-2 text-white text-sm"
              />
            </div>
            <div class="mt-auto space-y-2">
              <button
                v-if="plan.kind === 'free'"
                type="button"
                class="w-full neon-button-large py-3 rounded-xl font-semibold text-white"
                @click="goSignup"
              >
                {{ isAuthed ? 'Open dashboard' : 'Create account' }}
              </button>
              <template v-else>
                <button
                  v-if="canSubscribe"
                  type="button"
                  class="w-full neon-button-large py-3 rounded-xl font-semibold text-white disabled:opacity-50"
                  :disabled="checkoutBusy || !plan.checkout_available"
                  @click="checkout(plan)"
                >
                  {{
                    checkoutBusy
                      ? 'Redirecting…'
                      : !plan.checkout_available
                        ? 'Configure Stripe price (admin)'
                        : 'Continue with Stripe'
                  }}
                </button>
                <router-link
                  v-else
                  :to="signupLink"
                  class="block w-full text-center neon-button-large py-3 rounded-xl font-semibold text-white"
                >
                  Sign up to subscribe
                </router-link>
              </template>
            </div>
          </article>
        </div>

        <p class="text-center text-slate-500 text-xs mt-10 max-w-xl mx-auto">
          Prices are charged by Stripe. Marketing amounts are indicative; set Stripe Price IDs in Super Admin → Pricing.
        </p>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { publicAPI, platformAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'
import { useRouteHead } from '@/composables/useRouteHead'

useRouteHead()

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const loadError = ref('')
const saasEnabled = ref(true)
const plans = ref([])
const trialDays = ref(14)
const freeLimit = ref(1)

const quantities = reactive({})

const checkoutBusy = ref(false)

const isAuthed = computed(() => auth.isAuthenticated)

const canSubscribe = computed(() => {
  if (!auth.isAuthenticated || !auth.user) return false
  const r = auth.user.role
  return r === 'Manager' || r === 'Developer'
})

const signupLink = computed(() => ({
  path: '/signup',
  query: { next: '/pricing' },
}))

const sortedPlans = computed(() => {
  const list = Array.isArray(plans.value) ? [...plans.value] : []
  return list.sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
})

function kindLabel(kind) {
  const m = { free: 'Free', bundle: 'Bundle', per_screen: 'Per screen', vip: 'VIP' }
  return m[kind] || kind
}

function kindBadgeClass(kind) {
  if (kind === 'free') return 'bg-slate-700/80 text-slate-200'
  if (kind === 'bundle') return 'bg-purple-500/20 text-purple-200'
  if (kind === 'per_screen') return 'bg-amber-500/15 text-amber-100'
  if (kind === 'vip') return 'bg-emerald-500/15 text-emerald-100'
  return 'bg-white/10 text-slate-200'
}

function defaultDescription(plan) {
  if (plan.kind === 'free') return `Up to ${freeLimit.value} screen(s) on the free tier—upgrade for more capacity.`
  if (plan.kind === 'bundle' && plan.included_screens)
    return `Includes up to ${plan.included_screens} screens on one subscription.`
  if (plan.kind === 'per_screen') return 'Subscribe with a quantity that matches your fleet size.'
  if (plan.kind === 'vip' || plan.is_unlimited) return 'Unlimited screens for your organization.'
  return ''
}

function formatMoney(cents, currency) {
  if (cents == null || Number.isNaN(Number(cents))) return '—'
  const cur = (currency || 'usd').toUpperCase()
  try {
    return new Intl.NumberFormat(undefined, { style: 'currency', currency: cur }).format(Number(cents) / 100)
  } catch {
    return `$${(Number(cents) / 100).toFixed(2)}`
  }
}

function priceLine(plan) {
  if (plan.kind === 'free') return 'Free'
  if (plan.kind === 'per_screen' && plan.display_amount_cents != null) {
    return `${formatMoney(plan.display_amount_cents, plan.currency)} / screen / mo`
  }
  if (plan.display_amount_cents != null) return `${formatMoney(plan.display_amount_cents, plan.currency)} / mo`
  if (plan.kind === 'vip' || plan.kind === 'bundle') return 'See checkout'
  return 'See checkout'
}

async function load() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await publicAPI.pricing()
    saasEnabled.value = Boolean(data.saas_enabled)
    trialDays.value = data.trial_days_display ?? 14
    freeLimit.value = data.default_free_screen_limit ?? 1
    plans.value = data.plans || []
    for (const p of plans.value) {
      const minQ = Math.max(1, p.min_quantity || 1)
      if (quantities[p.key] == null) quantities[p.key] = minQ
    }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Could not load pricing.'
  } finally {
    loading.value = false
  }
}

watch(
  () => plans.value,
  (list) => {
    for (const p of list || []) {
      const minQ = Math.max(1, p.min_quantity || 1)
      if (quantities[p.key] == null) quantities[p.key] = minQ
    }
  },
  { immediate: true }
)

function goSignup() {
  if (isAuthed.value) {
    router.push('/dashboard')
    return
  }
  router.push(signupLink.value)
}

async function checkout(plan) {
  if (!canSubscribe.value) {
    router.push(signupLink.value)
    return
  }
  const base = typeof window !== 'undefined' ? `${window.location.origin}` : ''
  const payload = {
    plan_key: plan.key,
    success_url: `${base}/settings?billing=1`,
    cancel_url: `${base}/pricing?billing=cancel`,
  }
  if (plan.kind === 'per_screen') {
    const q = quantities[plan.key]
    payload.quantity = Math.max(plan.min_quantity || 1, Number(q) || 1)
  }
  checkoutBusy.value = true
  try {
    const { data } = await platformAPI.billingCheckout(payload)
    if (data.url) {
      window.location.href = data.url
    }
  } catch (e) {
    loadError.value = normalizeApiError(e).userMessage || 'Checkout failed.'
  } finally {
    checkoutBusy.value = false
  }
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.pricing-page {
  /* Same token isolation as landing — cosmic UI is always dark copy regardless of app light theme */
  --text-body: #e2e8f0;
  --text-main: #e2e8f0;
  --text-heading: #f8fafc;
  --text-muted: #94a3b8;
  color-scheme: dark;
}
.starfield-background {
  background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%);
}
.starfield-background::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: radial-gradient(1px 1px at 20px 30px, rgba(255, 255, 255, 0.35), transparent),
    radial-gradient(1px 1px at 40px 70px, rgba(255, 255, 255, 0.2), transparent);
  background-size: 200px 200px;
  opacity: 0.35;
}
.glass-card {
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}
.neon-button-large {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.35) 0%, rgba(124, 58, 237, 0.45) 100%);
  box-shadow: 0 0 20px rgba(34, 211, 238, 0.15);
}
</style>
