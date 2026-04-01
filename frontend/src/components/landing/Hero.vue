<template>
  <section class="pt-32 pb-24 md:pt-40 md:pb-32 bg-gradient-to-b from-slate-50 via-white to-white relative overflow-hidden">
    <!-- Subtle background pattern -->
    <div class="absolute inset-0 opacity-5">
      <div class="absolute top-0 left-1/4 w-96 h-96 bg-slate-900 rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-slate-900 rounded-full blur-3xl"></div>
    </div>
    
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="max-w-5xl mx-auto text-center">
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :transition="{ duration: 600 }"
          class="inline-block mb-4"
        >
          <span class="inline-flex items-center px-4 py-1.5 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
            Enterprise Digital Signage Platform
          </span>
        </div>
        
        <h1
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :transition="{ duration: 600, delay: 100 }"
          class="text-5xl md:text-6xl lg:text-7xl font-bold text-slate-900 mb-6 leading-tight tracking-tight"
        >
          Manage Your Digital Screens<br />From Anywhere
        </h1>
        
        <p
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :transition="{ duration: 600, delay: 200 }"
          class="text-xl md:text-2xl text-slate-600 mb-10 max-w-3xl mx-auto leading-relaxed"
        >
          Control and monitor thousands of displays in real-time. Upload content, schedule playlists, and execute commands remotely with enterprise-grade security.
        </p>
        
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :transition="{ duration: 600, delay: 300 }"
          class="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <router-link
            v-if="authStore.isAuthenticated"
            to="/dashboard"
            class="px-8 py-3.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-semibold text-base transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-100"
          >
            Go to Dashboard
          </router-link>
          <router-link
            v-else
            to="/signup"
            class="px-8 py-3.5 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-semibold text-base transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-100"
          >
            Get Started
          </router-link>
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="px-8 py-3.5 bg-white text-slate-900 border-2 border-slate-300 rounded-lg hover:border-slate-400 hover:bg-slate-50 font-semibold text-base transition-all duration-200 hover:shadow-md"
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

