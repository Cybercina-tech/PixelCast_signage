<template>
  <div class="auth-page cosmic-auth min-h-screen flex flex-col items-center justify-center px-4 py-12 sm:py-16 relative">
    <!-- Deep space gradient base -->
    <div class="cosmic-bg" aria-hidden="true" />

    <!-- Animated starfield -->
    <div class="cosmic-starfield" aria-hidden="true" />

    <!-- Nebula accents -->
    <div class="nebula nebula--indigo" aria-hidden="true" />
    <div class="nebula nebula--purple" aria-hidden="true" />

    <div class="w-full max-w-md relative z-10">
      <!-- Glass-portal card -->
      <div
        v-motion
        :initial="{ opacity: 0, y: 12 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 350 }"
        class="glass-portal rounded-2xl overflow-hidden"
      >
        <div class="px-8 sm:px-10 py-10 sm:py-12">
          <!-- Header -->
          <div class="text-center mb-8">
            <h1 class="cosmic-heading text-2xl sm:text-3xl font-bold text-white tracking-wide">
              Create account
            </h1>
            <p class="mt-2 text-sm text-slate-400">
              Sign up with your email to get started
            </p>
          </div>

          <form @submit.prevent="handleSignup" class="space-y-5">
            <!-- Error message -->
            <transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 -translate-y-1"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition-all duration-200 ease-in"
              leave-from-class="opacity-100 translate-y-0"
              leave-to-class="opacity-0 -translate-y-1"
            >
              <div
                v-if="error"
                class="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3.5 text-sm text-red-300 flex items-start gap-2.5"
                role="alert"
              >
                <ExclamationCircleIcon class="h-5 w-5 flex-shrink-0 mt-0.5 text-red-400 cosmic-icon" />
                <span class="flex-1">{{ error }}</span>
              </div>
            </transition>

            <!-- Email (floating label) -->
            <div class="input-wrap">
              <div class="input-group relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors duration-300 cosmic-icon-wrap">
                  <EnvelopeIcon class="h-5 w-5 cosmic-icon" />
                </div>
                <input
                  id="signup-email"
                  v-model="form.email"
                  type="email"
                  required
                  autocomplete="email"
                  class="auth-input cosmic-input w-full pl-11 pr-4 py-3 rounded-xl border border-white/10 bg-black/40 text-white placeholder-transparent focus:outline-none focus:border-indigo-500 hover:border-white/20 transition-all duration-300"
                  :class="{ 'border-red-500/50 focus:border-red-400': fieldErrors.email }"
                  placeholder=" "
                  @focus="focusEmail = true"
                  @blur="focusEmail = false"
                />
                <label
                  for="signup-email"
                  class="floating-label cosmic-floating-label"
                  :class="{ 'floating-label--active': form.email || focusEmail }"
                >
                  Email
                </label>
              </div>
              <p v-if="fieldErrors.email" class="mt-1.5 text-xs text-red-400">{{ fieldErrorMsg('email') }}</p>
            </div>

            <!-- Password (floating label) -->
            <div class="input-wrap">
              <div class="input-group relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors duration-300 cosmic-icon-wrap">
                  <LockClosedIcon class="h-5 w-5 cosmic-icon" />
                </div>
                <input
                  id="signup-password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  autocomplete="new-password"
                  class="auth-input cosmic-input w-full pl-11 pr-12 py-3 rounded-xl border border-white/10 bg-black/40 text-white placeholder-transparent focus:outline-none focus:border-indigo-500 hover:border-white/20 transition-all duration-300"
                  :class="{ 'border-red-500/50 focus:border-red-400': fieldErrors.password }"
                  placeholder=" "
                  @focus="focusPassword = true"
                  @blur="focusPassword = false"
                />
                <label
                  for="signup-password"
                  class="floating-label cosmic-floating-label"
                  :class="{ 'floating-label--active': form.password || focusPassword }"
                >
                  Password
                </label>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-cyan-400 focus:outline-none transition-colors duration-300 cosmic-icon-wrap"
                  tabindex="-1"
                  :aria-label="showPassword ? 'Hide password' : 'Show password'"
                >
                  <EyeIcon v-if="!showPassword" class="h-5 w-5 cosmic-icon" />
                  <EyeSlashIcon v-else class="h-5 w-5 cosmic-icon" />
                </button>
              </div>
              <!-- Password strength -->
              <div class="mt-2 flex items-center gap-2">
                <div class="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
                  <div
                    class="h-full rounded-full transition-all duration-300 ease-out"
                    :class="passwordStrengthClass"
                    :style="{ width: `${passwordStrengthWidth}%` }"
                  />
                </div>
                <span class="text-xs text-slate-500 min-w-[4rem]" :class="passwordStrengthTextClass">
                  {{ passwordStrengthLabel }}
                </span>
              </div>
              <p class="mt-1 text-xs text-slate-500">At least 8 characters; letters and numbers recommended.</p>
              <p v-if="fieldErrors.password" class="mt-1 text-xs text-red-400">{{ fieldErrorMsg('password') }}</p>
            </div>

            <!-- Confirm Password (floating label) -->
            <div class="input-wrap">
              <div class="input-group relative group">
                <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500 group-focus-within:text-indigo-400 transition-colors duration-300 cosmic-icon-wrap">
                  <LockClosedIcon class="h-5 w-5 cosmic-icon" />
                </div>
                <input
                  id="signup-password-confirm"
                  v-model="form.password_confirm"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  required
                  autocomplete="new-password"
                  placeholder=" "
                  :class="[
                    'auth-input cosmic-input w-full pl-11 pr-12 py-3 rounded-xl border bg-black/40 text-white placeholder-transparent focus:outline-none focus:border-indigo-500 hover:border-white/20 transition-all duration-300',
                    passwordsMismatch || (fieldErrors.password_confirm && !passwordsMismatch)
                      ? 'border-red-500/50 focus:border-red-400'
                      : 'border-white/10'
                  ]"
                  @focus="focusPasswordConfirm = true"
                  @blur="focusPasswordConfirm = false"
                />
                <label
                  for="signup-password-confirm"
                  class="floating-label cosmic-floating-label"
                  :class="{ 'floating-label--active': form.password_confirm || focusPasswordConfirm }"
                >
                  Confirm password
                </label>
                <button
                  type="button"
                  @click="showPasswordConfirm = !showPasswordConfirm"
                  class="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-500 hover:text-cyan-400 focus:outline-none transition-colors duration-300 cosmic-icon-wrap"
                  tabindex="-1"
                  :aria-label="showPasswordConfirm ? 'Hide password' : 'Show password'"
                >
                  <EyeIcon v-if="!showPasswordConfirm" class="h-5 w-5 cosmic-icon" />
                  <EyeSlashIcon v-else class="h-5 w-5 cosmic-icon" />
                </button>
              </div>
              <transition
                enter-active-class="transition-all duration-200 ease-out"
                enter-from-class="opacity-0"
                enter-to-class="opacity-100"
                leave-active-class="transition-all duration-150"
                leave-from-class="opacity-100"
                leave-to-class="opacity-0"
              >
                <p v-if="passwordsMismatch" class="mt-1.5 text-xs text-red-400 flex items-center gap-1">
                  <ExclamationCircleIcon class="h-4 w-4 flex-shrink-0" />
                  Passwords do not match
                </p>
              </transition>
              <p v-if="fieldErrors.password_confirm && !passwordsMismatch" class="mt-1.5 text-xs text-red-400">{{ fieldErrorMsg('password_confirm') }}</p>
            </div>

            <!-- Submit -->
            <div class="pt-2">
              <button
                type="submit"
                :disabled="loading || passwordsMismatch"
                class="cosmic-btn auth-btn w-full py-3.5 px-4 rounded-xl font-semibold text-white text-base bg-indigo-600 hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-[#0B0E14] disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:bg-indigo-600 transition-all duration-300 flex items-center justify-center gap-2 min-h-[52px] shadow-lg hover:shadow-indigo-500/40 hover:shadow-xl active:scale-95"
              >
                <template v-if="loading">
                  <svg
                    class="animate-spin h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span>Creating account…</span>
                </template>
                <template v-else>
                  <span>Create account</span>
                  <ArrowRightIcon class="h-5 w-5" />
                </template>
              </button>
            </div>
          </form>

          <!-- Already have an account: Sign in -->
          <div class="mt-8 pt-6 border-t border-white/10">
            <p class="text-center text-sm text-slate-400 mb-3">Already have an account?</p>
            <router-link
              to="/login"
              class="cosmic-secondary-link inline-flex items-center justify-center gap-2 w-full sm:w-auto px-5 py-2.5 rounded-xl border border-white/20 text-slate-300 font-medium text-sm hover:border-cyan-400/60 hover:text-cyan-400 hover:bg-cyan-400/10 focus:outline-none focus:ring-2 focus:ring-cyan-400/30 focus:ring-offset-2 focus:ring-offset-[#0B0E14] transition-all duration-300"
            >
              Sign in
            </router-link>
          </div>
        </div>
      </div>

      <!-- Back to home -->
      <router-link
        to="/"
        class="mt-6 flex items-center justify-center gap-2 text-sm text-slate-500 hover:text-slate-300 focus:outline-none focus:underline transition-colors duration-300"
      >
        <ArrowLeftIcon class="h-4 w-4" />
        Back to home
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import {
  EnvelopeIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const notify = useNotification()

const form = ref({
  email: '',
  password: '',
  password_confirm: '',
})
const loading = ref(false)
const error = ref('')
const fieldErrors = ref({})
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const focusEmail = ref(false)
const focusPassword = ref(false)
const focusPasswordConfirm = ref(false)

const passwordsMismatch = computed(() => {
  const p = form.value.password
  const c = form.value.password_confirm
  return p.length > 0 && c.length > 0 && p !== c
})

/** Password strength: 0–4 for progress bar and label */
function getPasswordStrength(password) {
  if (!password || password.length === 0) return 0
  let score = 0
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1
  if (/\d/.test(password)) score += 1
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  return Math.min(score, 4)
}

const passwordStrengthWidth = computed(() => {
  const s = getPasswordStrength(form.value.password)
  return s === 0 ? 0 : (s / 4) * 100
})

const passwordStrengthLabel = computed(() => {
  const s = getPasswordStrength(form.value.password)
  if (s === 0) return ''
  if (s === 1) return 'Weak'
  if (s === 2) return 'Fair'
  if (s === 3) return 'Good'
  return 'Strong'
})

const passwordStrengthClass = computed(() => {
  const s = getPasswordStrength(form.value.password)
  if (s <= 1) return 'bg-red-500/80'
  if (s === 2) return 'bg-amber-500/80'
  if (s === 3) return 'bg-emerald-500/80'
  return 'bg-emerald-400'
})

const passwordStrengthTextClass = computed(() => {
  const s = getPasswordStrength(form.value.password)
  if (s <= 1) return 'text-red-400'
  if (s === 2) return 'text-amber-400'
  return 'text-slate-400'
})

function fieldErrorMsg(field) {
  const v = fieldErrors.value[field]
  if (!v) return ''
  return Array.isArray(v) ? v[0] : String(v)
}

function setError(msg) {
  error.value = msg
  fieldErrors.value = {}
}

function setFieldErrors(errors) {
  fieldErrors.value = typeof errors === 'object' && errors !== null ? errors : {}
  const first = Object.values(fieldErrors.value).flat().find(Boolean)
  error.value = Array.isArray(first) ? first[0] : first || ''
}

async function handleSignup() {
  if (form.value.password !== form.value.password_confirm) {
    setError('Passwords do not match.')
    return
  }
  if (form.value.password.length < 8) {
    setFieldErrors({ password: 'Password must be at least 8 characters.' })
    return
  }

  loading.value = true
  setError('')
  setFieldErrors({})

  try {
    const email = form.value.email.trim().toLowerCase()
    const userData = {
      username: email,
      email,
      password: form.value.password,
      password_confirm: form.value.password_confirm,
    }

    const response = await authAPI.signup(userData)

    if (response.data?.tokens) {
      authStore.token = response.data.tokens.access
      authStore.refreshToken = response.data.tokens.refresh
      localStorage.setItem('auth_token', authStore.token)
      localStorage.setItem('refresh_token', authStore.refreshToken)
      authStore.isAuthenticated = true
      if (response.data.user) {
        authStore.user = response.data.user
      }
    }

    notify.success('Account created successfully!')
    router.push('/dashboard')
  } catch (err) {
    const data = err.response?.data
    if (data && typeof data === 'object') {
      const firstMessage = data.detail || data.message || data.error
      if (firstMessage && typeof firstMessage === 'string') {
        setError(firstMessage)
      } else {
        setFieldErrors(data)
        const first = Object.values(data).flat().find(Boolean)
        if (Array.isArray(first)) setError(first[0])
        else if (typeof first === 'string') setError(first)
        else setError('Failed to create account. Please check the form.')
      }
    } else {
      setError(err.message || 'Failed to create account.')
    }
    notify.error(error.value || 'Sign up failed.')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  position: relative;
  font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Deep space gradient */
.cosmic-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(to bottom right, #0B0E14, #161B22, #0B0E14);
  pointer-events: none;
}

/* Animated starfield */
.cosmic-starfield {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: 0.6;
  animation: cosmicTwinkle 6s ease-in-out infinite;
}

.cosmic-starfield::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(1.5px 1.5px at 15% 25%, rgba(255,255,255,0.9), transparent),
    radial-gradient(1px 1px at 25% 15%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1.5px 1.5px at 75% 30%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 85% 20%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 10% 60%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 30% 70%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1.5px 1.5px at 60% 80%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 80% 55%, rgba(255,255,255,0.9), transparent),
    radial-gradient(1.5px 1.5px at 45% 35%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1px 1px at 55% 45%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1.5px 1.5px at 20% 85%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 90% 75%, rgba(255,255,255,0.5), transparent),
    radial-gradient(1.5px 1.5px at 5% 40%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 95% 50%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1.5px 1.5px at 40% 10%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 70% 65%, rgba(255,255,255,0.8), transparent);
  background-size: 100% 100%;
  background-repeat: repeat;
}

@keyframes cosmicTwinkle {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.9; }
}

/* Nebula accents */
.nebula {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 1;
  opacity: 0.25;
}
.nebula--indigo {
  width: 400px;
  height: 400px;
  background: rgba(99, 102, 241, 0.4);
  top: -100px;
  right: -100px;
}
.nebula--purple {
  width: 350px;
  height: 350px;
  background: rgba(139, 92, 246, 0.35);
  bottom: -80px;
  left: -80px;
}

/* Glass-portal card */
.glass-portal {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Galactic typography */
.cosmic-heading {
  letter-spacing: 0.05em;
  text-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

/* Input: dark sleek, power-up glow on focus */
.cosmic-input {
  border-color: rgba(255, 255, 255, 0.1);
}
.cosmic-input:focus {
  border-color: #6366F1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25), 0 0 20px rgba(99, 102, 241, 0.15);
}

/* Neon icon glow */
.cosmic-icon {
  filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4));
}
.group-focus-within .cosmic-icon {
  filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.6));
}

/* Primary button: Electric Indigo + Cyan accent */
.cosmic-btn {
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  box-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
}
.cosmic-btn:hover:not(:disabled) {
  box-shadow: 0 8px 30px rgba(99, 102, 241, 0.45), 0 0 40px rgba(34, 211, 238, 0.15);
}
.cosmic-btn:focus:not(:disabled) {
  box-shadow: 0 0 0 2px #0B0E14, 0 0 0 4px rgba(99, 102, 241, 0.5), 0 0 30px rgba(99, 102, 241, 0.3);
}

/* Floating label (cosmic): when active, label sits above input so it never overlaps typed text */
.cosmic-floating-label {
  color: rgb(148 163 184);
}
.floating-label--active.cosmic-floating-label {
  color: rgb(148 163 184);
}
.input-wrap {
  position: relative;
}
.input-wrap .input-group {
  margin-top: 1.5rem;
}
.floating-label {
  position: absolute;
  left: 2.75rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  pointer-events: none;
  transition: transform 0.2s ease, font-size 0.2s ease, color 0.2s ease, top 0.2s ease;
}
.floating-label--active {
  top: -1.5rem;
  transform: translateY(0);
  font-size: 0.75rem;
  font-weight: 500;
}
</style>
