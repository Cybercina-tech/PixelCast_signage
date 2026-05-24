<template>
  <div class="auth-page cosmic-auth min-h-screen flex" :class="{ 'theme-light': !themeStore.isDarkMode }">
    <!-- Deep space gradient base -->
    <div class="cosmic-bg" aria-hidden="true" />

    <!-- Animated starfield (CSS-only twinkling stars) -->
    <div class="cosmic-starfield" aria-hidden="true" />

    <!-- Nebula accents (blurred glow in corners) -->
    <div class="nebula nebula--indigo" aria-hidden="true" />
    <div class="nebula nebula--purple" aria-hidden="true" />
    <div class="absolute top-4 right-4 z-20">
      <ThemeToggle />
    </div>

    <!-- Left: Brand (visible on lg+) -->
    <div
      class="hidden lg:flex lg:w-1/2 xl:w-[55%] flex-col justify-center px-12 xl:px-20 py-16 relative z-10"
    >
      <div
        v-motion
        :initial="{ opacity: 0, x: -24 }"
        :enter="{ opacity: 1, x: 0 }"
        :transition="{ duration: 500 }"
        class="max-w-md"
      >
        <div class="cosmic-icon-wrap auth-brand-mark inline-flex items-center justify-center w-14 h-14 rounded-xl mb-8">
          <svg class="w-7 h-7 cosmic-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h1 class="cosmic-title auth-title text-3xl xl:text-4xl font-bold tracking-wide mb-3">
          PixelCast Signage
        </h1>
        <p class="auth-copy text-lg leading-relaxed">
          Secure digital signage management. Sign in to manage screens, content, and schedules.
        </p>
        <div class="auth-preview-card mt-12 rounded-2xl p-8">
          <div class="flex items-center gap-4">
            <div class="auth-preview-track-muted flex-1 h-2 rounded-full" />
            <div class="auth-preview-track-active flex-1 h-2 rounded-full" />
            <div class="auth-preview-track-muted flex-1 h-2 rounded-full" />
          </div>
          <div class="mt-4 flex gap-3">
            <div class="auth-preview-chip-muted w-16 h-12 rounded-xl" />
            <div class="auth-preview-chip-active w-20 h-12 rounded-xl" />
            <div class="auth-preview-chip-muted w-14 h-12 rounded-xl" />
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Form -->
    <div class="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center px-4 sm:px-6 py-12 lg:py-16 relative z-10">
      <div
        v-motion
        :initial="{ opacity: 0, y: 16 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 400 }"
        class="w-full max-w-md"
      >
        <div class="lg:hidden text-center mb-8">
          <h1 class="cosmic-title auth-title text-2xl font-bold">PixelCast Signage</h1>
          <p class="auth-subtitle text-sm mt-1">Sign in to your account</p>
        </div>

        <!-- Glass-portal card -->
        <div class="glass-portal rounded-2xl overflow-hidden">
          <div class="px-6 sm:px-8 py-8 sm:py-10">
            <h2 class="cosmic-heading auth-heading text-xl font-bold mb-1">
              {{ needs2fa ? 'Two-factor authentication' : 'Welcome back' }}
            </h2>
            <p class="auth-subtitle text-sm mb-6">
              {{
                needs2fa
                  ? 'Enter the 6-digit code from your authenticator app or a backup code.'
                  : 'Enter your credentials to continue'
              }}
            </p>

            <form v-if="!needs2fa" @submit.prevent="handleLogin" class="space-y-5">
              <!-- Error -->
              <transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 -translate-y-1"
                enter-to-class="opacity-100 translate-y-0"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 translate-y-0"
                leave-to-class="opacity-0 -translate-y-1"
              >
                <div
                  v-if="authStore.error"
                  class="auth-alert rounded-xl px-4 py-3 text-sm flex items-start gap-2"
                  role="alert"
                >
                  <ExclamationCircleIcon class="auth-alert-icon h-5 w-5 flex-shrink-0 mt-0.5 cosmic-icon" />
                  <span class="flex-1">{{ authStore.error }}</span>
                </div>
              </transition>

              <!-- Username / Email (floating label) -->
              <div class="input-wrap">
                <div class="input-group relative group">
                  <div class="auth-input-icon absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors duration-300 cosmic-icon-wrap">
                    <UserIcon class="h-5 w-5 cosmic-icon" />
                  </div>
                  <input
                    id="login-username"
                    v-model="form.username"
                    type="text"
                    required
                    autocomplete="username"
                    class="auth-input cosmic-input w-full pl-11 pr-4 py-3 rounded-xl placeholder-transparent transition-all duration-300"
                    placeholder=" "
                    @focus="focusUsername = true"
                    @blur="focusUsername = false"
                  />
                  <label
                    for="login-username"
                    class="floating-label cosmic-floating-label auth-floating-label"
                    :class="{ 'floating-label--active': form.username || focusUsername }"
                  >
                    Username or Email
                  </label>
                </div>
              </div>

              <!-- Password (floating label) -->
              <div class="input-wrap">
                <div class="input-group relative group">
                  <div class="auth-input-icon absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none transition-colors duration-300 cosmic-icon-wrap">
                    <LockClosedIcon class="h-5 w-5 cosmic-icon" />
                  </div>
                  <input
                    id="login-password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    required
                    autocomplete="current-password"
                    class="auth-input cosmic-input w-full pl-11 pr-12 py-3 rounded-xl placeholder-transparent transition-all duration-300"
                    placeholder=" "
                    @focus="focusPassword = true"
                    @blur="focusPassword = false"
                  />
                  <label
                    for="login-password"
                    class="floating-label cosmic-floating-label auth-floating-label"
                    :class="{ 'floating-label--active': form.password || focusPassword }"
                  >
                    Password
                  </label>
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="auth-password-toggle absolute inset-y-0 right-0 pr-4 flex items-center focus:outline-none transition-colors duration-300 cosmic-icon-wrap"
                    tabindex="-1"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                  >
                    <EyeIcon v-if="!showPassword" class="h-5 w-5 cosmic-icon" />
                    <EyeSlashIcon v-else class="h-5 w-5 cosmic-icon" />
                  </button>
                </div>
              </div>

              <!-- Submit -->
              <div class="pt-1">
                <button
                  type="submit"
                  :disabled="authStore.loading"
                  class="cosmic-btn auth-btn w-full py-3.5 px-4 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2 min-h-[48px]"
                >
                  <template v-if="authStore.loading">
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
                    <span>Signing in…</span>
                  </template>
                  <template v-else>
                    <span>Sign in</span>
                    <ArrowRightIcon class="h-5 w-5" />
                  </template>
                </button>
              </div>

              <p class="text-right text-xs">
                <router-link to="/forgot-password" class="auth-inline-link">
                  Forgot password?
                </router-link>
              </p>
            </form>

            <form v-else @submit.prevent="handle2fa" class="space-y-5">
              <div class="input-wrap">
                <label class="auth-subtitle block text-sm mb-2">Authenticator code</label>
                <input
                  v-model="code2fa"
                  type="text"
                  inputmode="numeric"
                  autocomplete="one-time-code"
                  maxlength="12"
                  class="auth-input cosmic-input w-full px-4 py-3 rounded-xl"
                  placeholder="123456"
                />
              </div>
              <button
                type="submit"
                :disabled="authStore.loading"
                class="cosmic-btn auth-btn w-full py-3.5 px-4 rounded-xl font-semibold disabled:opacity-60"
              >
                {{ authStore.loading ? 'Verifying…' : 'Verify & continue' }}
              </button>
              <button type="button" class="auth-text-link text-sm" @click="cancel2fa">
                Back to login
              </button>
            </form>

            <!-- Secondary action: Sign up -->
            <div class="mt-6 text-center">
              <p class="auth-subtitle text-sm mb-3">Don't have an account?</p>
              <router-link
                to="/signup"
                class="cosmic-secondary-link auth-secondary-link inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-300"
              >
                Sign up
              </router-link>
            </div>
          </div>
        </div>

        <router-link
          to="/"
          class="auth-back-link mt-6 flex items-center justify-center gap-2 text-sm focus:outline-none focus:underline transition-colors duration-300"
        >
          <ArrowLeftIcon class="h-4 w-4" />
          Back to home
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useNotification } from '@/composables/useNotification'
import { normalizeApiError } from '@/utils/apiError'
import { pushLogin } from '@/analytics/dataLayer'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import {
  UserIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowRightIcon,
  ArrowLeftIcon,
  ExclamationCircleIcon,
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const notify = useNotification()

const form = ref({
  username: '',
  password: '',
})
const showPassword = ref(false)
const focusUsername = ref(false)
const focusPassword = ref(false)
const needs2fa = ref(false)
const twoFactorToken = ref('')
const code2fa = ref('')

async function handleLogin() {
  try {
    authStore.error = null
    const credentials = {
      username: form.value.username.trim().toLowerCase(),
      password: form.value.password,
    }
    const result = await authStore.login(credentials)
    if (result?.needs2fa) {
      needs2fa.value = true
      twoFactorToken.value = result.twoFactorToken
      return
    }
    notify.success('Login successful!')
    pushLogin('password')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    const parsed = error.apiError || normalizeApiError(error)
    authStore.error = parsed.userMessage || 'Login failed. Please check your credentials.'
    // Inline alert above the form is enough; avoid duplicate toasts (interceptor + here).
  }
}

async function handle2fa() {
  try {
    authStore.error = null
    await authStore.complete2fa({
      twoFactorToken: twoFactorToken.value,
      code: code2fa.value,
    })
    notify.success('Login successful!')
    pushLogin('2fa')
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (error) {
    const parsed = error.apiError || normalizeApiError(error)
    authStore.error = parsed.userMessage || 'Invalid code.'
  }
}

function cancel2fa() {
  needs2fa.value = false
  twoFactorToken.value = ''
  code2fa.value = ''
  authStore.error = null
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push(route.query.redirect || '/dashboard')
  }
})
</script>

