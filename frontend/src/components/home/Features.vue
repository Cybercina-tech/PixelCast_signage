<template>
  <section id="features" class="py-24 bg-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h2
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-4xl md:text-5xl font-bold text-slate-900 mb-4"
        >
          Everything You Need
        </h2>
        <p
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="100"
          class="text-xl text-slate-600 max-w-2xl mx-auto"
        >
          Comprehensive tools for managing your digital signage infrastructure
        </p>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
        <div
          v-for="(feature, index) in features"
          :key="feature.title"
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="200 + (index * 100)"
          class="group bg-white rounded-xl p-6 border border-slate-200 hover:border-slate-300 hover:shadow-lg transition-all duration-200"
        >
          <div class="w-12 h-12 rounded-lg bg-slate-100 group-hover:bg-slate-900 flex items-center justify-center mb-4 transition-colors duration-200">
            <component :is="feature.icon" class="w-6 h-6 text-slate-700 group-hover:text-white transition-colors" />
          </div>
          <h3 class="text-xl font-semibold text-slate-900 mb-2">{{ feature.title }}</h3>
          <p class="text-slate-600 leading-relaxed">{{ feature.description }}</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import {
  TvIcon,
  DocumentTextIcon,
  ClockIcon,
  CommandLineIcon,
  ChartBarIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'

const features = [
  {
    title: 'Remote Screen Management',
    description: 'Monitor and control all connected displays in real-time with status tracking and heartbeat monitoring.',
    icon: TvIcon,
  },
  {
    title: 'Template & Content Control',
    description: 'Create reusable templates, upload content, and manage your media library with version control.',
    icon: DocumentTextIcon,
  },
  {
    title: 'Scheduling',
    description: 'Schedule content playback, create playlists, and automate content changes based on time or events.',
    icon: ClockIcon,
  },
  {
    title: 'Commands & Monitoring',
    description: 'Execute commands instantly via WebSocket, monitor execution status, and track system health.',
    icon: CommandLineIcon,
  },
  {
    title: 'Analytics',
    description: 'Track screen activity, content performance, and system metrics with comprehensive reporting.',
    icon: ChartBarIcon,
  },
  {
    title: 'Secure & Scalable',
    description: 'Enterprise-grade security with role-based access control, audit logs, and scalable architecture.',
    icon: ShieldCheckIcon,
  },
]
</script>

