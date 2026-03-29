<template>
  <section class="py-24 bg-gradient-to-br from-slate-800 via-slate-900 to-slate-800 text-white border-t border-slate-700 relative overflow-hidden">
    <!-- Background decoration -->
    <div class="absolute inset-0 opacity-5">
      <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white rounded-full blur-3xl"></div>
    </div>
    
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div
        v-motion
        :initial="{ opacity: 0, y: 20 }"
        :visible="{ opacity: 1, y: 0 }"
        class="max-w-3xl mx-auto text-center"
      >
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">
          Start Managing Your Screens Today
        </h2>
        <p class="text-xl text-slate-300 mb-10 leading-relaxed">
          Join organizations using PixelCast Signage to streamline their digital signage operations.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <router-link
            v-if="authStore.isAuthenticated"
            to="/dashboard"
            class="inline-block px-8 py-3.5 bg-white text-slate-900 rounded-lg hover:bg-slate-100 font-semibold text-base transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-100"
          >
            Go to Dashboard
          </router-link>
          <router-link
            v-else
            to="/signup"
            class="inline-block px-8 py-3.5 bg-white text-slate-900 rounded-lg hover:bg-slate-100 font-semibold text-base transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-100"
          >
            Sign Up
          </router-link>
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="inline-block px-8 py-3.5 bg-transparent text-white border-2 border-slate-600 rounded-lg hover:border-slate-500 hover:bg-slate-800/50 font-semibold text-base transition-all duration-200"
          >
            Login
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

