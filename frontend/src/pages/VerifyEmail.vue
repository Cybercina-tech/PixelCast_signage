<template>
  <AuthPageLayout
    variant="verify"
    eyebrow="Security check"
    heading="Verify your email"
    :subtitle="stepSubtitle"
    mobile-title="Verify email"
    mobile-subtitle="Enter the code we sent you"
    brand-copy="We use your email for account security, password recovery, and important notifications."
    back-link-label="Back to login"
  >
    <form v-if="!show2faStep" class="verify-form" @submit.prevent="submitCode">
      <div v-if="initialSending" class="auth-inbox-status flex items-center gap-3 py-2">
        <span class="auth-spinner" aria-hidden="true" />
        <span class="auth-subtitle text-sm">Sending verification code…</span>
      </div>

      <template v-else>
        <div v-if="maskedEmail" class="auth-email-chip">
          <div class="auth-email-chip__icon" aria-hidden="true">
            <EnvelopeIcon class="w-5 h-5" />
          </div>
          <div class="min-w-0">
            <p class="auth-email-chip__label">Code sent to</p>
            <p class="auth-email-chip__value">{{ maskedEmail }}</p>
          </div>
        </div>

        <p v-if="info" class="auth-success rounded-xl px-4 py-3 text-sm flex items-start gap-2">
          <CheckCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{{ info }}</span>
        </p>

        <div v-if="error" class="auth-alert rounded-xl px-4 py-3 text-sm flex items-start gap-2" role="alert">
          <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0 mt-0.5" />
          <span>{{ error }}</span>
        </div>

        <div class="verify-form__otp">
          <label class="auth-subtitle block text-sm font-medium mb-3">Enter 6-digit code</label>
          <OtpCodeInput ref="otpRef" v-model="code" :disabled="loading" @complete="submitCode" />
          <p class="auth-helper text-xs mt-2">Tip: paste the full code from your email</p>
        </div>

        <button
          type="submit"
          class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold flex items-center justify-center gap-2 min-h-[48px]"
          :class="{ 'auth-btn--loading': loading }"
          :disabled="loading || code.length !== 6"
        >
          <span v-if="loading" class="auth-spinner" aria-hidden="true" />
          <span>{{ loading ? 'Verifying…' : 'Verify & continue' }}</span>
          <ArrowRightIcon v-if="!loading" class="w-5 h-5" />
        </button>

        <div class="auth-resend-bar">
          <span class="auth-resend-bar__hint">Didn't receive it?</span>
          <button
            type="button"
            class="auth-inline-link text-sm font-semibold"
            :disabled="resendDisabled"
            @click="sendCode"
          >
            {{ resendDisabled ? `Resend in ${resendCountdown}s` : 'Resend code' }}
          </button>
        </div>
      </template>
    </form>

    <form v-else-if="ENABLE_2FA" class="verify-form space-y-5" @submit.prevent="submit2fa">
      <div class="auth-email-chip">
        <div class="auth-email-chip__icon" aria-hidden="true">
          <ShieldCheckIcon class="w-5 h-5" />
        </div>
        <div>
          <p class="auth-email-chip__label">Next step</p>
          <p class="auth-email-chip__value">Two-factor authentication</p>
        </div>
      </div>

      <div v-if="error" class="auth-alert rounded-xl px-4 py-3 text-sm" role="alert">{{ error }}</div>

      <div>
        <label class="auth-subtitle block text-sm font-medium mb-2">Authenticator code</label>
        <input
          v-model="code2fa"
          type="text"
          inputmode="numeric"
          autocomplete="one-time-code"
          maxlength="12"
          class="auth-input cosmic-input w-full px-4 py-3 rounded-xl text-center text-lg font-semibold tracking-widest"
          placeholder="000000"
        />
      </div>

      <button
        type="submit"
        class="auth-btn w-full py-3.5 px-4 rounded-xl font-semibold flex items-center justify-center gap-2"
        :disabled="loading"
      >
        <span v-if="loading" class="auth-spinner" aria-hidden="true" />
        <span>{{ loading ? 'Verifying…' : 'Verify & sign in' }}</span>
      </button>
    </form>
  </AuthPageLayout>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowRightIcon,
  CheckCircleIcon,
  EnvelopeIcon,
  ExclamationCircleIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'
import AuthPageLayout from '@/components/auth/AuthPageLayout.vue'
import { ENABLE_2FA } from '@/config/features'
import OtpCodeInput from '@/components/auth/OtpCodeInput.vue'
import { useAuthStore } from '@/stores/auth'
import { authAPI, usersAPI } from '@/services/api'
import { normalizeApiError } from '@/utils/apiError'
import { useNotification } from '@/composables/useNotification'
import { pushLogin } from '@/analytics/dataLayer'
import {
  clearEmailVerificationSession,
  readEmailVerificationSession,
  storeEmailVerificationSession,
} from '@/utils/emailVerificationSession'

