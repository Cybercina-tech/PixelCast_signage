<template>
  <section class="py-24 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="max-w-3xl mx-auto text-center">
        <h2
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-4xl md:text-5xl font-bold mb-6"
        >
          Start Managing Your Screens Today
        </h2>
        <p
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="100"
          class="text-xl text-on-starfield mb-10 leading-relaxed"
        >
          Join organizations using PixelCast Signage to streamline their digital signage operations
        </p>
        <div
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="200"
          class="flex flex-col sm:flex-row gap-4 justify-center"
        >
          <router-link
            to="/signup"
            class="group px-8 py-3.5 bg-white text-slate-900 rounded-lg font-semibold text-base hover:bg-slate-100 transition-all duration-200 shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0"
          >
            <span class="flex items-center justify-center">
              Sign Up
              <ArrowRightIcon class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </span>
          </router-link>
          <router-link
            to="/login"
            class="px-8 py-3.5 bg-transparent text-white border-2 border-white rounded-lg font-semibold text-base hover:bg-white/10 transition-all duration-200"
          >
            Login
          </router-link>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ArrowRightIcon } from '@heroicons/vue/24/outline'
</script>

