<template>
  <footer class="relative bg-gradient-to-br from-neutral-900 via-neutral-900 to-neutral-950 text-white overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(249,115,22,0.05),transparent_50%)]"></div>
    
    <div class="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <!-- Main Footer Content -->
      <div class="py-16 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
        <!-- About Section -->
        <div class="lg:col-span-1">
          <div class="flex items-center space-x-3 mb-6">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/30">
              <BoltIcon class="w-6 h-6 text-white" />
            </div>
            <span class="text-2xl font-black bg-gradient-to-r from-orange-500 to-orange-600 bg-clip-text text-transparent">
              PixelCast
            </span>
          </div>
          <p class="text-neutral-400 leading-relaxed mb-6 text-sm">
            Enterprise digital signage management platform. Control thousands of displays in real-time with secure, scalable infrastructure built for mission-critical deployments.
          </p>
          <div class="flex space-x-4">
            <!-- LinkedIn -->
            <a
              href="https://linkedin.com/company/pixelcast-signage"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 rounded-lg bg-neutral-800 hover:bg-orange-500 flex items-center justify-center transition-all duration-300 ease-out hover:scale-110 hover:rotate-3 group"
              aria-label="LinkedIn"
            >
              <svg class="w-5 h-5 text-neutral-400 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
            </a>
            <!-- Twitter -->
            <a
              href="https://twitter.com/pixelcast-signage"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 rounded-lg bg-neutral-800 hover:bg-orange-500 flex items-center justify-center transition-all duration-300 ease-out hover:scale-110 hover:rotate-3 group"
              aria-label="Twitter"
            >
              <svg class="w-5 h-5 text-neutral-400 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
              </svg>
            </a>
            <!-- GitHub -->
            <a
              href="https://github.com/pixelcast-signage"
              target="_blank"
              rel="noopener noreferrer"
              class="w-10 h-10 rounded-lg bg-neutral-800 hover:bg-orange-500 flex items-center justify-center transition-all duration-300 ease-out hover:scale-110 hover:rotate-3 group"
              aria-label="GitHub"
            >
              <svg class="w-5 h-5 text-neutral-400 group-hover:text-white transition-colors" fill="currentColor" viewBox="0 0 24 24">
                <path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd"/>
              </svg>
            </a>
          </div>
        </div>

        <!-- Product Links Section -->
        <div>
          <h3 class="text-lg font-bold text-white mb-6">Product</h3>
          <ul class="space-y-3">
            <li>
              <a
                href="#features"
                @click.prevent="scrollToSection('#features')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Features
                </span>
              </a>
            </li>
            <li>
              <a
                href="#features"
                @click.prevent="scrollToSection('#features')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Screens
                </span>
              </a>
            </li>
            <li>
              <a
                href="#features"
                @click.prevent="scrollToSection('#features')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Templates
                </span>
              </a>
            </li>
            <li>
              <a
                href="#features"
                @click.prevent="scrollToSection('#features')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Schedules
                </span>
              </a>
            </li>
            <li>
              <a
                href="#features"
                @click.prevent="scrollToSection('#features')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Pricing
                </span>
              </a>
            </li>
          </ul>
        </div>

        <!-- Company / Legal Section -->
        <div>
          <h3 class="text-lg font-bold text-white mb-6">Company</h3>
          <ul class="space-y-3">
            <li>
              <a
                href="#about"
                @click.prevent="scrollToSection('#about')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  About
                </span>
              </a>
            </li>
            <li>
              <a
                href="#contact"
                @click.prevent="scrollToSection('#contact')"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Contact
                </span>
              </a>
            </li>
            <li>
              <router-link
                to="/privacy"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Privacy Policy
                </span>
              </router-link>
            </li>
            <li>
              <router-link
                to="/terms"
                class="text-neutral-400 hover:text-orange-400 transition-all duration-300 ease-out inline-block hover:translate-x-1 text-sm group"
              >
                <span class="flex items-center">
                  <span class="w-0 group-hover:w-2 h-0.5 bg-orange-500 mr-0 group-hover:mr-2 transition-all duration-300"></span>
                  Terms of Service
                </span>
              </router-link>
            </li>
          </ul>
        </div>

        <!-- Meta / Trust Section -->
        <div>
          <h3 class="text-lg font-bold text-white mb-6">Support</h3>
          <ul class="space-y-3 mb-6">
            <li>
              <a
                href="mailto:support@pixelcastsignage.com"
                class="text-neutral-400 hover:text-orange-400 transition-colors duration-300 text-sm flex items-center gap-2"
              >
                <EnvelopeIcon class="w-4 h-4" />
                support@pixelcastsignage.com
              </a>
            </li>
            <li>
              <span class="text-neutral-400 text-sm">Version: v{{ appVersion }}</span>
            </li>
            <li>
              <a
                href="#"
                class="text-neutral-400 hover:text-orange-400 transition-colors duration-300 text-sm"
              >
                Status Page
              </a>
            </li>
          </ul>
          
          <!-- Optional CTA -->
          <div class="mt-4">
            <a
              href="/signup"
              class="inline-block px-4 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-medium text-sm hover:from-orange-600 hover:to-orange-700 transition-all duration-300 ease-out shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 hover:-translate-y-0.5 active:translate-y-0"
            >
              Start Free Trial
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom Bar -->
      <div class="border-t border-neutral-800 py-8">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div class="flex items-center space-x-2 text-neutral-400 text-sm">
            <span>© {{ currentYear }} PixelCast Signage. All rights reserved.</span>
          </div>
          <div class="flex items-center space-x-6 text-sm">
            <router-link
              to="/privacy"
              class="text-neutral-400 hover:text-orange-400 transition-colors duration-300"
            >
              Privacy Policy
            </router-link>
            <router-link
              to="/terms"
              class="text-neutral-400 hover:text-orange-400 transition-colors duration-300"
            >
              Terms of Service
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Scroll to Top Button -->
    <button
      v-if="showScrollTop"
      @click="scrollToTop"
      class="fixed bottom-8 right-8 w-12 h-12 bg-gradient-to-br from-orange-500 to-orange-600 text-white rounded-full shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 flex items-center justify-center transition-all duration-300 ease-out hover:scale-110 hover:-translate-y-1 active:translate-y-0 z-40 group"
      aria-label="Scroll to top"
    >
      <ArrowUpIcon class="w-6 h-6 group-hover:-translate-y-1 transition-transform duration-300" />
    </button>
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import {
  BoltIcon,
  EnvelopeIcon,
  ArrowUpIcon
} from '@heroicons/vue/24/outline'

const currentYear = new Date().getFullYear()
const showScrollTop = ref(false)

// App version from Git (set at build time)
// Format: commit hash (e.g., "e994370")
const appVersion = ref(typeof __APP_VERSION__ !== 'undefined' ? __APP_VERSION__ : 'dev')

const scrollToSection = (href) => {
  const targetId = href.replace('#', '')
  const element = document.getElementById(targetId)
  if (element) {
    const offset = 80
    const elementPosition = element.getBoundingClientRect().top
    const offsetPosition = elementPosition + window.pageYOffset - offset

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
  }
}

const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// Newsletter form removed - replaced with CTA button

const handleScroll = () => {
  showScrollTop.value = window.scrollY > 500
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
