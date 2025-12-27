<template>
  <div class="min-h-screen bg-white">
    <LandingNav />
    <Hero />
    <Features />
    <HowItWorks />
    <TrustSection />
    <CTA />
    <LandingFooter />
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
import Hero from '@/components/landing/Hero.vue'
import Features from '@/components/landing/Features.vue'
import HowItWorks from '@/components/landing/HowItWorks.vue'
import TrustSection from '@/components/landing/TrustSection.vue'
import CTA from '@/components/landing/CTA.vue'
import LandingFooter from '@/components/landing/LandingFooter.vue'
</script>
