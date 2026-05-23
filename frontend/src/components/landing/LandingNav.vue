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
          <div class="relative group">
            <button
              type="button"
              class="inline-flex items-center gap-1 text-slate-600 hover:text-slate-900 font-medium text-sm transition-colors duration-200"
              aria-label="Open blog, guides, and solutions links"
            >
              Blog
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div class="invisible opacity-0 group-hover:visible group-hover:opacity-100 group-focus-within:visible group-focus-within:opacity-100 absolute right-0 mt-2 w-80 rounded-xl border border-slate-200 bg-white shadow-lg transition-all duration-150">
              <div class="px-4 py-2 border-b border-slate-200">
                <p class="text-xs uppercase tracking-wide text-slate-500 font-semibold">Blog</p>
                <router-link to="/blog" class="mt-1 block text-sm font-semibold text-slate-900 hover:text-cyan-700">
                  PixelCast blog
                </router-link>
              </div>
              <div class="px-4 py-3">
                <p class="text-xs uppercase tracking-wide text-slate-500 font-semibold mb-2">Guides & Solutions</p>
                <div class="space-y-1">
                  <router-link to="/guides/turn-smart-tv-into-digital-signboard" class="block text-sm text-slate-700 hover:text-slate-900">
                    Guide: Turn smart TV into digital signboard
                  </router-link>
                  <router-link to="/solutions/browser-based-digital-signage-software" class="block text-sm text-slate-700 hover:text-slate-900">
                    Solution: Browser-based digital signage
                  </router-link>
                  <router-link to="/solutions/free-digital-signage-menu-boards" class="block text-sm text-slate-700 hover:text-slate-900">
                    Solution: Free menu boards
                  </router-link>
                  <router-link to="/solutions/cloud-digital-signage-tv-browser" class="block text-sm text-slate-700 hover:text-slate-900">
                    Solution: Cloud signage on TV browser
                  </router-link>
                </div>
              </div>
            </div>
          </div>
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

