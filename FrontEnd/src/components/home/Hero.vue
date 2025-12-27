<template>
  <section class="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-50 via-white to-slate-50">
    <!-- Subtle background pattern -->
    <div class="absolute inset-0 opacity-5">
      <div class="absolute top-20 left-10 w-96 h-96 bg-slate-300 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-slate-300 rounded-full blur-3xl"></div>
    </div>

    <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10 py-20">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Badge -->
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="inline-block mb-6"
        >
          <span class="inline-flex items-center px-4 py-2 rounded-full bg-slate-100 text-slate-700 text-sm font-medium">
            <ShieldCheckIcon class="w-4 h-4 mr-2 text-slate-600" />
            Enterprise Digital Signage Platform
          </span>
        </div>

        <!-- Main Headline -->
        <h1
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="100"
          class="text-5xl md:text-7xl font-bold text-slate-900 mb-6 leading-tight"
        >
          ScreenGram
        </h1>

        <!-- Subheading -->
        <p
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="200"
          class="text-xl md:text-2xl text-slate-600 mb-4 max-w-2xl mx-auto leading-relaxed"
        >
          Manage and control your digital signage network from one powerful platform
        </p>

        <p
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="300"
          class="text-lg text-slate-500 mb-10 max-w-xl mx-auto"
        >
          Real-time monitoring, content scheduling, and secure command execution for enterprise deployments
        </p>

        <!-- CTAs -->
        <div
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="400"
          class="flex flex-col sm:flex-row gap-4 justify-center items-center"
        >
          <router-link
            to="/signup"
            class="group px-8 py-3.5 bg-slate-900 text-white rounded-lg font-semibold text-base hover:bg-slate-800 transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
          >
            <span class="flex items-center">
              Get Started
              <ArrowRightIcon class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </span>
          </router-link>
          <router-link
            to="/login"
            class="px-8 py-3.5 bg-white text-slate-900 border-2 border-slate-300 rounded-lg font-semibold text-base hover:border-slate-900 hover:bg-slate-50 transition-all duration-200"
          >
            Login
          </router-link>
        </div>

        <!-- Optional: Dashboard Preview Placeholder -->
        <div
          v-motion
          :initial="{ opacity: 0, y: 40 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="500"
          class="mt-16 max-w-5xl mx-auto"
        >
          <div class="bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden">
            <div class="bg-slate-100 px-4 py-3 flex items-center gap-2 border-b border-slate-200">
              <div class="w-3 h-3 rounded-full bg-red-400"></div>
              <div class="w-3 h-3 rounded-full bg-yellow-400"></div>
              <div class="w-3 h-3 rounded-full bg-green-400"></div>
              <div class="flex-1 text-center text-sm text-slate-500 font-medium">Dashboard Preview</div>
            </div>
            <div class="aspect-video bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
              <div class="text-center text-slate-400">
                <TvIcon class="w-16 h-16 mx-auto mb-3 opacity-50" />
                <p class="text-sm">Dashboard Interface</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ShieldCheckIcon, ArrowRightIcon, TvIcon } from '@heroicons/vue/24/outline'
</script>

