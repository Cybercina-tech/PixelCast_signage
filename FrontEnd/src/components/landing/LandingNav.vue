<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-200/60 shadow-sm">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <router-link
          to="/"
          class="flex items-center space-x-2 hover:opacity-80 transition-opacity"
        >
          <span class="text-xl font-bold text-slate-900 tracking-tight">PixelCast Signage</span>
        </router-link>
        <div class="flex items-center space-x-4">
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="text-slate-600 hover:text-slate-900 font-medium text-sm transition-colors duration-200"
          >
            Login
          </router-link>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/dashboard"
            class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium text-sm transition-all duration-200 hover:shadow-md"
          >
            Dashboard
          </router-link>
          <router-link
            v-else
            to="/signup"
            class="px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium text-sm transition-all duration-200 hover:shadow-md"
          >
            Get Started
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

