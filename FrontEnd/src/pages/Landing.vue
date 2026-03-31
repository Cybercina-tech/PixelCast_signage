<template>
  <div class="landing-page">
    <!-- Scroll Progress Indicator -->
    <div class="fixed top-0 left-0 right-0 h-1 z-50">
      <div 
        class="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 transition-all duration-150"
        :style="{ width: scrollProgress + '%' }"
      ></div>
    </div>

    <!-- Starfield Background -->
    <div class="fixed inset-0 starfield-background pointer-events-none z-0"></div>

    <!-- Compact top bar: logo + auth only (section jumps via side dots / scroll) -->
    <nav class="landing-nav fixed top-0 left-0 right-0 z-40 backdrop-blur-xl bg-black/20 border-b border-white/10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        <div class="flex items-center justify-between gap-3 min-h-[2.5rem]">
          <router-link
            to="/"
            class="flex items-center gap-2 min-w-0 shrink"
          >
            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-purple-600 flex items-center justify-center shrink-0">
              <svg class="w-[1.125rem] h-[1.125rem] text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <span class="text-base sm:text-lg font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent truncate">
              PixelCast
            </span>
          </router-link>
          <div class="flex items-center gap-2 sm:gap-2.5 shrink-0">
            <router-link
              to="/login"
              class="px-2 py-1.5 text-xs sm:text-sm text-white/80 hover:text-white transition-colors"
            >
              Login
            </router-link>
            <router-link
              to="/signup"
              class="neon-button px-3.5 sm:px-5 py-1.5 rounded-lg text-xs sm:text-sm font-semibold text-white transition-all duration-300"
            >
              Get Started
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- Bullet Navigation -->
    <div class="fixed right-6 top-1/2 -translate-y-1/2 z-50 hidden lg:flex flex-col gap-4">
      <button
        v-for="(section, index) in sections"
        :key="index"
        @click="scrollToSection(index)"
        class="nav-dot group relative"
        :class="{ 'active': activeSection === index }"
        :aria-label="`Go to ${section.name}`"
      >
        <div class="dot-indicator"></div>
        <span class="nav-dot-label">{{ section.name }}</span>
      </button>
    </div>

    <!-- Scroll Container with Sections -->
    <div class="scroll-container">
      <!-- Hero Section -->
      <section 
        ref="sectionRefs"
        data-section="0"
        class="section snap-section hero-section"
      >
        <div class="section-content">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div
              class="hero-align-grid grid grid-cols-1 lg:grid-cols-2 gap-8 md:gap-10 lg:gap-12 items-center h-full"
            >
              <div
                class="text-center lg:text-left section-fade-in space-y-5 md:space-y-6 max-w-2xl mx-auto lg:mx-0 lg:max-w-none"
              >
                <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
                  <span class="bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                    Command Your Screens
                  </span>
                  <br>
                  <span class="text-white">From Deep Space</span>
                </h1>
                <p class="text-lg md:text-xl text-white/70 leading-relaxed max-w-xl mx-auto lg:mx-0">
                  The most advanced digital signage platform for professional networks.
                </p>
                <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center lg:justify-start pt-1">
                  <router-link 
                    to="/signup" 
                    class="neon-button-large px-8 py-4 rounded-lg font-semibold text-lg text-white transition-all duration-300 text-center"
                  >
                    Start Free Trial
                  </router-link>
                  <button 
                    type="button"
                    @click="scrollToSection(1)" 
                    class="glass-card px-8 py-4 rounded-lg font-semibold text-lg text-white border border-white/20 hover:border-white/40 transition-all duration-300 text-center"
                  >
                    Explore Features
                  </button>
                </div>
                <div class="flex flex-wrap gap-x-6 gap-y-2 justify-center lg:justify-start pt-2 text-white/60 text-sm">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-cyan-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span>No Credit Card</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-cyan-400 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                    <span>14-Day Trial</span>
                  </div>
                </div>
              </div>
              <div
                class="relative section-fade-in hero-mockup-col hidden sm:block w-full max-w-md sm:max-w-lg md:max-w-xl mx-auto lg:max-w-none lg:mx-0 max-lg:scale-[0.94] max-lg:origin-top lg:scale-100 lg:origin-center"
                style="animation-delay: 0.2s"
              >
                <!-- Single floating device (one glass surface, 3/4 perspective) -->
                <div class="relative perspective-1000 max-w-lg mx-auto lg:max-w-none">
                  <div class="floating-mockup">
                    <div
                      class="hero-device glass-card rounded-2xl p-3 lg:p-4 shadow-2xl transform rotate-y-12 border border-white/15"
                    >
                      <div
                        class="hero-device-display relative overflow-hidden rounded-xl border border-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]"
                      >
                        <div
                          class="relative aspect-[4/3] bg-gradient-to-br from-[#0c0828] via-[#1e1b4b] to-[#5b21b6] p-4 lg:p-5"
                        >
                          <div
                            class="pointer-events-none absolute inset-0 bg-gradient-to-tr from-transparent via-white/[0.04] to-transparent"
                            aria-hidden="true"
                          ></div>
                          <div
                            class="pointer-events-none absolute inset-0 backdrop-blur-[1px] bg-white/[0.02]"
                            aria-hidden="true"
                          ></div>
                          <div
                            class="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/25 via-transparent to-indigo-950/20"
                            aria-hidden="true"
                          ></div>
                          <div class="relative z-10 flex h-full min-h-[11rem] flex-col lg:min-h-[14rem]">
                            <div class="mb-4 flex items-center justify-between">
                              <div class="h-2 w-20 rounded-full bg-white/25 lg:w-28"></div>
                              <div
                                class="h-2.5 w-2.5 animate-pulse rounded-full bg-cyan-400/90 shadow-[0_0_10px_rgba(34,211,238,0.55)]"
                              ></div>
                            </div>
                            <div class="mb-4 grid flex-1 grid-cols-3 gap-2">
                              <div
                                class="rounded-lg border border-white/10 bg-white/[0.06] backdrop-blur-sm"
                              ></div>
                              <div
                                class="rounded-lg border border-white/10 bg-white/[0.06] backdrop-blur-sm"
                              ></div>
                              <div
                                class="rounded-lg border border-white/10 bg-white/[0.06] backdrop-blur-sm"
                              ></div>
                            </div>
                            <div
                              class="h-16 rounded-lg border border-cyan-400/20 bg-gradient-to-r from-cyan-500/15 via-violet-500/10 to-purple-500/20 lg:h-20"
                            ></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Features Section -->
      <section 
        ref="sectionRefs"
        data-section="1"
        class="section snap-section features-section"
      >
        <div class="section-content">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="text-center mb-8 lg:mb-12 section-fade-in">
              <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
                Powerful <span class="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">Features</span>
              </h2>
              <p class="text-lg md:text-xl text-white/60 max-w-2xl mx-auto">
                Everything you need to manage your digital signage network at scale
              </p>
            </div>
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
              <div 
                v-for="(feature, index) in features" 
                :key="index"
                class="glass-card p-6 lg:p-8 rounded-xl group hover:scale-105 transition-transform duration-300 feature-card"
                :style="{ animationDelay: `${index * 0.1}s` }"
              >
                <div class="w-12 lg:w-14 h-12 lg:h-14 rounded-xl bg-gradient-to-br from-cyan-400/20 to-purple-500/20 flex items-center justify-center mb-4 lg:mb-6 group-hover:scale-110 transition-transform duration-300">
                  <svg class="w-6 lg:w-7 h-6 lg:h-7 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="feature.iconPath" />
                  </svg>
                </div>
                <h3 class="text-xl lg:text-2xl font-bold text-white mb-2 lg:mb-3">{{ feature.title }}</h3>
                <p class="text-white leading-relaxed text-sm lg:text-base">{{ feature.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Live Pulse Section -->
      <section 
        ref="sectionRefs"
        data-section="2"
        id="pulse"
        class="section snap-section pulse-section"
      >
        <div class="section-content">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="text-center mb-8 lg:mb-12 section-fade-in">
              <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
                Live <span class="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">Pulse</span>
              </h2>
              <p class="text-lg md:text-xl text-white/60 max-w-2xl mx-auto">
                Monitor your entire network in real-time from anywhere in the universe
              </p>
            </div>
            <div class="grid md:grid-cols-3 gap-4 lg:gap-6">
              <div 
                v-for="(screen, index) in liveScreens" 
                :key="index"
                class="glass-card p-5 lg:p-6 rounded-xl section-fade-in"
                :style="{ animationDelay: `${index * 0.15}s` }"
              >
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg lg:text-xl font-semibold text-white">{{ screen.name }}</h3>
                  <div class="flex items-center space-x-2">
                    <div 
                      class="w-2.5 lg:w-3 h-2.5 lg:h-3 rounded-full animate-pulse"
                      :class="screen.status === 'Online' ? 'bg-green-400' : 'bg-red-400'"
                    ></div>
                    <span class="text-xs lg:text-sm text-white/60">{{ screen.status }}</span>
                  </div>
                </div>
                <div class="space-y-2 lg:space-y-3">
                  <div class="flex justify-between text-xs lg:text-sm">
                    <span class="text-white/60">Uptime</span>
                    <span class="text-white font-semibold">{{ screen.uptime }}</span>
                  </div>
                  <div class="flex justify-between text-xs lg:text-sm">
                    <span class="text-white/60">Last Sync</span>
                    <span class="text-white font-semibold">{{ screen.lastSync }}</span>
                  </div>
                  <div class="flex justify-between text-xs lg:text-sm">
                    <span class="text-white/60">Content</span>
                    <span class="text-white font-semibold">{{ screen.content }}</span>
                  </div>
                </div>
                <div class="mt-4 h-2 bg-slate-700/50 rounded-full overflow-hidden">
                  <div 
                    class="h-full bg-gradient-to-r from-cyan-400 to-purple-500 rounded-full transition-all duration-1000"
                    :style="{ width: screen.status === 'Online' ? '100%' : '0%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Industry Use Cases Section -->
      <section 
        ref="sectionRefs"
        data-section="3"
        id="use-cases"
        class="section snap-section industries-section"
      >
        <div class="section-content">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <div class="text-center mb-8 lg:mb-12 section-fade-in">
              <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 text-white">
                Built for <span class="bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">Every Industry</span>
              </h2>
              <p class="text-lg md:text-xl text-white/60 max-w-2xl mx-auto">
                See how PixelCast Signage transforms operations across different sectors
              </p>
            </div>
            <div class="glass-card rounded-2xl p-6 lg:p-8 section-fade-in" style="animation-delay: 0.2s">
              <!-- Tabs -->
              <div class="flex flex-wrap gap-3 lg:gap-4 mb-6 lg:mb-8 border-b border-white/10 pb-4">
                <button
                  v-for="(industry, index) in industries"
                  :key="index"
                  @click="activeTab = index"
                  class="px-4 lg:px-6 py-2 lg:py-3 rounded-lg font-semibold text-sm lg:text-base transition-all duration-300"
                  :class="activeTab === index 
                    ? 'bg-gradient-to-r from-cyan-400 to-purple-500 text-white' 
                    : 'text-white/60 hover:text-white hover:bg-white/5'"
                >
                  {{ industry.name }}
                </button>
              </div>
              <!-- Tab Content -->
              <div class="grid md:grid-cols-2 gap-6 lg:gap-8 items-center">
                <div class="text-white">
                  <h3 class="text-2xl lg:text-3xl font-bold text-white mb-3 lg:mb-4">{{ industries[activeTab].title }}</h3>
                  <p class="text-white mb-4 lg:mb-6 leading-relaxed text-sm lg:text-base">{{ industries[activeTab].description }}</p>
                  <ul class="space-y-2 lg:space-y-3">
                    <li 
                      v-for="(benefit, idx) in industries[activeTab].benefits" 
                      :key="idx"
                      class="flex items-start space-x-2 lg:space-x-3"
                    >
                      <svg class="w-5 lg:w-6 h-5 lg:h-6 text-cyan-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                      <span class="text-white text-sm lg:text-base">{{ benefit }}</span>
                    </li>
                  </ul>
                </div>
                <div class="relative">
                  <div class="glass-card p-4 lg:p-6 rounded-xl bg-gradient-to-br from-slate-800/50 to-slate-900/50">
                    <div class="aspect-video rounded-lg overflow-hidden bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center">
                      <div class="text-center">
                        <svg class="w-16 lg:w-24 h-16 lg:h-24 mx-auto text-cyan-400/50 mb-3 lg:mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="industries[activeTab].iconPath" />
                        </svg>
                        <p class="text-white/40 text-xs lg:text-sm">{{ industries[activeTab].name }} Dashboard</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Tech Stack & CTA Section -->
      <section 
        ref="sectionRefs"
        data-section="4"
        class="section snap-section cta-section"
      >
        <div class="section-content">
          <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
            <!-- Tech Stack -->
            <div class="glass-card rounded-xl p-5 lg:p-6 text-center mb-6 lg:mb-8 section-fade-in">
              <p class="text-white/60 mb-3 lg:mb-4 text-sm lg:text-base">Powered by</p>
              <div class="flex flex-wrap justify-center items-center gap-4 lg:gap-6">
                <div class="flex items-center space-x-2 text-white/80 text-sm lg:text-base">
                  <svg class="w-5 lg:w-6 h-5 lg:h-6 text-cyan-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <span class="font-semibold">IoT</span>
                </div>
                <div class="flex items-center space-x-2 text-white/80 text-sm lg:text-base">
                  <svg class="w-5 lg:w-6 h-5 lg:h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <span class="font-semibold">Real-time Sync</span>
                </div>
                <div class="flex items-center space-x-2 text-white/80 text-sm lg:text-base">
                  <svg class="w-5 lg:w-6 h-5 lg:h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                  </svg>
                  <span class="font-semibold">Cloud Infrastructure</span>
                </div>
              </div>
            </div>
            <!-- CTA -->
            <div class="glass-card rounded-2xl p-8 lg:p-12 section-fade-in" style="animation-delay: 0.2s">
              <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-4 lg:mb-6 text-white">
                Ready to Launch Your Digital Network?
              </h2>
              <p class="text-lg lg:text-xl text-white/70 mb-6 lg:mb-8 max-w-2xl mx-auto">
                Join thousands of organizations managing their screens from deep space
              </p>
              <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <router-link 
                  to="/signup" 
                  class="neon-button-large px-8 py-4 rounded-lg font-semibold text-lg text-white transition-all duration-300 text-center"
                >
                  Start Free Trial
                </router-link>
                <router-link 
                  to="/login" 
                  class="glass-card px-8 py-4 rounded-lg font-semibold text-lg text-white border border-white/20 hover:border-white/40 transition-all duration-300 text-center"
                >
                  Sign In
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const scrollProgress = ref(0)
const activeTab = ref(0)
const activeSection = ref(0)
const sectionRefs = ref([])

const sections = ref([
  { name: 'Hero', id: 'hero' },
  { name: 'Features', id: 'features' },
  { name: 'Pulse', id: 'pulse' },
  { name: 'Industries', id: 'industries' },
  { name: 'CTA', id: 'cta' }
])

const liveScreens = ref([
  {
    name: 'London Office',
    status: 'Online',
    uptime: '99.9%',
    lastSync: '2s ago',
    content: '3 Active'
  },
  {
    name: 'Dubai Mall',
    status: 'Online',
    uptime: '99.8%',
    lastSync: '5s ago',
    content: '12 Active'
  },
  {
    name: 'Tokyo Lab',
    status: 'Offline',
    uptime: '98.2%',
    lastSync: '2m ago',
    content: '0 Active'
  }
])

const features = ref([
  {
    title: 'Visual Editor',
    description: 'Drag, drop, and rotate with pixel precision. Create stunning content without coding.',
    iconPath: 'M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z'
  },
  {
    title: 'Global Push',
    description: 'Update 1000 screens with one click. Deploy content instantly across your entire network.',
    iconPath: 'M13 10V3L4 14h7v7l9-11h-7z'
  },
  {
    title: 'Media Vault',
    description: 'Standalone cloud library for all your assets. Organize, search, and manage with ease.',
    iconPath: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z'
  },
  {
    title: 'Offline Mode',
    description: 'Content keeps playing even without internet. Never miss a beat with intelligent caching.',
    iconPath: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0'
  },
  {
    title: 'Smart Logs',
    description: 'Every heartbeat and command is tracked. Complete audit trail for compliance and debugging.',
    iconPath: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
  },
  {
    title: 'Group Management',
    description: 'Organize screens by cities, tags, or sectors. Flexible hierarchy for any organization.',
    iconPath: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z'
  }
])

const industries = ref([
  {
    name: 'Retail',
    title: 'Transform Retail Experiences',
    description: 'Engage customers with dynamic displays, promotions, and wayfinding. Update pricing and content in real-time across all locations.',
    benefits: [
      'Real-time price updates across all stores',
      'Dynamic promotional content scheduling',
      'Customer engagement analytics',
      'Multi-location content management'
    ],
    iconPath: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z'
  },
  {
    name: 'Healthcare',
    title: 'Enhance Patient Communication',
    description: 'Display wait times, appointment schedules, and health information. Keep patients informed and reduce anxiety.',
    benefits: [
      'Real-time wait time displays',
      'Appointment scheduling integration',
      'Health information broadcasting',
      'Emergency alert systems'
    ],
    iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z'
  },
  {
    name: 'F&B',
    title: 'Elevate Dining Experiences',
    description: 'Showcase menus, specials, and promotions. Update offerings instantly and create immersive dining atmospheres.',
    benefits: [
      'Dynamic menu displays',
      'Promotional content scheduling',
      'Multi-language support',
      'Nutritional information display'
    ],
    iconPath: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
  }
])

// Scroll to section
const scrollToSection = (index) => {
  const scrollContainer = document.querySelector('.scroll-container')
  if (scrollContainer) {
    const sections = scrollContainer.querySelectorAll('.snap-section')
    if (sections[index]) {
      sections[index].scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }
}

// Update active section based on scroll position
const updateActiveSection = () => {
  const scrollContainer = document.querySelector('.scroll-container')
  if (!scrollContainer) return
  
  const sections = scrollContainer.querySelectorAll('.snap-section')
  const scrollTop = scrollContainer.scrollTop
  const viewportHeight = window.innerHeight
  
  sections.forEach((section, index) => {
    const sectionTop = section.offsetTop
    const sectionHeight = section.offsetHeight
    
    // Check if section is in viewport center
    if (scrollTop + viewportHeight / 2 >= sectionTop && scrollTop + viewportHeight / 2 < sectionTop + sectionHeight) {
      activeSection.value = index
    }
  })
  
  // Update scroll progress
  const totalHeight = scrollContainer.scrollHeight - scrollContainer.clientHeight
  scrollProgress.value = totalHeight > 0 ? (scrollTop / totalHeight) * 100 : 0
}

// Intersection Observer for better section detection
let observer = null

onMounted(() => {
  // Enable scrolling
  document.body.style.overflow = 'auto'
  document.body.style.height = 'auto'
  document.documentElement.style.overflow = 'auto'
  document.documentElement.style.height = 'auto'
  
  const appContainer = document.querySelector('#app')
  if (appContainer) {
    appContainer.style.overflow = 'auto'
    appContainer.style.height = 'auto'
  }
  
  const appDiv = document.querySelector('#app > div')
  if (appDiv) {
    appDiv.style.overflow = 'auto'
    appDiv.style.height = 'auto'
  }
  
  const scrollContainer = document.querySelector('.scroll-container')
  if (scrollContainer) {
    scrollContainer.addEventListener('scroll', updateActiveSection, { passive: true })
    updateActiveSection()
    
    // Use Intersection Observer for more accurate section detection
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio > 0.5) {
            const sectionIndex = parseInt(entry.target.getAttribute('data-section') || '0')
            activeSection.value = sectionIndex
          }
        })
      },
      {
        root: scrollContainer,
        threshold: [0.5, 0.75, 1.0],
        rootMargin: '-20% 0px -20% 0px'
      }
    )
    
    scrollContainer.querySelectorAll('.snap-section').forEach((section) => {
      observer.observe(section)
    })
  }
})

