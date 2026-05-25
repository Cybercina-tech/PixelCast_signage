<template>
  <div class="auth-page cosmic-auth min-h-screen flex" :class="{ 'theme-light': !isDarkMode }">
    <div class="cosmic-bg" aria-hidden="true" />
    <div class="cosmic-starfield" aria-hidden="true" />
    <div class="nebula nebula--indigo" aria-hidden="true" />
    <div class="nebula nebula--purple" aria-hidden="true" />
    <div class="absolute top-4 right-4 z-20">
      <ThemeToggle />
    </div>

    <div
      v-if="showBrand"
      class="hidden lg:flex lg:w-1/2 xl:w-[55%] flex-col justify-center px-12 xl:px-20 py-16 relative z-10"
    >
      <div
        v-motion
        :initial="{ opacity: 0, x: -20 }"
        :enter="{ opacity: 1, x: 0 }"
        :transition="{ duration: 450 }"
        class="max-w-md w-full"
      >
        <div class="cosmic-icon-wrap auth-brand-mark inline-flex items-center justify-center w-14 h-14 rounded-xl mb-8">
          <component :is="brandIconComponent" class="w-7 h-7 cosmic-icon" />
        </div>
        <h1 class="cosmic-title auth-title text-3xl xl:text-4xl font-bold tracking-wide mb-3">
          PixelCast Signage
        </h1>
        <p class="auth-copy text-lg leading-relaxed mb-8">
          {{ brandCopy }}
        </p>

        <div v-if="heroSteps.length" class="auth-hero-panel space-y-4">
          <div class="auth-inbox-mock rounded-2xl p-5">
            <div class="flex items-center gap-3 mb-4">
              <div class="auth-inbox-mock__avatar" aria-hidden="true" />
              <div class="min-w-0 flex-1">
                <p class="auth-inbox-mock__from text-sm font-semibold">PixelCast Signage</p>
                <p class="auth-inbox-mock__subject text-xs truncate">{{ heroEmailSubject }}</p>
              </div>
              <span class="auth-inbox-mock__badge text-[10px] font-bold uppercase tracking-wide">Secure</span>
            </div>
            <p class="auth-inbox-mock__body text-sm leading-relaxed">{{ heroEmailBody }}</p>
            <div v-if="variant === 'verify'" class="auth-inbox-mock__code mt-4 flex justify-center gap-2" aria-hidden="true">
              <span v-for="i in 6" :key="i" class="auth-inbox-mock__digit" />
            </div>
            <div v-else-if="variant === 'forgot'" class="auth-inbox-mock__link mt-4 rounded-lg px-3 py-2 text-xs font-medium text-center" aria-hidden="true">
              Reset your password →
            </div>
            <div v-else-if="variant === 'reset'" class="auth-inbox-mock__lock mt-4 flex justify-center" aria-hidden="true">
              <KeyIcon class="w-8 h-8 opacity-80" />
            </div>
          </div>
          <ul class="auth-step-list">
            <li
              v-for="(step, idx) in heroSteps"
              :key="idx"
              class="auth-step-list__item"
              :class="{
                'auth-step-list__item--done': step.state === 'done',
                'auth-step-list__item--active': step.state === 'active',
              }"
            >
              <span class="auth-step-list__dot" />
              {{ step.label }}
            </li>
          </ul>
        </div>

        <slot v-if="!heroSteps.length" name="aside" />
      </div>
    </div>

    <div class="w-full lg:w-1/2 xl:w-[45%] flex items-center justify-center px-4 sm:px-6 py-12 lg:py-16 relative z-10">
      <div class="w-full max-w-md">
        <div v-if="mobileTitle" class="lg:hidden text-center mb-8">
          <h1 class="cosmic-title auth-title text-2xl font-bold">{{ mobileTitle }}</h1>
          <p v-if="mobileSubtitle" class="auth-subtitle text-sm mt-1">{{ mobileSubtitle }}</p>
        </div>

        <div
          v-motion
          :initial="{ opacity: 0, y: 16 }"
          :enter="{ opacity: 1, y: 0 }"
          :transition="{ duration: 400 }"
          class="auth-card-stack"
        >
          <div class="auth-card-glow" aria-hidden="true" />
          <div class="glass-portal rounded-2xl overflow-hidden relative">
            <div class="auth-card-shine" aria-hidden="true" />
            <div class="px-6 sm:px-8 py-8 sm:py-10 relative">
              <div v-if="heading" class="mb-6">
                <p v-if="eyebrow" class="auth-eyebrow text-xs font-semibold uppercase tracking-wider mb-2">
                  {{ eyebrow }}
                </p>
                <h2 class="cosmic-heading auth-heading text-2xl font-bold mb-2">{{ heading }}</h2>
                <p v-if="subtitle" class="auth-subtitle text-sm leading-relaxed">{{ subtitle }}</p>
              </div>
              <slot />
            </div>
          </div>
        </div>

        <div v-if="showBackLink" class="mt-6 text-center">
          <router-link
            :to="backLinkTo"
            class="auth-back-link inline-flex items-center justify-center gap-2 text-sm focus:outline-none focus:underline transition-colors duration-300"
          >
            <ArrowLeftIcon class="h-4 w-4" />
            {{ backLinkLabel }}
          </router-link>
        </div>
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import { ArrowLeftIcon, EnvelopeIcon, KeyIcon, LockClosedIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  heading: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  eyebrow: { type: String, default: '' },
  mobileTitle: { type: String, default: 'PixelCast Signage' },
  mobileSubtitle: { type: String, default: '' },
  brandCopy: {
    type: String,
    default: 'Secure digital signage management. Sign in to manage screens, content, and schedules.',
  },
  variant: { type: String, default: 'default' },
  showBrand: { type: Boolean, default: true },
  showBackLink: { type: Boolean, default: true },
  backLinkTo: { type: String, default: '/login' },
  backLinkLabel: { type: String, default: 'Back to login' },
})

const themeStore = useThemeStore()
const { isDarkMode } = storeToRefs(themeStore)

const brandIconComponent = computed(() => {
  if (props.variant === 'reset') return KeyIcon
  if (props.variant === 'forgot') return LockClosedIcon
  return EnvelopeIcon
})

const heroEmailSubject = computed(() => {
  if (props.variant === 'forgot') return 'Reset your password'
  if (props.variant === 'reset') return 'Password reset link'
  return 'Your verification code'
})

const heroEmailBody = computed(() => {
  if (props.variant === 'forgot') {
    return 'We will email you a secure link. The link is time-limited and works with your SMTP configuration.'
  }
  if (props.variant === 'reset') {
    return 'You opened a valid reset link. Choose a new password to regain access to your account.'
  }
  return 'Your 6-digit code is ready. Enter it on the right to activate your account.'
})

const heroSteps = computed(() => {
  if (props.variant === 'verify') {
    return [
      { label: 'Account created', state: 'done' },
      { label: 'Verify email', state: 'active' },
      { label: 'Access dashboard', state: 'pending' },
    ]
  }
  if (props.variant === 'forgot') {
    return [
      { label: 'Enter your email', state: 'active' },
      { label: 'Check your inbox', state: 'pending' },
      { label: 'Set new password', state: 'pending' },
    ]
  }
  if (props.variant === 'reset') {
    return [
      { label: 'Open email link', state: 'done' },
      { label: 'Choose new password', state: 'active' },
      { label: 'Sign in', state: 'pending' },
    ]
  }
  return []
})
</script>

