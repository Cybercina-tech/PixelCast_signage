<template>
  <main class="min-h-screen bg-slate-950 text-slate-100">
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <p class="text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Cloud Digital Signage</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Cloud digital signage for running on TV browser
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast delivers cloud digital signage for running on TV browser workflows. Pair smart TVs securely, schedule
        content centrally, and keep playback consistent across your screen network.
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
          <li>Monitoring and remote commands for quick issue recovery.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Deployment fit</h2>
        <p class="mt-3 text-slate-300">
          Ideal for organizations that want fast rollout without on-site USB updates or heavy player management.
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
</template>