onUnmounted(() => {
  const scrollContainer = document.querySelector('.scroll-container')
  if (scrollContainer) {
    scrollContainer.removeEventListener('scroll', updateActiveSection)
  }
  
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.landing-page {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0f172a 50%, #1e293b 75%, #0a0e27 100%);
  background-size: 400% 400%;
  animation: gradientShift 20s ease infinite;
}

.scroll-container {
  height: 100vh;
  overflow-y: scroll;
  overflow-x: hidden;
  scroll-behavior: smooth;
  scroll-snap-type: y mandatory;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
  position: relative;
}

.scroll-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}

.section {
  height: 100vh;
  width: 100%;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding-top: 5rem; /* Compact single-row nav */
  padding-bottom: 40px;
}

.section-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
  overflow-x: hidden;
}

.section-content::-webkit-scrollbar {
  width: 4px;
}

.section-content::-webkit-scrollbar-track {
  background: transparent;
}

.section-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

/* Background gradient animation */

@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* Starfield Background */
.starfield-background {
  background: radial-gradient(ellipse at bottom, #1b2735 0%, #090a0f 100%);
  overflow: hidden;
}

.starfield-background::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(2px 2px at 20% 30%, white, transparent),
    radial-gradient(2px 2px at 60% 70%, white, transparent),
    radial-gradient(1px 1px at 50% 50%, white, transparent),
    radial-gradient(1px 1px at 80% 10%, white, transparent),
    radial-gradient(2px 2px at 30% 80%, white, transparent),
    radial-gradient(1px 1px at 90% 40%, white, transparent);
  background-repeat: repeat;
  background-size: 200% 200%;
  animation: starfield 20s linear infinite;
  opacity: 0.6;
}

