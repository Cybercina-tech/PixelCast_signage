<template>
  <section class="py-24 bg-white">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="max-w-6xl mx-auto">
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-slate-900 mb-4">
            Everything You Need
          </h2>
          <p class="text-lg text-slate-600 max-w-2xl mx-auto">
            Powerful features to manage your digital signage network efficiently
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            v-for="(feature, index) in features"
            :key="feature.title"
            :title="feature.title"
            :description="feature.description"
            :icon="feature.icon"
            :delay="index * 100"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import {
  ComputerDesktopIcon,
  DocumentTextIcon,
  ClockIcon,
  CommandLineIcon,
  ChartBarIcon,
  ShieldCheckIcon,
} from '@heroicons/vue/24/outline'
import FeatureCard from './FeatureCard.vue'

const features = ref([
  {
    title: 'Remote Screen Management',
    description: 'Control and monitor all connected displays from a centralized dashboard with real-time status updates.',
    icon: ComputerDesktopIcon,
  },
  {
    title: 'Template & Content Control',
    description: 'Upload, organize, and schedule content across your network with flexible template-based layouts.',
    icon: DocumentTextIcon,
  },
  {
    title: 'Advanced Scheduling',
    description: 'Time-based content delivery with automated playlists and event-driven triggers for precise control.',
    icon: ClockIcon,
  },
  {
    title: 'Commands & Monitoring',
    description: 'Execute remote commands instantly via WebSocket with comprehensive logging and execution tracking.',
    icon: CommandLineIcon,
  },
  {
    title: 'Analytics & Insights',
    description: 'Track screen performance, content engagement, and system health with detailed analytics dashboards.',
    icon: ChartBarIcon,
  },
  {
    title: 'Secure & Scalable',
    description: 'Enterprise-grade security with role-based access control, audit logs, and scalable architecture.',
    icon: ShieldCheckIcon,
  },
])
</script>

