<template>
  <div class="flex h-screen starry-background relative">
    <!-- Animated Blob Background -->
    <div class="starry-blobs">
      <div class="starry-blob starry-blob-1"></div>
      <div class="starry-blob starry-blob-2"></div>
      <div class="starry-blob starry-blob-3"></div>
    </div>
    
    <Sidebar :is-open="sidebarOpen" @close="sidebarOpen = false" />
    <div class="flex-1 flex flex-col overflow-hidden md:ml-0 relative z-10">
      <Navbar :title="title" @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
      <Footer />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

defineProps({
  title: {
    type: String,
    default: 'ScreenGram',
  },
})

const sidebarOpen = ref(false)
</script>
