<template>
  <nav
    class="fixed top-0 left-0 right-0 z-50 bg-neutral-900/95 backdrop-blur-md border-b border-neutral-800/50 transition-all duration-300"
    :class="{ 'shadow-lg shadow-orange-500/10': scrolled }"
  >
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-20">
        <!-- Logo -->
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center shadow-lg shadow-orange-500/30">
            <BoltIcon class="w-6 h-6 text-white" />
          </div>
          <span class="text-2xl font-black bg-gradient-to-r from-orange-500 to-orange-600 bg-clip-text text-transparent">
            Screengram
          </span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden lg:flex items-center space-x-1">
          <a
            v-for="link in navLinks"
            :key="link.name"
            :href="link.href"
            @click.prevent="scrollToSection(link.href)"
            class="px-4 py-2 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800/50 transition-all duration-300 ease-out font-medium text-sm relative group"
            :class="{ 'text-orange-400': link.active }"
          >
            <span class="relative z-10">{{ link.name }}</span>
            <span
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-orange-500 to-orange-600 transform transition-transform duration-300 origin-left rounded-full"
              :class="link.active ? 'scale-x-100' : 'scale-x-0 group-hover:scale-x-100'"
            ></span>
          </a>
        </div>

        <!-- CTA Button & Mobile Menu Toggle -->
        <div class="flex items-center space-x-4">
          <button
            @click="scrollToSection('#contact')"
            class="hidden lg:block px-6 py-2.5 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-bold text-sm hover:from-orange-600 hover:to-orange-700 transition-all duration-300 ease-out shadow-lg shadow-orange-500/30 hover:shadow-xl hover:shadow-orange-500/40 hover:-translate-y-0.5 active:translate-y-0"
          >
            Get Started
          </button>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            class="lg:hidden p-2 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800/50 transition-colors"
            aria-label="Toggle menu"
          >
            <div class="w-6 h-6 relative">
              <span
                class="absolute top-0 left-0 w-6 h-0.5 bg-current transform transition-all duration-300"
                :class="mobileMenuOpen ? 'rotate-45 translate-y-2.5' : ''"
              ></span>
              <span
                class="absolute top-2.5 left-0 w-6 h-0.5 bg-current transition-all duration-300"
                :class="mobileMenuOpen ? 'opacity-0' : 'opacity-100'"
              ></span>
              <span
                class="absolute top-5 left-0 w-6 h-0.5 bg-current transform transition-all duration-300"
                :class="mobileMenuOpen ? '-rotate-45 -translate-y-2.5' : ''"
              ></span>
            </div>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div
        class="lg:hidden overflow-hidden transition-all duration-300 ease-out"
        :class="mobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'"
      >
        <div class="py-4 space-y-2 border-t border-neutral-800/50 mt-2">
          <a
            v-for="link in navLinks"
            :key="link.name"
            :href="link.href"
            @click.prevent="scrollToSection(link.href); closeMobileMenu()"
            class="block px-4 py-3 rounded-lg text-neutral-300 hover:text-white hover:bg-neutral-800/50 transition-all duration-300 font-medium"
            :class="{ 'text-orange-400 bg-neutral-800/30': link.active }"
          >
            {{ link.name }}
          </a>
          <button
            @click="scrollToSection('#contact'); closeMobileMenu()"
            class="w-full mt-4 px-6 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-bold text-sm hover:from-orange-600 hover:to-orange-700 transition-all duration-300 shadow-lg shadow-orange-500/30"
          >
            Get Started
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { BoltIcon } from '@heroicons/vue/24/outline'

const mobileMenuOpen = ref(false)
const scrolled = ref(false)

const navLinks = ref([
  { name: 'Home', href: '#home', active: true },
  { name: 'Features', href: '#features', active: false },
  { name: 'Templates', href: '#features', active: false },
  { name: 'Commands', href: '#features', active: false },
  { name: 'Scheduling', href: '#features', active: false },
  { name: 'Users', href: '#features', active: false },
  { name: 'Contact', href: '#contact', active: false }
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
}

const handleScroll = () => {
  scrolled.value = window.scrollY > 20
  updateActiveLink()
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  updateActiveLink()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>
