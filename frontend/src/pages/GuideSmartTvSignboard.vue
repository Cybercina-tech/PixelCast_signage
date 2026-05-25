<template>
  <SolutionPageLayout>
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <router-link to="/" class="solution-back-btn">
        <span aria-hidden="true">←</span>
        Back to home
      </router-link>
      <p class="solution-kicker">Guides</p>
      <h1 class="solution-title">How to turn a smart TV into a digital signboard</h1>
      <p class="solution-lead">
        This setup guide shows how to turn a smart TV into a digital signboard with PixelCast. You can open the TV
        browser, pair in seconds, then manage all content and schedules remotely from one dashboard.
      </p>
      <article class="solution-card mt-6">
        <h2 class="solution-card-title text-lg">Before you start</h2>
        <ul>
          <li>A stable internet connection for the TV and the admin dashboard.</li>
          <li>Access to PixelCast dashboard with permission to add and manage screens.</li>
          <li>Prepared media assets or templates for your first schedule.</li>
        </ul>
      </article>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-6">
      <article class="solution-card">
        <h2 class="solution-card-title">Step 1: Open the pairing screen</h2>
        <p class="solution-body-text">
          On the television, open the browser and visit the pairing URL. PixelCast will generate a secure pairing flow
          for the display.
        </p>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Step 2: Assign the screen</h2>
        <p class="solution-body-text">
          In the dashboard, name the screen, assign a location, and connect it to your content playlists or templates.
        </p>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Step 3: Build content and schedule</h2>
        <p class="solution-body-text">
          Create or select templates, upload content, then publish a schedule based on date and time windows for each
          location.
        </p>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Step 4: Publish and monitor</h2>
        <p class="solution-body-text">
          Publish your first schedule, monitor heartbeat and status, and push updates remotely whenever content changes.
        </p>
      </article>
      <article class="solution-card">
        <h2 class="solution-card-title">Operational tips for reliable playback</h2>
        <ul>
          <li>Use meaningful screen names and groups for easier bulk actions.</li>
          <li>Keep one fallback playlist ready for emergency recovery.</li>
          <li>Review status/logs regularly to catch download or command failures early.</li>
        </ul>
      </article>
      <div class="flex flex-wrap gap-3 pt-2">
        <router-link to="/player/connect" class="solution-cta-primary">Open pairing now</router-link>
        <router-link to="/solutions/cloud-digital-signage-tv-browser" class="solution-cta-secondary">
          Cloud TV browser solution
        </router-link>
        <router-link to="/solutions/browser-based-digital-signage-software" class="solution-cta-secondary">
          Browser signage overview
        </router-link>
      </div>
    </section>
  </SolutionPageLayout>
</template>

<script setup>
import SolutionPageLayout from '@/components/landing/SolutionPageLayout.vue'
</script>
