<template>
  <main class="min-h-screen bg-slate-950 text-slate-100">
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <p class="text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Solutions</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        Browser-based digital signage software for multi-location teams
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        PixelCast helps organizations, restaurants, and retail operators run browser-based digital signage software without
        extra complexity. Publish once, schedule centrally, and keep every screen aligned across locations.
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
        <h2 class="text-xl font-semibold">Why operations teams choose a browser-first stack</h2>
        <ul class="mt-3 list-disc pl-6 text-slate-300 space-y-2">
          <li>Central content and schedule management for offices, stores, and restaurant branches.</li>
          <li>Fast launch using secure pairing on browsers and managed player endpoints.</li>
          <li>Lower maintenance burden than USB-based content workflows.</li>
        </ul>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Use cases we support</h2>
        <p class="mt-3 text-slate-300">
          Run menu boards, promotions, wayfinding screens, KPI dashboards, and internal communication signage from one
          cloud workspace.
        </p>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Related resources</h2>
        <div class="mt-3 flex flex-wrap gap-3 text-sm">
          <router-link class="text-cyan-300 hover:text-cyan-200" to="/guides/turn-smart-tv-into-digital-signboard">
            Smart TV setup guide
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
</template>
