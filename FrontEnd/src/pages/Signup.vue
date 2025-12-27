<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 flex items-center justify-center px-4 py-12 relative overflow-hidden">
    <!-- Animated Background Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000"></div>
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000"></div>
    </div>

    <div class="w-full max-w-md relative z-10">
      <!-- Auth Card with Animation -->
      <div 
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :enter="{ opacity: 1, y: 0 }"
        :transition="{ duration: 500 }"
        class="bg-card backdrop-blur-lg rounded-2xl shadow-2xl border border-border-color overflow-hidden hover:shadow-3xl transition-all duration-300"
      >
        <!-- Branding Header with Gradient -->
        <div class="bg-gradient-to-r from-slate-900 via-emerald-700 to-emerald-600 dark:from-emerald-600 dark:via-emerald-500 dark:to-emerald-400 px-8 py-10 text-center relative overflow-hidden">
          <!-- Animated Background Pattern -->
          <div class="absolute inset-0 opacity-10">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, white 1px, transparent 0); background-size: 40px 40px;"></div>
          </div>
          
          <div class="relative z-10">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-white/10 rounded-full mb-4 backdrop-blur-sm border border-white/20">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
              </svg>
            </div>
            <h1 class="text-3xl font-bold text-white mb-2 tracking-tight">ScreenGram</h1>
            <p class="text-emerald-100 dark:text-emerald-900 text-sm font-medium">Secure Digital Signage Management</p>
          </div>
        </div>

        <!-- Form Content -->
        <div class="px-8 py-8">
          <div 
            v-motion
            :initial="{ opacity: 0 }"
            :enter="{ opacity: 1 }"
            :transition="{ delay: 200, duration: 400 }"
            class="mb-6"
          >
            <h2 class="text-2xl font-bold text-primary mb-1">Create your account</h2>
            <p class="text-sm text-secondary">Sign up to get started with ScreenGram</p>
          </div>

          <form @submit.prevent="handleSignup" class="space-y-5">
            <!-- Error Message with Animation -->
            <transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 transform -translate-y-2"
              enter-to-class="opacity-100 transform translate-y-0"
              leave-active-class="transition-all duration-200 ease-in"
              leave-from-class="opacity-100 transform translate-y-0"
              leave-to-class="opacity-0 transform -translate-y-2"
            >
              <div
                v-if="error"
                class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 dark:border-red-400 rounded-lg px-4 py-3 text-sm text-red-700 dark:text-red-300 flex items-start gap-2 shadow-sm"
                role="alert"
              >
                <svg class="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="flex-1">{{ error }}</span>
              </div>
            </transition>

            <!-- Username Field -->
            <div
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0 }"
              :transition="{ delay: 300, duration: 400 }"
            >
              <label
                for="username"
                class="label-base block text-sm mb-2"
              >
                Username
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-emerald-600 dark:group-focus-within:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  id="username"
                  v-model="form.username"
                  type="text"
                  required
                  autocomplete="username"
                  class="input-base w-full pl-10 pr-4 py-3 rounded-xl"
                  placeholder="Choose a username"
                />
              </div>
            </div>

            <!-- Email Field -->
            <div
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0 }"
              :transition="{ delay: 350, duration: 400 }"
            >
              <label
                for="email"
                class="label-base block text-sm mb-2"
              >
                Email
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-emerald-600 dark:group-focus-within:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                </div>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  autocomplete="email"
                  class="input-base w-full pl-10 pr-4 py-3 rounded-xl"
                  placeholder="your@email.com"
                />
              </div>
            </div>

            <!-- Full Name Field -->
            <div
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0 }"
              :transition="{ delay: 400, duration: 400 }"
            >
              <label
                for="full_name"
                class="label-base block text-sm mb-2"
              >
                Full Name
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-emerald-600 dark:group-focus-within:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <input
                  id="full_name"
                  v-model="form.full_name"
                  type="text"
                  required
                  autocomplete="name"
                  class="input-base w-full pl-10 pr-4 py-3 rounded-xl"
                  placeholder="John Doe"
                />
              </div>
            </div>

            <!-- Password Field with Eye Icon -->
            <div
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0 }"
              :transition="{ delay: 450, duration: 400 }"
            >
              <label
                for="password"
                class="label-base block text-sm mb-2"
              >
                Password
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-emerald-600 dark:group-focus-within:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <input
                  id="password"
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  minlength="8"
                  autocomplete="new-password"
                  class="input-base w-full pl-10 pr-12 py-3 rounded-xl"
                  placeholder="Create a password"
                />
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 dark:text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 focus:outline-none transition-colors duration-200"
                  tabindex="-1"
                >
                  <EyeIcon v-if="!showPassword" class="h-5 w-5" />
                  <EyeSlashIcon v-else class="h-5 w-5" />
                </button>
              </div>
              <p class="mt-1.5 text-xs text-muted">Must be at least 8 characters</p>
            </div>

            <!-- Confirm Password Field with Eye Icon -->
            <div
              v-motion
              :initial="{ opacity: 0, x: -20 }"
              :enter="{ opacity: 1, x: 0 }"
              :transition="{ delay: 500, duration: 400 }"
            >
              <label
                for="password_confirm"
                class="label-base block text-sm mb-2"
              >
                Confirm Password
              </label>
              <div class="relative group">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-5 w-5 text-slate-400 dark:text-slate-500 group-focus-within:text-emerald-600 dark:group-focus-within:text-emerald-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <input
                  id="password_confirm"
                  v-model="form.password_confirm"
                  :type="showPasswordConfirm ? 'text' : 'password'"
                  required
                  autocomplete="new-password"
                  class="w-full pl-10 pr-12 py-3 rounded-xl transition-all duration-200"
                  :class="form.password && form.password_confirm && form.password !== form.password_confirm 
                    ? 'input-base input-error' 
                    : 'input-base'"
                  placeholder="Confirm your password"
                />
                <button
                  type="button"
                  @click="showPasswordConfirm = !showPasswordConfirm"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 dark:text-slate-500 hover:text-emerald-600 dark:hover:text-emerald-400 focus:outline-none transition-colors duration-200"
                  tabindex="-1"
                >
                  <EyeIcon v-if="!showPasswordConfirm" class="h-5 w-5" />
                  <EyeSlashIcon v-else class="h-5 w-5" />
                </button>
              </div>
              <transition
                enter-active-class="transition-all duration-200 ease-out"
                enter-from-class="opacity-0 transform -translate-y-1"
                enter-to-class="opacity-100 transform translate-y-0"
                leave-active-class="transition-all duration-150 ease-in"
                leave-from-class="opacity-100 transform translate-y-0"
                leave-to-class="opacity-0 transform -translate-y-1"
              >
                <p
                  v-if="form.password && form.password_confirm && form.password !== form.password_confirm"
                  class="mt-1.5 text-xs text-error flex items-center gap-1"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Passwords do not match
                </p>
              </transition>
            </div>

            <!-- Submit Button with Animation -->
            <div
              v-motion
              :initial="{ opacity: 0, y: 20 }"
              :enter="{ opacity: 1, y: 0 }"
              :transition="{ delay: 600, duration: 400 }"
            >
              <button
                type="submit"
                :disabled="loading || (form.password && form.password_confirm && form.password !== form.password_confirm)"
                class="btn-primary w-full py-3.5 px-4 rounded-xl focus:ring-offset-2 dark:focus:ring-offset-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02]"
              >
                <span v-if="!loading" class="flex items-center justify-center gap-2">
                  <span>Create account</span>
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
                <span v-else class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5 dark:text-slate-900" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Creating account...</span>
                </span>
              </button>
            </div>
          </form>

          <!-- Sign In Link -->
          <div
            v-motion
            :initial="{ opacity: 0 }"
            :enter="{ opacity: 1 }"
            :transition="{ delay: 700, duration: 400 }"
            class="mt-6 text-center"
          >
            <p class="text-sm text-secondary">
              Already have an account?
              <router-link
                to="/login"
                class="font-semibold text-primary-color hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-200 ml-1 inline-flex items-center gap-1 group"
              >
                Sign in
                <svg class="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </router-link>
            </p>
          </div>

          <!-- Back to Home Link -->
          <div
            v-motion
            :initial="{ opacity: 0 }"
            :enter="{ opacity: 1 }"
            :transition="{ delay: 800, duration: 400 }"
            class="mt-4 text-center"
          >
            <router-link
              to="/"
              class="text-sm text-muted hover:text-secondary transition-colors duration-200 inline-flex items-center gap-1 group"
            >
              <svg class="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Back to home</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useNotification } from '@/composables/useNotification'
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const notify = useNotification()

const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  password_confirm: '',
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)
const showPasswordConfirm = ref(false)

const handleSignup = async () => {
  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // Create user via public signup endpoint
    const userData = {
      username: form.value.username.trim().toLowerCase(),
      email: form.value.email.trim().toLowerCase(),
      full_name: form.value.full_name.trim(),
      password: form.value.password,
      password_confirm: form.value.password_confirm,
    }
    
    const response = await authAPI.signup(userData)
    
    // Signup endpoint returns tokens, so auto-login is done
    if (response.data.tokens) {
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
    error.value = err.response?.data?.detail || err.response?.data?.message || 'Failed to create account'
    notify.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
