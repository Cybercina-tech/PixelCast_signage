<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <LandingNav />
    <main class="pt-16">
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <router-link
        to="/"
        class="inline-flex items-center gap-2 rounded-lg border border-white/15 px-3 py-2 text-sm text-slate-200 hover:border-white/35 hover:text-white transition-colors"
      >
        <span aria-hidden="true">←</span>
        Back to home
      </router-link>
      <p class="mt-5 text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Solutions</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Browser-based digital signage software for multi-location teams
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast helps operations, marketing, and IT teams run browser-based digital signage without hardware-heavy
        rollout. Pair displays quickly, publish centrally, and keep every location aligned from one dashboard.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link
          to="/signup"
          class="rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-3 text-sm font-semibold text-white"
        >
          Start free
        </router-link>
        <router-link
          to="/pricing"
          class="rounded-lg border border-white/20 px-5 py-3 text-sm font-semibold text-white hover:border-white/40"
        >
          Compare plans
        </router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Why teams choose the browser-first model</h2>
        <ul class="mt-3 list-disc pl-6 text-slate-300 space-y-2">
          <li>One workspace for content, schedules, screens, and logs across all branches.</li>
          <li>Secure pairing flow for fast onboarding on TV browsers and web players.</li>
          <li>Role-based collaboration between operators, marketers, and administrators.</li>
          <li>Remote commands and heartbeat monitoring to reduce on-site support tickets.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">How rollout works in PixelCast</h2>
        <ol class="mt-3 list-decimal pl-6 text-slate-300 space-y-2">
          <li>Create screens and pair devices from the player connection flow.</li>
          <li>Build templates, upload media, and define playlists for each location.</li>
          <li>Publish schedules with timing windows and assign them at scale.</li>
          <li>Track status, command execution, and content download health in dashboard reports.</li>
        </ol>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Use cases we support</h2>
        <p class="mt-3 text-slate-300">
          Run menu boards, promotions, wayfinding, KPI dashboards, compliance screens, and internal communication
          channels from one centralized platform.
        </p>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Related resources</h2>
        <div class="mt-3 flex flex-wrap gap-3 text-sm">
          <router-link class="text-cyan-300 hover:text-cyan-200" to="/guides/turn-smart-tv-into-digital-signboard">
            Smart TV setup guide
          </router-link>
          <router-link class="text-cyan-300 hover:text-cyan-200" to="/solutions/cloud-digital-signage-tv-browser">
            Cloud TV browser solution
          </router-link>
          <router-link class="text-cyan-300 hover:text-cyan-200" to="/blog">
            Blog and best practices
          </router-link>
          <router-link class="text-cyan-300 hover:text-cyan-200" to="/data-center">
            Data center and downloads
          </router-link>
        </div>
      </article>
    </section>
    </main>
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
</script>
