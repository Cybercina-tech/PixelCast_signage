<template>
  <section class="py-24 bg-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-16">
        <h2
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-4xl md:text-5xl font-bold text-slate-900 mb-4"
        >
          Built for Production
        </h2>
        <p
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="100"
          class="text-xl text-slate-600 max-w-2xl mx-auto"
        >
          Enterprise-grade architecture designed for reliability and scale
        </p>
      </div>

      <div class="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
        <div
          v-for="(item, index) in trustItems"
          :key="item.title"
          v-motion
          :initial="{ opacity: 0, y: 30 }"
          :visible="{ opacity: 1, y: 0 }"
          :delay="200 + (index * 100)"
          class="bg-slate-50 rounded-xl p-6 border border-slate-200"
        >
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center">
              <component :is="item.icon" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-slate-900 mb-2">{{ item.title }}</h3>
              <p class="text-slate-600 leading-relaxed">{{ item.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import {
  ShieldCheckIcon,
  DocumentTextIcon,
  ServerIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline'

const trustItems = [
  {
    title: 'Security-First Architecture',
    description: 'JWT authentication, role-based access control, and comprehensive audit logging ensure your system stays secure.',
    icon: ShieldCheckIcon,
  },
  {
    title: 'Audit Logs & Permissions',
    description: 'Complete audit trail of all actions with granular permission management for teams and organizations.',
    icon: DocumentTextIcon,
  },
  {
    title: 'Scalable Backend',
    description: 'Built on Django and Django Channels, designed to handle thousands of concurrent connections efficiently.',
    icon: ServerIcon,
  },
  {
    title: 'Real-Time Monitoring',
    description: 'WebSocket-based communication provides instant status updates and command execution tracking.',
    icon: ChartBarIcon,
  },
]
</script>

