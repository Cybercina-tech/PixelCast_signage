<template>
  <main class="min-h-screen bg-slate-950 text-slate-100">
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <p class="text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Restaurant Solution</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Free digital signage for menu boards
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast offers free digital signage for menu boards so restaurants and cafes can launch quickly. Schedule
        breakfast, lunch, and dinner layouts, then update every location from one cloud console.
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
          <li>Fast promotion changes for limited-time offers and seasonal items.</li>
          <li>Template reuse across single stores or franchise fleets.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Recommended next step</h2>
        <p class="mt-3 text-slate-300">
          Pair your first screen in minutes, publish a menu template, then use remote commands to maintain uptime.
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
</template>
