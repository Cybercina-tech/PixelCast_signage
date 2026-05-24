<template>
  <SolutionPageLayout>
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <router-link to="/" class="solution-back-btn">
        <span aria-hidden="true">←</span>
        Back to home
      </router-link>
      <p class="solution-kicker">Solutions</p>
      <h1 class="solution-title">
        Browser-based digital signage software for multi-location teams
      </h1>
      <p class="solution-lead">
        PixelCast helps operations, marketing, and IT teams run browser-based digital signage without hardware-heavy
        rollout. Pair displays quickly, publish centrally, and keep every location aligned from one dashboard.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link to="/signup" class="solution-cta-primary">Start free</router-link>
        <router-link to="/pricing" class="solution-cta-secondary">Compare plans</router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="solution-card">
        <h2 class="solution-card-title">Why teams choose the browser-first model</h2>
        <ul>
          <li>One workspace for content, schedules, screens, and logs across all branches.</li>
          <li>Secure pairing flow for fast onboarding on TV browsers and web players.</li>
          <li>Role-based collaboration between operators, marketers, and administrators.</li>
          <li>Remote commands and heartbeat monitoring to reduce on-site support tickets.</li>
        </ul>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">How rollout works in PixelCast</h2>
        <ol>
          <li>Create screens and pair devices from the player connection flow.</li>
          <li>Build templates, upload media, and define playlists for each location.</li>
          <li>Publish schedules with timing windows and assign them at scale.</li>
          <li>Track status, command execution, and content download health in dashboard reports.</li>
        </ol>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Use cases we support</h2>
        <p class="solution-body-text">
          Run menu boards, promotions, wayfinding, KPI dashboards, compliance screens, and internal communication
          channels from one centralized platform.
        </p>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Related resources</h2>
        <div class="solution-links-row mt-3">
          <router-link class="solution-inline-link" to="/guides/turn-smart-tv-into-digital-signboard">
            Smart TV setup guide
          </router-link>
          <router-link class="solution-inline-link" to="/solutions/cloud-digital-signage-tv-browser">
            Cloud TV browser solution
          </router-link>
          <router-link class="solution-inline-link" to="/blog">Blog and best practices</router-link>
          <router-link class="solution-inline-link" to="/data-center">Data center and downloads</router-link>
        </div>
      </article>
    </section>
  </SolutionPageLayout>
</template>

<script setup>
import SolutionPageLayout from '@/components/landing/SolutionPageLayout.vue'
</script>