@keyframes starfield {
  from { transform: translateY(0); }
  to { transform: translateY(-2000px); }
}

/* Glassmorphism */
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Neon Buttons */
.neon-button {
  background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
  transition: all 0.3s ease;
}

.neon-button:hover {
  box-shadow: 0 0 30px rgba(6, 182, 212, 0.6), 0 0 50px rgba(139, 92, 246, 0.4);
  transform: translateY(-2px);
}

.neon-button-large {
  background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%);
  box-shadow: 0 0 25px rgba(6, 182, 212, 0.4);
  transition: all 0.3s ease;
}

.neon-button-large:hover {
  box-shadow: 0 0 40px rgba(6, 182, 212, 0.7), 0 0 60px rgba(139, 92, 246, 0.5);
  transform: translateY(-3px) scale(1.02);
}

/* Floating 3D Mockup */
.perspective-1000 {
  perspective: 1000px;
}

.floating-mockup {
  animation: float 6s ease-in-out infinite;
  transform-style: preserve-3d;
  will-change: transform;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotateX(0deg) rotateY(0deg);
  }
  50% {
    transform: translateY(-20px) rotateX(5deg) rotateY(5deg);
  }
}

.rotate-y-12 {
  transform: rotateY(12deg);
}

.hero-device {
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.09) 0%,
    rgba(255, 255, 255, 0.04) 50%,
    rgba(255, 255, 255, 0.07) 100%
  );
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.45),
    0 0 0 1px rgba(255, 255, 255, 0.06) inset;
}