const RESEND_SECONDS = 60

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notify = useNotification()
const otpRef = ref(null)

const verificationToken = ref('')
const maskedEmail = ref('')
const authenticatedFlow = ref(false)
const initialSending = ref(true)
const code = ref('')
const code2fa = ref('')
const needs2fa = ref(false)
const twoFactorToken = ref('')
const loading = ref(false)
const sending = ref(false)
const error = ref('')
const info = ref('')
const resendCountdown = ref(0)
let resendTimer = null

const resendDisabled = computed(() => sending.value || resendCountdown.value > 0 || initialSending.value)
const show2faStep = computed(() => ENABLE_2FA && needs2fa.value)

const stepSubtitle = computed(() =>
  show2faStep.value
    ? 'Email verified. Enter your authenticator code to finish signing in.'
    : 'We sent a one-time code to your inbox. It expires in 10 minutes.'
)

function startResendCountdown(seconds = RESEND_SECONDS) {
  resendCountdown.value = seconds
  if (resendTimer) clearInterval(resendTimer)
  resendTimer = setInterval(() => {
    resendCountdown.value -= 1
    if (resendCountdown.value <= 0) {
      clearInterval(resendTimer)
      resendTimer = null
    }
  }, 1000)
}

async function sendCode() {
  if (resendDisabled.value) return
  sending.value = true
  error.value = ''
  try {
    if (authenticatedFlow.value) {
      await usersAPI.sendVerificationEmail()
      if (authStore.user?.email) maskedEmail.value = authStore.user.email
    } else {
      const { data } = await authAPI.emailVerificationSend({
        verification_token: verificationToken.value,
      })
      if (data?.email) maskedEmail.value = data.email
    }
    info.value = 'New code sent — check your inbox and spam folder.'
    startResendCountdown()
    await nextTick()
    otpRef.value?.focus()
  } catch (e) {
    const norm = normalizeApiError(e)
    error.value = norm.userMessage || norm.detail || 'Failed to send verification code.'
    if (e.response?.status === 429 && e.response?.data?.retry_after_seconds) {
      startResendCountdown(Number(e.response.data.retry_after_seconds) || RESEND_SECONDS)
    }
  } finally {
    sending.value = false
    initialSending.value = false
  }
}

function finishLogin() {
  clearEmailVerificationSession()
  notify.success('Email verified!')
  pushLogin('email_verification')
  const redirect = route.query.redirect || '/dashboard'
  router.push(typeof redirect === 'string' ? redirect : '/dashboard')
}

async function submitCode() {
  if (code.value.length !== 6) {
    error.value = 'Enter the full 6-digit code from your email.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    if (authenticatedFlow.value) {
      await usersAPI.verifyEmail({ code: code.value })
      await authStore.fetchMe()
      finishLogin()
      return
    }

    const result = await authStore.completeEmailVerification({
      verificationToken: verificationToken.value,
      code: code.value,
    })
    if (result?.needs2fa && ENABLE_2FA) {
      needs2fa.value = true
      twoFactorToken.value = result.twoFactorToken
      info.value = ''
      return
    }
    finishLogin(result)
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Invalid or expired code. Request a new code below.'
    code.value = ''
    await nextTick()
    otpRef.value?.focus()
  } finally {
    loading.value = false
  }
}

async function submit2fa() {
  loading.value = true
  error.value = ''
  try {
    await authStore.complete2fa({
      twoFactorToken: twoFactorToken.value,
      code: code2fa.value,
    })
    clearEmailVerificationSession()
    notify.success('Login successful!')
    pushLogin('2fa')
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    error.value = normalizeApiError(e).userMessage || 'Invalid code.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const session = readEmailVerificationSession()
  verificationToken.value = (route.query.token || session.token || '').trim()
  maskedEmail.value = (route.query.email || session.email || '').trim()

  if (
    !verificationToken.value &&
    authStore.isAuthenticated &&
    authStore.user &&
    !authStore.user.is_email_verified
  ) {
    authenticatedFlow.value = true
    maskedEmail.value = authStore.user.email || maskedEmail.value
    await sendCode()
    await nextTick()
    otpRef.value?.focus()
    return
  }

  if (!verificationToken.value) {
    router.replace({ name: 'login' })
    return
  }

  storeEmailVerificationSession(verificationToken.value, maskedEmail.value)
  await sendCode()
  await nextTick()
  otpRef.value?.focus()
})

onBeforeUnmount(() => {
  if (resendTimer) clearInterval(resendTimer)
})
</script>

<style scoped>
.verify-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.verify-form__otp {
  margin-top: 0.25rem;
}
</style>
