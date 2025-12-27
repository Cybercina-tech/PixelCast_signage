<template>
  <section class="py-24 bg-gradient-to-b from-slate-50 to-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
            How It Works
          </h2>
          <p class="text-lg text-slate-600 max-w-2xl mx-auto">
            Get started in three simple steps
          </p>
        </div>
        
        <!-- Desktop: Horizontal layout -->
        <div class="hidden md:flex items-start justify-between gap-8">
          <StepCard
            v-for="(step, index) in steps"
            :key="step.number"
            :number="step.number"
            :title="step.title"
            :description="step.description"
            :icon="step.icon"
            :delay="index * 150"
            :show-connector="index < steps.length - 1"
            class="flex-1"
          />
        </div>
        
        <!-- Mobile: Vertical layout -->
        <div class="md:hidden space-y-8">
          <StepCard
            v-for="(step, index) in steps"
            :key="step.number"
            :number="step.number"
            :title="step.title"
            :description="step.description"
            :icon="step.icon"
            :delay="index * 150"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import {
  LinkIcon,
  CloudArrowUpIcon,
  CommandLineIcon,
} from '@heroicons/vue/24/outline'
import StepCard from './StepCard.vue'

const steps = ref([
  {
    number: 1,
    title: 'Connect Screens',
    description: 'Register your digital displays and establish secure connections to the platform.',
    icon: LinkIcon,
  },
  {
    number: 2,
    title: 'Upload Content & Templates',
    description: 'Create templates and upload your content. Organize everything in your library.',
    icon: CloudArrowUpIcon,
  },
  {
    number: 3,
    title: 'Control & Monitor Remotely',
    description: 'Schedule playlists, execute commands, and monitor all screens from anywhere.',
    icon: CommandLineIcon,
  },
])
</script>