<style scoped>
.auth-page {
  position: relative;
  font-family: 'Plus Jakarta Sans', sans-serif;
  --auth-bg-start: #0b0e14;
  --auth-bg-mid: #161b22;
  --auth-bg-end: #0b0e14;
  --auth-star-opacity: 0.6;
  --auth-nebula-opacity: 0.25;
  --auth-text-primary: #f8fafc;
  --auth-text-secondary: #94a3b8;
  --auth-text-tertiary: #64748b;
  --auth-card-bg: rgba(255, 255, 255, 0.05);
  --auth-card-border: rgba(255, 255, 255, 0.1);
  --auth-card-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  --auth-brand-mark-bg: rgba(255, 255, 255, 0.05);
  --auth-brand-mark-border: rgba(255, 255, 255, 0.1);
  --auth-brand-mark-color: #818cf8;
  --auth-preview-muted: rgba(255, 255, 255, 0.18);
  --auth-preview-active: rgba(99, 102, 241, 0.38);
  --auth-input-bg: rgba(2, 6, 23, 0.5);
  --auth-input-border: rgba(255, 255, 255, 0.12);
  --auth-input-border-hover: rgba(255, 255, 255, 0.22);
  --auth-input-border-focus: #6366f1;
  --auth-input-text: #f8fafc;
  --auth-input-placeholder: #94a3b8;
  --auth-input-icon: #64748b;
  --auth-input-icon-focus: #818cf8;
  --auth-focus-ring: rgba(99, 102, 241, 0.28);
  --auth-focus-offset: #0b0e14;
  --auth-link: #818cf8;
  --auth-link-hover: #a5b4fc;
  --auth-secondary-bg: rgba(34, 211, 238, 0.08);
  --auth-secondary-border: rgba(255, 255, 255, 0.22);
  --auth-secondary-border-hover: rgba(34, 211, 238, 0.55);
  --auth-secondary-text: #cbd5e1;
  --auth-secondary-text-hover: #22d3ee;
  --auth-btn-bg: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
  --auth-btn-shadow: 0 4px 20px rgba(99, 102, 241, 0.35);
  --auth-btn-shadow-hover: 0 10px 30px rgba(99, 102, 241, 0.45);
  --auth-label-bg: rgba(11, 14, 20, 0.92);
  --auth-label-text: #94a3b8;
  --auth-label-active: #a5b4fc;
  --auth-alert-border: rgba(239, 68, 68, 0.35);
  --auth-alert-bg: rgba(239, 68, 68, 0.12);
  --auth-alert-text: #fca5a5;
  --auth-autofill-bg: rgba(2, 6, 23, 0.56);
}

