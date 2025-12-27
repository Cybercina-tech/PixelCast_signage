<template>
  <section id="how-it-works" class="py-24 bg-slate-50">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h2
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-4xl md:text-5xl font-bold text-slate-900 mb-4"
        >
          How It Works
        </h2>
        <p
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="100"
          class="text-xl text-slate-600 max-w-2xl mx-auto"
        >
          Simple three-step process to get your digital signage network running
        </p>
      </div>

      <!-- Desktop: Horizontal Steps -->
      <div class="hidden md:block max-w-5xl mx-auto">
        <div class="relative">
          <!-- Connection Line -->
          <div class="absolute top-16 left-0 right-0 h-0.5 bg-slate-200">
            <div class="absolute top-0 left-0 w-full h-full bg-slate-900 origin-left" 
                 v-motion
                 :initial="{ scaleX: 0 }"
                 :visible="{ scaleX: 1 }"
                 :delay="400"
                 style="transition: transform 1s ease-out;"></div>
          </div>

          <div class="grid grid-cols-3 gap-8">
            <div
              v-for="(step, index) in steps"
              :key="step.title"
              v-motion
              :initial="{ opacity: 0, y: 30 }"
              :visible="{ opacity: 1, y: 0 }"
              :delay="200 + (index * 150)"
              class="text-center"
            >
              <div class="w-32 h-32 mx-auto mb-6 rounded-2xl bg-white border-2 border-slate-200 flex items-center justify-center shadow-sm group-hover:border-slate-900 transition-colors">
                <component :is="step.icon" class="w-12 h-12 text-slate-700" />
              </div>
              <div class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-slate-900 text-white font-semibold text-sm mb-4">
                {{ index + 1 }}
              </div>
              <h3 class="text-xl font-semibold text-slate-900 mb-2">{{ step.title }}</h3>
              <p class="text-slate-600 leading-relaxed">{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Mobile: Vertical Steps -->
      <div class="md:hidden max-w-md mx-auto space-y-8">
        <div
          v-for="(step, index) in steps"
          :key="step.title"
          v-motion
          :initial="{ opacity: 0, x: -30 }"
          :visible="{ opacity: 1, x: 0 }"
          :delay="200 + (index * 150)"
          class="flex gap-4"
        >
          <div class="flex-shrink-0">
            <div class="w-16 h-16 rounded-xl bg-white border-2 border-slate-200 flex items-center justify-center shadow-sm">
              <component :is="step.icon" class="w-8 h-8 text-slate-700" />
            </div>
          </div>
          <div class="flex-1 pt-1">
            <div class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-slate-900 text-white font-semibold text-xs mb-2">
              {{ index + 1 }}
            </div>
            <h3 class="text-lg font-semibold text-slate-900 mb-1">{{ step.title }}</h3>
            <p class="text-slate-600 text-sm leading-relaxed">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { LinkIcon, CloudArrowUpIcon, CommandLineIcon } from '@heroicons/vue/24/outline'

const steps = [
  {
    title: 'Connect Screens',
    description: 'Register your digital displays and establish secure connections to the platform.',
    icon: LinkIcon,
  },
  {
    title: 'Upload Content & Templates',
    description: 'Create templates, upload media files, and organize your content library.',
    icon: CloudArrowUpIcon,
  },
  {
    title: 'Control & Monitor Remotely',
    description: 'Schedule content, execute commands, and monitor all screens from the dashboard.',
    icon: CommandLineIcon,
  },
]
</script>

