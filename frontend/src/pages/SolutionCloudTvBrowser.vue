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
      <p class="mt-5 text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Cloud Digital Signage</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Cloud digital signage for running on TV browser
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast is optimized for cloud-managed playback on TV browsers. Pair screens securely, control schedules
        centrally, and maintain consistent playback quality without local USB workflows.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link
          to="/signup"
          class="rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-3 text-sm font-semibold text-white"
        >
          Start cloud signage
        </router-link>
        <router-link
          to="/player/connect"
          class="rounded-lg border border-white/20 px-5 py-3 text-sm font-semibold text-white hover:border-white/40"
        >
          Open TV pairing
        </router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">What you get in the cloud workflow</h2>
        <ul class="mt-3 list-disc pl-6 text-slate-300 space-y-2">
          <li>Centralized playlist and template scheduling by location and time window.</li>
          <li>Role-based access control for operations, marketing, and IT teams.</li>
          <li>Monitoring, logs, and remote commands for quick issue recovery.</li>
          <li>Consistent rollout process from pilot branch to full multi-site deployment.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Deployment model</h2>
        <ol class="mt-3 list-decimal pl-6 text-slate-300 space-y-2">
          <li>Connect each TV browser to the dashboard using secure pairing.</li>
          <li>Assign screen groups and attach templates or playlists to each group.</li>
          <li>Publish schedules with timing rules and branch-specific targeting.</li>
          <li>Monitor heartbeat, execution status, and content sync from reports.</li>
        </ol>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Deployment fit</h2>
        <p class="mt-3 text-slate-300">
          Ideal for organizations that need fast expansion, minimal on-site maintenance, and centralized governance for
          screens across multiple cities or business units.
        </p>
      </article>
      <div class="text-sm flex flex-wrap gap-3">
        <router-link class="text-cyan-300 hover:text-cyan-200" to="/solutions/browser-based-digital-signage-software">
          Browser signage overview
        </router-link>
        <router-link class="text-cyan-300 hover:text-cyan-200" to="/pricing">
          Compare pricing
        </router-link>
      </div>
    </section>
    </main>
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
</script>