/* Fade-in animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-fade-in {
  opacity: 0;
  animation: fadeInUp 0.8s ease-out forwards;
}

.feature-card {
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

/* Bullet Navigation */
.nav-dot {
  position: relative;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
  margin: 0;
}

.nav-dot:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.2);
}

.nav-dot.active {
  background: rgba(6, 182, 212, 0.8);
  border-color: #06b6d4;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.6);
  transform: scale(1.3);
}

.nav-dot-label {
  position: absolute;
  right: 24px;
  top: 50%;
  transform: translateY(-50%);
  white-space: nowrap;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(10px);
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  color: white;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
}

.nav-dot:hover .nav-dot-label {
  opacity: 1;
}

/* Accessibility - Reduced Motion */
@media (prefers-reduced-motion: reduce) {
  .landing-page,
  .starfield-background::before,
  .floating-mockup,
  .feature-card,
  .section-fade-in {
    animation: none !important;
  }
  
  .scroll-container {
    scroll-behavior: auto;
  }
  
  .neon-button:hover,
  .neon-button-large:hover {
    transform: none !important;
  }
}

/* Mobile Optimizations */
@media (max-width: 1024px) {
  .section {
    scroll-snap-type: y proximity; /* Less strict on mobile */
  }
  
  .section-content {
    max-height: calc(100vh - 100px);
    padding: 20px 0;
  }
}

@media (max-width: 768px) {
  .glass-card {
    padding: 1rem;
  }
  
  .section {
    padding-top: 4.75rem;
    padding-bottom: 20px;
  }
  
  .section-content {
    max-height: calc(100vh - 90px);
  }
  
  .nav-dot {
    display: none; /* Hide on mobile */
  }
  
  /* Allow internal scrolling on mobile if content is too tall */
  .section-content {
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
}
</style>