.theme-light {
  color-scheme: light;
  --auth-bg-start: #f8fafc;
  --auth-bg-mid: #eef2ff;
  --auth-bg-end: #e2e8f0;
  --auth-star-opacity: 0.22;
  --auth-nebula-opacity: 0.16;
  --auth-text-primary: #0f172a;
  --auth-text-secondary: #475569;
  --auth-text-tertiary: #64748b;
  --auth-card-bg: rgba(255, 255, 255, 0.9);
  --auth-card-border: rgba(148, 163, 184, 0.32);
  --auth-card-shadow: 0 18px 40px rgba(15, 23, 42, 0.14);
  --auth-brand-mark-bg: linear-gradient(140deg, #dbeafe 0%, #bfdbfe 45%, #ddd6fe 100%);
  --auth-brand-mark-border: rgba(99, 102, 241, 0.28);
  --auth-brand-mark-color: #1d4ed8;
  --auth-preview-muted: rgba(148, 163, 184, 0.35);
  --auth-preview-active: rgba(79, 70, 229, 0.32);
  --auth-input-bg: rgba(255, 255, 255, 0.96);
  --auth-input-border: rgba(148, 163, 184, 0.48);
  --auth-input-border-hover: rgba(100, 116, 139, 0.62);
  --auth-input-border-focus: #2563eb;
  --auth-input-text: #0f172a;
  --auth-input-placeholder: #94a3b8;
  --auth-input-icon: #64748b;
  --auth-input-icon-focus: #2563eb;
  --auth-focus-ring: rgba(37, 99, 235, 0.24);
  --auth-focus-offset: #ffffff;
  --auth-link: #2563eb;
  --auth-link-hover: #1d4ed8;
  --auth-secondary-bg: rgba(37, 99, 235, 0.07);
  --auth-secondary-border: rgba(148, 163, 184, 0.38);
  --auth-secondary-border-hover: rgba(37, 99, 235, 0.42);
  --auth-secondary-text: #334155;
  --auth-secondary-text-hover: #1d4ed8;
  --auth-btn-bg: linear-gradient(135deg, #2563eb 0%, #4338ca 100%);
  --auth-btn-shadow: 0 8px 22px rgba(37, 99, 235, 0.24);
  --auth-btn-shadow-hover: 0 14px 30px rgba(37, 99, 235, 0.28);
  --auth-label-bg: rgba(255, 255, 255, 0.98);
  --auth-label-text: #64748b;
  --auth-label-active: #1d4ed8;
  --auth-alert-border: rgba(239, 68, 68, 0.26);
  --auth-alert-bg: rgba(254, 242, 242, 0.92);
  --auth-alert-text: #b91c1c;
  --auth-autofill-bg: rgba(255, 255, 255, 0.98);
}

/* Deep space gradient */
.cosmic-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background: linear-gradient(135deg, var(--auth-bg-start) 0%, var(--auth-bg-mid) 42%, var(--auth-bg-end) 100%);
  pointer-events: none;
}

/* Animated starfield (CSS-only twinkling stars via box-shadow) */
.cosmic-starfield {
  position: fixed;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  opacity: var(--auth-star-opacity);
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
  opacity: var(--auth-nebula-opacity);
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
  background: var(--auth-card-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--auth-card-border);
  box-shadow:
    var(--auth-card-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Galactic typography */
.cosmic-title,
.cosmic-heading {
  letter-spacing: 0.05em;
  text-shadow: 0 0 30px rgba(99, 102, 241, 0.2);
}

/* Neon icon glow */
.cosmic-icon {
  filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.4));
}
.group-focus-within .cosmic-icon {
  filter: drop-shadow(0 0 6px rgba(99, 102, 241, 0.6));
}

.auth-title,
.auth-heading {
  color: var(--auth-text-primary);
}

.auth-copy,
.auth-subtitle,
.auth-helper,
.auth-back-link {
  color: var(--auth-text-secondary);
}

.auth-brand-mark {
  background: var(--auth-brand-mark-bg);
  border: 1px solid var(--auth-brand-mark-border);
  color: var(--auth-brand-mark-color);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.14);
}

