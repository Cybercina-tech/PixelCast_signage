<template>
  <SolutionPageLayout>
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <router-link to="/" class="solution-back-btn">
        <span aria-hidden="true">←</span>
        Back to home
      </router-link>
      <p class="solution-kicker">Cloud Digital Signage</p>
      <h1 class="solution-title">Cloud digital signage for running on TV browser</h1>
      <p class="solution-lead">
        PixelCast is optimized for cloud-managed playback on TV browsers. Pair screens securely, control schedules
        centrally, and maintain consistent playback quality without local USB workflows.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link to="/signup" class="solution-cta-primary">Start cloud signage</router-link>
        <router-link to="/player/connect" class="solution-cta-secondary">Open TV pairing</router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="solution-card">
        <h2 class="solution-card-title">What you get in the cloud workflow</h2>
        <ul>
          <li>Centralized playlist and template scheduling by location and time window.</li>
          <li>Role-based access control for operations, marketing, and IT teams.</li>
          <li>Monitoring, logs, and remote commands for quick issue recovery.</li>
          <li>Consistent rollout process from pilot branch to full multi-site deployment.</li>
        </ul>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Deployment model</h2>
        <ol>
          <li>Connect each TV browser to the dashboard using secure pairing.</li>
          <li>Assign screen groups and attach templates or playlists to each group.</li>
          <li>Publish schedules with timing rules and branch-specific targeting.</li>
          <li>Monitor heartbeat, execution status, and content sync from reports.</li>
        </ol>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Deployment fit</h2>
        <p class="solution-body-text">
          Ideal for organizations that need fast expansion, minimal on-site maintenance, and centralized governance for
          screens across multiple cities or business units.
        </p>
      </article>
      <div class="solution-links-row pb-2">
        <router-link class="solution-inline-link" to="/solutions/browser-based-digital-signage-software">
          Browser signage overview
        </router-link>
        <router-link class="solution-inline-link" to="/pricing">Compare pricing</router-link>
      </div>
    </section>
  </SolutionPageLayout>
</template>

<script setup>
import SolutionPageLayout from '@/components/landing/SolutionPageLayout.vue'
</script>
