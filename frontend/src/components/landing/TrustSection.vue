<template>
  <section class="py-24 bg-slate-900 text-white relative overflow-hidden">
    <!-- Subtle background decoration -->
    <div class="absolute inset-0 opacity-10">
      <div class="absolute top-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
    </div>
    
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="max-w-6xl mx-auto">
        <div
          v-motion
          :initial="{ opacity: 0, y: 20 }"
          :visible="{ opacity: 1, y: 0 }"
          class="text-center mb-16"
        >
          <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            Built for Production Environments
          </h2>
          <p class="text-lg text-on-starfield max-w-2xl mx-auto">
            Enterprise-grade infrastructure designed for reliability, security, and scale
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 gap-6 mb-12">
          <TrustCard
            v-for="(item, index) in trustItems"
            :key="item.title"
            :title="item.title"
            :description="item.description"
            :icon="item.icon"
            :delay="index * 100"
          />
        </div>
        
        <div
          v-motion
          :initial="{ opacity: 0 }"
          :visible="{ opacity: 1 }"
          :transition="{ delay: 400 }"
          class="text-center"
        >
          <p class="text-on-starfield text-lg">
            Trusted by enterprises requiring mission-critical reliability and security
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import {
  ShieldCheckIcon,
  DocumentCheckIcon,
  ArrowPathIcon,
  ChartBarIcon,
} from '@heroicons/vue/24/outline'
import TrustCard from './TrustCard.vue'

const trustItems = ref([
  {
    title: 'Security-First Architecture',
    description: 'JWT authentication, HMAC-signed payloads, and secure URL generation ensure tamper-proof communications and content delivery.',
    icon: ShieldCheckIcon,
  },
  {
    title: 'Audit Logs & Permissions',
    description: 'Comprehensive audit trails for all actions with granular role-based access control for users, screens, and administrative functions.',
    icon: DocumentCheckIcon,
  },
  {
    title: 'Scalable Backend',
    description: 'Architecture designed for horizontal scaling with support for thousands of concurrent screen connections and efficient resource management.',
    icon: ArrowPathIcon,
  },
  {
    title: 'Real-Time Monitoring',
    description: 'WebSocket-based communication ensures instant command delivery and status updates with comprehensive health metrics and analytics.',
    icon: ChartBarIcon,
  },
])
</script>