.auth-preview-card {
  background: color-mix(in oklab, var(--auth-card-bg) 92%, transparent);
  border: 1px solid var(--auth-card-border);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
}

.auth-preview-track-muted,
.auth-preview-chip-muted {
  background: var(--auth-preview-muted);
}

.auth-preview-track-active,
.auth-preview-chip-active {
  background: var(--auth-preview-active);
}

.auth-alert {
  border: 1px solid var(--auth-alert-border);
  background: var(--auth-alert-bg);
  color: var(--auth-alert-text);
}

.auth-alert-icon {
  color: var(--auth-alert-text);
}

.input-wrap {
  position: relative;
}
.input-wrap .input-group {
  margin-top: 0;
}
.floating-label {
  position: absolute;
  left: 0.75rem;
  top: -0.55rem;
  transform: none;
  font-size: 0.72rem;
  font-weight: 600;
  pointer-events: none;
  transition: color 0.2s ease;
  z-index: 2;
  padding: 0 0.35rem;
  border-radius: 999px;
  background: var(--auth-label-bg);
  line-height: 1.2;
  color: var(--auth-label-text);
}
.floating-label--active {
  top: -0.55rem;
}

.floating-label--active.cosmic-floating-label {
  color: var(--auth-label-active);
}

.auth-input {
  border: 1px solid var(--auth-input-border);
  background: var(--auth-input-bg);
  color: var(--auth-input-text);
}

