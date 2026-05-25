<template>
  <AuthPageLayout
    variant="reset"
    eyebrow="Set new password"
    heading="Create a new password"
    subtitle="Use at least 8 characters. Mix letters, numbers, and symbols for a stronger password."
    mobile-title="New password"
    mobile-subtitle="Complete your reset"
    brand-copy="Reset links expire after a short time. If this page fails, request a fresh link from the login screen."
    back-link-label="Back to login"
    back-link-to="/login"
  >
    <form v-if="!success" class="auth-form-stack" @submit.prevent="submit">
      <div v-if="!hasToken" class="auth-alert rounded-xl px-4 py-3 text-sm flex items-start gap-2" role="alert">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <span>Invalid or expired reset link. Request a new one below.</span>
      </div>

      <div v-else class="auth-email-chip">
        <div class="auth-email-chip__icon" aria-hidden="true">
          <KeyIcon class="w-5 h-5" />
        </div>
        <div>
          <p class="auth-email-chip__label">Reset link</p>
          <p class="auth-email-chip__value">Verified — choose your new password</p>
        </div>
      </div>

      <div v-if="error" class="auth-alert rounded-xl px-4 py-3 text-sm flex items-start gap-2" role="alert">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <span>{{ error }}</span>
      </div>

      <div>
        <label for="reset-pw" class="auth-subtitle block text-sm font-medium mb-2">New password</label>
        <div class="auth-password-field">
          <input
            id="reset-pw"
            v-model="pw"
            :type="showPassword ? 'text' : 'password'"
            required
            minlength="8"
            autocomplete="new-password"
            class="auth-input cosmic-input w-full pl-4 pr-12 py-3 rounded-xl"
            placeholder="At least 8 characters"
          />
          <button
            type="button"
            class="auth-password-toggle"
            :aria-label="showPassword ? 'Hide password' : 'Show password'"
            tabindex="-1"
            @click="showPassword = !showPassword"
          >
            <EyeIcon v-if="!showPassword" class="w-5 h-5" />
            <EyeSlashIcon v-else class="w-5 h-5" />
          </button>
        </div>
        <div v-if="pw.length > 0" class="auth-strength">
          <div class="auth-strength__track">
            <div
              class="auth-strength__bar"
              :class="passwordStrengthBarClass"
              :style="{ width: passwordStrengthWidth + '%' }"
            />
          </div>
          <p v-if="passwordStrengthLabel" class="auth-strength__label" :class="passwordStrengthTextClass">
            Strength: {{ passwordStrengthLabel }}
          </p>
        </div>
      </div>

      <div>
        <label for="reset-pw2" class="auth-subtitle block text-sm font-medium mb-2">Confirm password</label>
        <div class="auth-password-field">
          <input
            id="reset-pw2"
            v-model="pw2"
            :type="showPasswordConfirm ? 'text' : 'password'"
            required
            autocomplete="new-password"
            class="auth-input cosmic-input w-full pl-4 pr-12 py-3 rounded-xl"
            :class="{ 'border-red-400/60': passwordsMismatch }"
            placeholder="Repeat password"
          />
          <button
            type="button"
            class="auth-password-toggle"
            :aria-label="showPasswordConfirm ? 'Hide password' : 'Show password'"
            tabindex="-1"
            @click="showPasswordConfirm = !showPasswordConfirm"
          >
            <EyeIcon v-if="!showPasswordConfirm" class="w-5 h-5" />
            <EyeSlashIcon v-else class="w-5 h-5" />
          </button>
        </div>
        <p v-if="passwordsMismatch" class="text-xs text-red-500 mt-1.5">Passwords do not match.</p>
      </div>

      <button
        type="submit"
        class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 min-h-[48px]"
        :class="{ 'auth-btn--loading': loading }"
        :disabled="loading || !hasToken || passwordsMismatch || pw.length < 8"
      >
        <span v-if="loading" class="auth-spinner" aria-hidden="true" />
        <span>{{ loading ? 'Saving…' : 'Update password' }}</span>
        <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
      </button>

      <p class="text-center text-sm">
        <router-link to="/forgot-password" class="auth-inline-link font-medium">Request a new reset link</router-link>
      </p>
    </form>

    <div v-else class="auth-form-stack">
      <div class="auth-success rounded-xl px-4 py-4 text-sm flex items-start gap-3">
        <CheckCircleIcon class="w-6 h-6 flex-shrink-0" />
        <div>
          <p class="font-semibold text-base mb-1">Password updated</p>
          <p class="opacity-90">You can now sign in with your new password.</p>
        </div>
      </div>

      <router-link
        to="/login"
        class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold inline-flex items-center justify-center gap-2 min-h-[48px]"
      >
        Sign in
        <ArrowRightIcon class="w-5 h-5" />
      </router-link>
    </div>
  </AuthPageLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowRightIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  EyeIcon,
  EyeSlashIcon,
  KeyIcon,
} from '@heroicons/vue/24/outline'
import AuthPageLayout from '@/components/auth/AuthPageLayout.vue'
import { authAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const route = useRoute()
const uid = ref('')
const token = ref('')
const pw = ref('')
const pw2 = ref('')
const showPassword = ref(false)
const showPasswordConfirm = ref(false)
const loading = ref(false)
const error = ref('')
const success = ref(false)

const hasToken = computed(() => Boolean(uid.value && token.value))

const passwordsMismatch = computed(() => {
  return pw.value.length > 0 && pw2.value.length > 0 && pw.value !== pw2.value
})

function getPasswordStrength(password) {
  if (!password) return 0
  let score = 0
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1
  if (/\d/.test(password)) score += 1
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  return Math.min(score, 4)
}

const passwordStrengthWidth = computed(() => {
  const s = getPasswordStrength(pw.value)
  return s === 0 ? 0 : (s / 4) * 100
})

const passwordStrengthLabel = computed(() => {
  const s = getPasswordStrength(pw.value)
  if (s === 0) return ''
  if (s === 1) return 'Weak'
  if (s === 2) return 'Fair'
  if (s === 3) return 'Good'
  return 'Strong'
})

const passwordStrengthBarClass = computed(() => {
  const s = getPasswordStrength(pw.value)
  if (s <= 1) return 'bg-red-500/80'
  if (s === 2) return 'bg-amber-500/80'
  if (s === 3) return 'bg-emerald-500/80'
  return 'bg-emerald-400'
})

const passwordStrengthTextClass = computed(() => {
  const s = getPasswordStrength(pw.value)
  if (s <= 1) return 'text-red-500'
  if (s === 2) return 'text-amber-500'
  return 'text-emerald-600'
})

onMounted(() => {
  uid.value = String(route.query.uid || '')
  token.value = String(route.query.token || '')
})

async function submit() {
  error.value = ''
  if (pw.value !== pw2.value) {
    error.value = 'Passwords do not match.'
    return
  }
  if (pw.value.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  loading.value = true
  try {
    await authAPI.passwordResetConfirm({
      uid: uid.value,
      token: token.value,
      new_password: pw.value,
      new_password_confirm: pw2.value,
    })
    success.value = true
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Reset failed. The link may have expired.'
  } finally {
    loading.value = false
  }
}
</script>
