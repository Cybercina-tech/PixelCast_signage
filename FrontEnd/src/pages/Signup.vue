<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center px-4">
    <div class="max-w-md w-full">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 mb-2">ScreenGram</h1>
          <p class="text-gray-600">Create your account</p>
        </div>
        
        <form @submit.prevent="handleSignup" class="space-y-6">
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ error }}
          </div>
          
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="johndoe"
            />
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="your@email.com"
            />
          </div>
          
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              id="full_name"
              v-model="form.full_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              minlength="8"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="••••••••"
            />
            <p class="mt-1 text-xs text-gray-500">Must be at least 8 characters</p>
          </div>
          
          <div>
            <label for="password_confirm" class="block text-sm font-medium text-gray-700 mb-1">
              Confirm Password
            </label>
            <input
              id="password_confirm"
              v-model="form.password_confirm"
              type="password"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="••••••••"
            />
          </div>
          
          <button
            type="submit"
            :disabled="loading || form.password !== form.password_confirm"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Creating account...' : 'Sign up' }}
          </button>
        </form>
        
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600">
            Already have an account?
            <router-link to="/login" class="text-indigo-600 hover:text-indigo-700 font-medium">
              Sign in
            </router-link>
          </p>
        </div>
        
        <div class="mt-4 text-center">
          <router-link to="/" class="text-sm text-gray-500 hover:text-gray-700">
            ← Back to home
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usersAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const authStore = useAuthStore()
const toastStore = useToastStore()

const form = ref({
  username: '',
  email: '',
  full_name: '',
  password: '',
  password_confirm: '',
})

const loading = ref(false)
const error = ref('')

const handleSignup = async () => {
  if (form.value.password !== form.value.password_confirm) {
    error.value = 'Passwords do not match'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    // Create user via API - backend requires password_confirm
    const userData = {
      username: form.value.username,
      email: form.value.email,
      full_name: form.value.full_name,
      password: form.value.password,
      password_confirm: form.value.password_confirm,
    }
    
    await usersAPI.create(userData)
    
    // Auto-login after signup - backend login uses username
    await authStore.login({
      username: form.value.username,
      password: form.value.password,
    })
    
    toastStore.success('Account created successfully!')
    router.push('/dashboard')
  } catch (err) {
    error.value = err.response?.data?.detail || err.response?.data?.message || 'Failed to create account'
    toastStore.error(error.value)
  } finally {
    loading.value = false
  }
}
</script>
