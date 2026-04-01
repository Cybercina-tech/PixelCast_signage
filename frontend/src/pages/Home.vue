<template>
  <div class="min-h-screen starry-background relative">
    <!-- Animated Blob Background -->
    <div class="starry-blobs">
      <div class="starry-blob starry-blob-1"></div>
      <div class="starry-blob starry-blob-2"></div>
      <div class="starry-blob starry-blob-3"></div>
    </div>
    
    <div class="relative z-10">
      <!-- Navbar -->
      <Navbar />
      
      <!-- Hero Section -->
      <Hero />
      
      <!-- Features Section -->
      <Features />
      
      <!-- How It Works Section -->
      <HowItWorks />
      
      <!-- Trust & System Strength Section -->
      <TrustSection />
      
      <!-- Final CTA Section -->
      <CTA />
      
      <!-- Footer -->
      <Footer />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navbar from '../components/home/Navbar.vue'
import Footer from '../components/home/Footer.vue'
import Hero from '../components/home/Hero.vue'
import Features from '../components/home/Features.vue'
import HowItWorks from '../components/home/HowItWorks.vue'
import TrustSection from '../components/home/TrustSection.vue'
import CTA from '../components/home/CTA.vue'

onMounted(() => {
  document.title = 'PixelCast Signage - Enterprise Digital Signage Management'
  
  // Add meta description
  const metaDescription = document.querySelector('meta[name="description"]')
  if (metaDescription) {
    metaDescription.setAttribute('content', 'PixelCast Signage - Manage and control your digital signage network from one powerful platform. Real-time monitoring, content scheduling, and secure command execution.')
  } else {
    const meta = document.createElement('meta')
    meta.name = 'description'
    meta.content = 'PixelCast Signage - Manage and control your digital signage network from one powerful platform. Real-time monitoring, content scheduling, and secure command execution.'
    document.head.appendChild(meta)
  }
})
</script>
