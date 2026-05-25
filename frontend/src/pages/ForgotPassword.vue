<template>
  <AuthPageLayout
    variant="forgot"
    eyebrow="Account recovery"
    heading="Forgot password?"
    subtitle="Enter your email address. If an account exists, we will send a secure reset link."
    mobile-title="Reset password"
    mobile-subtitle="We'll email you a secure link"
    brand-copy="Password reset uses the same SMTP system as verification emails — configure it in Super Admin → Communications."
    back-link-label="Back to login"
  >
    <form v-if="!sent" class="auth-form-stack" @submit.prevent="submit">
      <div v-if="error" class="auth-alert rounded-xl px-4 py-3 text-sm flex items-start gap-2" role="alert">
        <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <span>{{ error }}</span>
      </div>

      <div>
        <label for="forgot-email" class="auth-subtitle block text-sm font-medium mb-2">Email address</label>
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-[var(--auth-input-icon)]">
            <EnvelopeIcon class="w-5 h-5" />
          </div>
          <input
            id="forgot-email"
            v-model="email"
            type="email"
            required
            autocomplete="email"
            class="auth-input cosmic-input w-full pl-11 pr-4 py-3 rounded-xl"
            placeholder="you@company.com"
          />
        </div>
      </div>

      <p class="auth-helper text-xs leading-relaxed">
        For security, we show the same message whether or not the email is registered.
      </p>

      <button
        type="submit"
        class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 min-h-[48px]"
        :class="{ 'auth-btn--loading': loading }"
        :disabled="loading || !email.trim()"
      >
        <span v-if="loading" class="auth-spinner" aria-hidden="true" />
        <span>{{ loading ? 'Sending…' : 'Send reset link' }}</span>
        <PaperAirplaneIcon v-if="!loading" class="w-5 h-5" />
      </button>
    </form>

    <div v-else class="auth-form-stack">
      <div class="auth-success rounded-xl px-4 py-4 text-sm flex items-start gap-3">
        <CheckCircleIcon class="w-6 h-6 flex-shrink-0" />
        <div>
          <p class="font-semibold text-base mb-1">Check your email</p>
          <p class="opacity-90 leading-relaxed">{{ message }}</p>
        </div>
      </div>

      <div v-if="email.trim()" class="auth-email-chip">
        <div class="auth-email-chip__icon" aria-hidden="true">
          <EnvelopeIcon class="w-5 h-5" />
        </div>
        <div class="min-w-0">
          <p class="auth-email-chip__label">Sent to</p>
          <p class="auth-email-chip__value">{{ email.trim().toLowerCase() }}</p>
        </div>
      </div>

      <p class="auth-helper text-xs">
        Didn't receive it? Check spam, promotions, or wait a few minutes.
      </p>

      <button type="button" class="auth-secondary-link w-full py-3 rounded-xl text-sm font-medium" @click="resetForm">
        Try another email
      </button>

      <router-link
        to="/login"
        class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold inline-flex items-center justify-center gap-2"
      >
        Back to login
        <ArrowRightIcon class="w-5 h-5" />
      </router-link>
    </div>
  </AuthPageLayout>
</template>

<script setup>
import { ref } from 'vue'
import {
  ArrowRightIcon,
  CheckCircleIcon,
  EnvelopeIcon,
  ExclamationCircleIcon,
  PaperAirplaneIcon,
} from '@heroicons/vue/24/outline'
import AuthPageLayout from '@/components/auth/AuthPageLayout.vue'
import { authAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'

const email = ref('')
const loading = ref(false)
const sent = ref(false)
const error = ref('')
const message = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  const addr = email.value.trim().toLowerCase()
  try {
    const { data } = await authAPI.passwordResetRequest({ email: addr })
    message.value =
      data?.message || 'If an account exists for that email, password reset instructions have been sent.'
    sent.value = true
  } catch (e) {
    const norm = normalizeApiError(e)
    message.value =
      norm.userMessage ||
      'If an account exists for that email, password reset instructions have been sent.'
    sent.value = true
  } finally {
    loading.value = false
  }
}

function resetForm() {
  sent.value = false
  message.value = ''
  error.value = ''
}
</script>
