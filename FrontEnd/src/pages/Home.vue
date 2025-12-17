<template>
  <div class="min-h-screen bg-white">
    <!-- Navbar -->
    <Navbar />
    
    <!-- Hero Section -->
    <section id="home" class="relative overflow-hidden bg-gradient-to-br from-orange-50 via-white to-orange-100 pt-32 pb-20 md:pt-40 md:pb-32">
      <!-- Animated Background Elements -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="absolute top-20 left-10 w-72 h-72 bg-orange-200 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-float"></div>
        <div class="absolute top-40 right-10 w-96 h-96 bg-orange-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style="animation-delay: 2s;"></div>
        <div class="absolute bottom-20 left-1/2 w-80 h-80 bg-orange-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-float" style="animation-delay: 4s;"></div>
      </div>
      
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="max-w-5xl mx-auto text-center">
          <div
            v-motion
            :initial="{ opacity: 0, scale: 0.9 }"
            :visible="{ opacity: 1, scale: 1 }"
            class="inline-block mb-6"
          >
            <span class="inline-flex items-center px-4 py-2 rounded-full bg-orange-100 text-orange-700 text-sm font-semibold mb-4">
              <BoltIcon class="w-4 h-4 mr-2" />
              Enterprise Digital Signage Platform
            </span>
          </div>
          
          <h1
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-6xl md:text-8xl font-black text-neutral-900 mb-6 tracking-tight leading-tight"
          >
            Screengram
            <span class="block text-orange-600 mt-2">Digital Signage System</span>
          </h1>
          
          <p
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="200"
            class="text-2xl md:text-3xl font-semibold text-neutral-700 mb-6 max-w-3xl mx-auto leading-relaxed"
          >
            Control thousands of displays in real-time. Manage content, schedules, and commands from one powerful platform.
          </p>
          
          <p
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="300"
            class="text-lg text-neutral-600 mb-10 max-w-2xl mx-auto"
          >
            Built for enterprises that demand reliability, security, and scale.
          </p>
          
          <div
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="400"
            class="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <button class="group relative px-10 py-4 bg-orange-600 text-white rounded-xl font-bold text-lg hover:bg-orange-700 transition-all duration-300 ease-out orange-glow-hover hover:-translate-y-1 active:translate-y-0 shadow-lg shadow-orange-500/30">
              <span class="relative z-10 flex items-center">
                Explore Features
                <ArrowRightIcon class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button class="group px-10 py-4 bg-white text-neutral-900 border-2 border-neutral-300 rounded-xl font-bold text-lg hover:border-orange-500 hover:text-orange-600 transition-all duration-300 ease-out hover:shadow-lg hover:-translate-y-1 active:translate-y-0">
              Get Started
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Grid Section -->
    <section id="features" class="py-24 bg-white relative">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            class="text-5xl md:text-6xl font-black text-neutral-900 mb-4"
          >
            Powerful Features
          </h2>
          <p
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-xl text-neutral-600 max-w-2xl mx-auto"
          >
            Everything you need to manage your digital signage network at scale
          </p>
        </div>
        
        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          <FeatureCard
            v-for="(feature, index) in features"
            :key="feature.title"
            :title="feature.title"
            :description="feature.description"
            :icon="feature.icon"
            :delay="200 + (index * 100)"
          />
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-24 bg-gradient-to-b from-white to-orange-50 relative overflow-hidden">
      <div class="absolute inset-0 bg-grid-pattern opacity-5"></div>
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center mb-16">
          <h2
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            class="text-5xl md:text-6xl font-black text-neutral-900 mb-4"
          >
            How It Works
          </h2>
          <p
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-xl text-neutral-600 max-w-2xl mx-auto"
          >
            Real-time communication, secure delivery, and intelligent management
          </p>
        </div>
        
        <div class="max-w-6xl mx-auto">
          <div class="grid md:grid-cols-3 gap-8 mb-8">
            <ArchitectureStep
              title="Screens Connect"
              description="Digital displays establish secure WebSocket connections, authenticated via JWT tokens for instant communication."
              :icon="DevicePhoneMobileIcon"
              :delay="200"
            />
            <ArchitectureStep
              title="Server Authenticates"
              description="The server validates credentials and maintains active connection registry for real-time command routing."
              :icon="ServerIcon"
              :delay="300"
            />
            <ArchitectureStep
              title="Commands Pushed"
              description="Commands and content updates are pushed instantly via WebSocket, with HTTP fallback for reliability."
              :icon="BoltIcon"
              :delay="400"
            />
          </div>
          <div class="grid md:grid-cols-2 gap-8">
            <ArchitectureStep
              title="Status & Logs Flow Back"
              description="Device status, heartbeat signals, and execution logs flow back to the server for monitoring and analytics."
              :icon="ArrowPathIcon"
              :delay="500"
            />
            <ArchitectureStep
              title="Secure Delivery"
              description="All communications use HMAC-signed payloads and secure URLs, ensuring content integrity and authorization."
              :icon="ShieldCheckIcon"
              :delay="600"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Why Screengram Section -->
    <section class="py-24 bg-white">
      <div class="container mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            class="text-5xl md:text-6xl font-black text-neutral-900 mb-4"
          >
            Why Screengram?
          </h2>
          <p
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-xl text-neutral-600 max-w-2xl mx-auto"
          >
            Built for enterprise scale and reliability
          </p>
        </div>
        
        <div class="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          <BenefitCard
            title="Designed for Scale"
            description="Architecture supports thousands of concurrent screen connections with efficient resource utilization."
            :icon="ScaleIcon"
            :delay="200"
          />
          <BenefitCard
            title="Secure by Default"
            description="HMAC-SHA256 signed payloads, JWT authentication, and secure signed URLs ensure tamper-proof communications."
            :icon="ShieldCheckIcon"
            :delay="300"
          />
          <BenefitCard
            title="Real-Time First"
            description="WebSocket-based communication ensures instant command delivery with intelligent HTTP fallback."
            :icon="BoltIcon"
            :delay="400"
          />
          <BenefitCard
            title="Proven Architecture"
            description="Built on Django, DRF, and Django Channels — battle-tested technologies used by enterprises worldwide."
            :icon="Cog6ToothIcon"
            :delay="500"
          />
          <BenefitCard
            title="Flexible Deployment"
            description="Deploy on-premises, use cloud storage (S3-compatible), or hybrid configurations to fit your infrastructure."
            :icon="CloudIcon"
            :delay="600"
          />
          <BenefitCard
            title="Enterprise Ready"
            description="Mission-critical deployments with reliability, monitoring, and compliance features built-in from day one."
            :icon="CheckCircleIcon"
            :delay="700"
          />
        </div>
      </div>
    </section>

    <!-- Technology Stack Section -->
    <section class="py-24 bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900 text-white relative overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(249,115,22,0.1),transparent_50%)]"></div>
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="text-center mb-16">
          <h2
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            class="text-5xl md:text-6xl font-black mb-4"
          >
            Technology & Security
          </h2>
          <p
            v-motion
            :initial="{ opacity: 0, y: 20 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-xl text-neutral-300 max-w-2xl mx-auto"
          >
            Built on enterprise-grade technologies you can trust
          </p>
        </div>
        
        <div class="max-w-5xl mx-auto">
          <div class="flex flex-wrap gap-4 justify-center">
            <TechnologyBadge
              v-for="(tech, index) in technologies"
              :key="tech.name"
              :name="tech.name"
              :icon="tech.icon"
              :delay="200 + (index * 100)"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- Call To Action Section -->
    <section id="contact" class="relative py-24 bg-gradient-to-br from-orange-600 via-orange-500 to-orange-700 text-white overflow-hidden">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_70%)]"></div>
      <div class="absolute inset-0">
        <div class="absolute top-10 left-10 w-64 h-64 bg-white/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div class="absolute bottom-10 right-10 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-pulse-slow" style="animation-delay: 2s;"></div>
      </div>
      
      <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div class="max-w-4xl mx-auto text-center">
          <h2
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            class="text-5xl md:text-6xl font-black mb-6"
          >
            Ready to Transform Your Digital Signage?
          </h2>
          <p
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="100"
            class="text-xl md:text-2xl text-orange-50 mb-10 leading-relaxed"
          >
            Join enterprises using Screengram to manage their digital signage infrastructure at scale. Start building your network today.
          </p>
          <div
            v-motion
            :initial="{ opacity: 0, y: 30 }"
            :visible="{ opacity: 1, y: 0 }"
            :delay="200"
            class="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button class="group px-10 py-4 bg-white text-orange-600 rounded-xl font-bold text-lg hover:bg-orange-50 transition-all duration-300 ease-out hover:shadow-2xl hover:-translate-y-1 active:translate-y-0 shadow-xl">
              <span class="flex items-center justify-center">
                Get Started Free
                <ArrowRightIcon class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </span>
            </button>
            <button class="px-10 py-4 bg-transparent text-white border-2 border-white rounded-xl font-bold text-lg hover:bg-white/10 transition-all duration-300 ease-out hover:-translate-y-1 active:translate-y-0">
              Schedule a Demo
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Navbar from '../components/home/Navbar.vue'
import Footer from '../components/home/Footer.vue'
import FeatureCard from '../components/home/FeatureCard.vue'
import TechnologyBadge from '../components/home/TechnologyBadge.vue'
import BenefitCard from '../components/home/BenefitCard.vue'
import ArchitectureStep from '../components/home/ArchitectureStep.vue'
import {
  DevicePhoneMobileIcon,
  ServerIcon,
  BoltIcon,
  ArrowPathIcon,
  ShieldCheckIcon,
  ScaleIcon,
  Cog6ToothIcon,
  CloudIcon,
  TvIcon,
  DocumentTextIcon,
  CommandLineIcon,
  ClockIcon,
  KeyIcon,
  ChartBarIcon,
  UserGroupIcon,
  ArrowRightIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const features = ref([
  {
    title: 'Screen Management',
    description: 'Real-time status monitoring, heartbeat tracking, and centralized control of all connected displays across your network.',
    icon: TvIcon
  },
  {
    title: 'Template & Content Management',
    description: 'Flexible template engine with widget-based content composition, version management, and drag-and-drop editing.',
    icon: DocumentTextIcon
  },
  {
    title: 'Command Execution',
    description: 'WebSocket-based command delivery for instant screen control, content updates, and system commands with guaranteed delivery.',
    icon: CommandLineIcon
  },
  {
    title: 'Scheduling System',
    description: 'Advanced scheduling engine for time-based content delivery, automated playlists, and event-driven content triggers.',
    icon: ClockIcon
  },
  {
    title: 'User & Role Management',
    description: 'Granular permissions system ensuring secure access control across users, screens, content, and administrative functions.',
    icon: UserGroupIcon
  },
  {
    title: 'Logging & Analytics',
    description: 'Comprehensive logging of all commands, executions, and system events for audit trails, troubleshooting, and insights.',
    icon: ChartBarIcon
  }
])

const technologies = ref([
  { name: 'Django + DRF', icon: Cog6ToothIcon },
  { name: 'WebSocket (Channels)', icon: BoltIcon },
  { name: 'JWT Authentication', icon: ShieldCheckIcon },
  { name: 'HMAC-SHA256', icon: ShieldCheckIcon },
  { name: 'Secure Signed URLs', icon: ShieldCheckIcon },
  { name: 'Redis / Cache', icon: ServerIcon },
  { name: 'Vue.js Frontend', icon: BoltIcon }
])
</script>