.auth-input:hover {
  border-color: var(--auth-input-border-hover);
}

.auth-input:focus {
  border-color: var(--auth-input-border-focus);
  box-shadow: 0 0 0 3px var(--auth-focus-ring);
  outline: none;
}

.auth-input::placeholder {
  color: var(--auth-input-placeholder);
}

.auth-input-icon {
  color: var(--auth-input-icon);
}

.group:focus-within .auth-input-icon {
  color: var(--auth-input-icon-focus);
}

.auth-password-toggle {
  color: var(--auth-input-icon);
}

.auth-password-toggle:hover {
  color: var(--auth-input-icon-focus);
}

.auth-btn {
  color: #ffffff;
  background: var(--auth-btn-bg);
  box-shadow: var(--auth-btn-shadow);
}

.auth-btn:hover:not(:disabled) {
  box-shadow: var(--auth-btn-shadow-hover);
  transform: translateY(-1px);
}

.auth-btn:focus-visible {
  outline: none;
  box-shadow: var(--auth-btn-shadow), 0 0 0 3px var(--auth-focus-ring);
}

.auth-inline-link {
  color: var(--auth-link);
}

.auth-inline-link:hover {
  color: var(--auth-link-hover);
}

.auth-secondary-link {
  border: 1px solid var(--auth-secondary-border);
  color: var(--auth-secondary-text);
  background: transparent;
}

.auth-secondary-link:hover {
  border-color: var(--auth-secondary-border-hover);
  color: var(--auth-secondary-text-hover);
  background: var(--auth-secondary-bg);
}

.auth-secondary-link:focus-visible,
.auth-back-link:focus-visible,
.auth-text-link:focus-visible,
.auth-inline-link:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--auth-focus-ring);
  border-radius: 0.6rem;
}

.auth-text-link {
  color: var(--auth-text-secondary);
}

.auth-text-link:hover,
.auth-back-link:hover {
  color: var(--auth-text-primary);
}

.cosmic-input:-webkit-autofill,
.cosmic-input:-webkit-autofill:hover,
.cosmic-input:-webkit-autofill:focus,
.cosmic-input:-webkit-autofill:active {
  -webkit-text-fill-color: var(--auth-input-text) !important;
  box-shadow: 0 0 0 1000px var(--auth-autofill-bg) inset !important;
  -webkit-box-shadow: 0 0 0 1000px var(--auth-autofill-bg) inset !important;
  caret-color: var(--auth-input-text) !important;
  transition: background-color 9999s ease-in-out 0s;
}
</style>
