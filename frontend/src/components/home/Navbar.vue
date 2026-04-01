<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 transition-all duration-300"
    :class="[
      scrolled 
        ? 'bg-white/95 backdrop-blur-md shadow-lg border-b border-gray-200' 
        : 'bg-transparent'
    ]"
  >
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        <!-- Logo -->
        <router-link
          to="/"
          class="flex items-center space-x-3"
        >
          <div
            :class="[
              'w-10 h-10 rounded-xl flex items-center justify-center shadow-lg transition-all duration-300',
              scrolled 
                ? 'bg-gradient-to-br from-orange-500 to-orange-600 shadow-orange-500/30' 
                : 'bg-gradient-to-br from-orange-500 to-orange-600 shadow-orange-500/30'
            ]"
          >
            <BoltIcon class="w-6 h-6 text-white" />
          </div>
          <span
            :class="[
              'text-2xl font-black bg-gradient-to-r from-orange-500 to-orange-600 bg-clip-text text-transparent transition-all duration-300',
              scrolled ? 'text-xl' : ''
            ]"
          >
            PixelCast
          </span>
        </router-link>

        <!-- Desktop Navigation -->
        <div class="hidden lg:flex items-center space-x-1">
          <a
            v-for="link in navLinks"
            :key="link.name"
            :href="link.href"
            @click.prevent="scrollToSection(link.href)"
            :class="[
              'px-4 py-2 rounded-lg transition-all duration-300 ease-out font-medium text-sm relative group',
              scrolled 
                ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50' 
                : 'text-white hover:text-orange-400 hover:bg-white/10',
              link.active ? (scrolled ? 'text-orange-600' : 'text-orange-400') : ''
            ]"
          >
            <span class="relative z-10">{{ link.name }}</span>
            <span
              :class="[
                'absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-orange-500 to-orange-600 transform transition-transform duration-300 origin-left rounded-full',
                link.active ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'
              ]"
            ></span>
          </a>
        </div>

        <!-- Right Side: Auth Buttons / User Menu -->
        <div class="flex items-center space-x-4">
          <!-- Authenticated: Dashboard Link -->
          <template v-if="authStore.isAuthenticated">
            <router-link
              to="/dashboard"
              :class="[
                'hidden lg:block px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300',
                scrolled 
                  ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50' 
                  : 'text-white hover:text-orange-400 hover:bg-white/10'
              ]"
            >
              Dashboard
            </router-link>
            <router-link
              to="/dashboard"
              class="lg:hidden p-2 rounded-lg"
              :class="scrolled ? 'text-gray-700' : 'text-white'"
            >
              <HomeIcon class="w-6 h-6" />
            </router-link>
          </template>

          <!-- Not Authenticated: Login + CTA -->
          <template v-else>
            <router-link
              to="/login"
              :class="[
                'hidden lg:block px-4 py-2 rounded-lg font-medium text-sm transition-all duration-300',
                scrolled 
                  ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50' 
                  : 'text-white hover:text-orange-400 hover:bg-white/10'
              ]"
            >
              Login
            </router-link>
            <router-link
              to="/signup"
              :class="[
                'px-6 py-2.5 rounded-lg font-bold text-sm transition-all duration-300 ease-out shadow-lg hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0',
                scrolled
                  ? 'bg-gradient-to-r from-orange-500 to-orange-600 text-white shadow-orange-500/30 hover:from-orange-600 hover:to-orange-700'
                  : 'bg-white text-orange-600 shadow-white/20 hover:bg-gray-50'
              ]"
            >
              <span class="hidden sm:inline">Sign up</span>
              <span class="sm:hidden">Sign up</span>
            </router-link>
          </template>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            :class="[
              'lg:hidden p-2 rounded-lg transition-colors',
              scrolled ? 'text-gray-700 hover:bg-gray-100' : 'text-white hover:bg-white/10'
            ]"
            aria-label="Toggle menu"
          >
            <div class="w-6 h-6 relative">
              <span
                :class="[
                  'absolute top-0 left-0 w-6 h-0.5 transform transition-all duration-300',
                  scrolled ? 'bg-gray-700' : 'bg-white',
                  mobileMenuOpen ? 'rotate-45 translate-y-2.5' : ''
                ]"
              ></span>
              <span
                :class="[
                  'absolute top-2.5 left-0 w-6 h-0.5 transition-all duration-300',
                  scrolled ? 'bg-gray-700' : 'bg-white',
                  mobileMenuOpen ? 'opacity-0' : 'opacity-100'
                ]"
              ></span>
              <span
                :class="[
                  'absolute top-5 left-0 w-6 h-0.5 transform transition-all duration-300',
                  scrolled ? 'bg-gray-700' : 'bg-white',
                  mobileMenuOpen ? '-rotate-45 -translate-y-2.5' : ''
                ]"
              ></span>
            </div>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div
        :class="[
          'lg:hidden overflow-hidden transition-all duration-300 ease-out',
          mobileMenuOpen ? 'max-h-96 opacity-100 pb-4' : 'max-h-0 opacity-0'
        ]"
      >
        <div
          :class="[
            'py-4 space-y-2 border-t',
            scrolled ? 'border-gray-200' : 'border-white/20'
          ]"
        >
          <a
            v-for="link in navLinks"
            :key="link.name"
            :href="link.href"
            @click.prevent="scrollToSection(link.href); closeMobileMenu()"
            :class="[
              'block px-4 py-3 rounded-lg transition-all duration-300 font-medium',
              scrolled
                ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50'
                : 'text-white hover:text-orange-400 hover:bg-white/10',
              link.active 
                ? (scrolled ? 'text-orange-600 bg-gray-50' : 'text-orange-400 bg-white/10')
                : ''
            ]"
          >
            {{ link.name }}
          </a>
          
          <!-- Auth Buttons in Mobile Menu -->
          <template v-if="!authStore.isAuthenticated">
            <div class="pt-2 border-t" :class="scrolled ? 'border-gray-200' : 'border-white/20'">
              <router-link
                to="/login"
                @click="closeMobileMenu"
                :class="[
                  'block px-4 py-3 rounded-lg font-medium transition-all duration-300',
                  scrolled
                    ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50'
                    : 'text-white hover:text-orange-400 hover:bg-white/10'
                ]"
              >
                Login
              </router-link>
              <router-link
                to="/signup"
                @click="closeMobileMenu"
                class="block mt-2 px-4 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-bold text-sm hover:from-orange-600 hover:to-orange-700 transition-all duration-300 shadow-lg shadow-orange-500/30"
              >
                Sign up
              </router-link>
            </div>
          </template>
          <template v-else>
            <div class="pt-2 border-t" :class="scrolled ? 'border-gray-200' : 'border-white/20'">
              <router-link
                to="/dashboard"
                @click="closeMobileMenu"
                :class="[
                  'block px-4 py-3 rounded-lg font-medium transition-all duration-300',
                  scrolled
                    ? 'text-gray-700 hover:text-orange-600 hover:bg-gray-50'
                    : 'text-white hover:text-orange-400 hover:bg-white/10'
                ]"
              >
                Go to Dashboard
              </router-link>
            </div>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BoltIcon, HomeIcon } from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)
const scrolled = ref(false)

const navLinks = ref([
  { name: 'Features', href: '#features', active: false },
  { name: 'How it works', href: '#how-it-works', active: false }
])

const updateActiveLink = () => {
  const sections = document.querySelectorAll('section[id]')
  const scrollPosition = window.scrollY + 100

  sections.forEach((section) => {
    const sectionTop = section.offsetTop
    const sectionHeight = section.offsetHeight
    const sectionId = section.getAttribute('id')

    if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
      navLinks.value.forEach((link) => {
        link.active = link.href === `#${sectionId}`
      })
    }
  })
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

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
  closeMobileMenu()
}

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
  updateActiveLink()
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  updateActiveLink()
  // Initial check
  scrolled.value = window.scrollY > 20
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* Smooth transitions */
nav {
  backdrop-filter: blur(8px);
}
</style>
