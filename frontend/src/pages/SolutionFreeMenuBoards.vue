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
      <p class="mt-5 text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Restaurant Solution</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Free digital signage for menu boards
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast gives restaurants and cafes a practical starting point for digital menu boards. Launch quickly on
        browser-based screens, schedule dayparts, and keep pricing or promotions synchronized across all branches.
      </p>
      <div class="mt-8 flex flex-wrap gap-3">
        <router-link
          to="/signup"
          class="rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-3 text-sm font-semibold text-white"
        >
          Start free menu boards
        </router-link>
        <router-link
          to="/pricing"
          class="rounded-lg border border-white/20 px-5 py-3 text-sm font-semibold text-white hover:border-white/40"
        >
          View paid scaling plans
        </router-link>
      </div>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-8">
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Built for food and beverage teams</h2>
        <ul class="mt-3 list-disc pl-6 text-slate-300 space-y-2">
          <li>Daypart scheduling for breakfast, lunch, and dinner menus.</li>
          <li>Fast price or promotion updates for limited-time and seasonal campaigns.</li>
          <li>Template reuse across single stores, chains, and franchise operations.</li>
          <li>Central quality control while each branch keeps local operational flexibility.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Menu board workflow in PixelCast</h2>
        <ol class="mt-3 list-decimal pl-6 text-slate-300 space-y-2">
          <li>Pair screens in the player flow and assign each display to a branch.</li>
          <li>Create menu templates and upload approved product media.</li>
          <li>Schedule breakfast, lunch, and dinner blocks with location-level targeting.</li>
          <li>Use monitoring and logs to verify content delivery and playback stability.</li>
        </ol>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Recommended next step</h2>
        <p class="mt-3 text-slate-300">
          Pair one pilot screen first, publish a validated menu template, then scale to additional branches with the
          same workflow and centralized controls.
        </p>
      </article>
      <div class="text-sm flex flex-wrap gap-3">
        <router-link class="text-cyan-300 hover:text-cyan-200" to="/guides/turn-smart-tv-into-digital-signboard">
          Smart TV menu board guide
        </router-link>
        <router-link class="text-cyan-300 hover:text-cyan-200" to="/blog">
          Restaurant signage articles
        </router-link>
      </div>
    </section>
    </main>
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
</script>
