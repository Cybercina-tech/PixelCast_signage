<template>
  <main class="min-h-screen bg-slate-950 text-slate-100">
    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-14 sm:py-16">
      <p class="text-xs uppercase tracking-[0.16em] text-cyan-300 font-semibold">Guides</p>
      <h1 class="mt-3 text-3xl sm:text-4xl font-bold leading-tight">
        How to turn a smart TV into a digital signboard
      </h1>
      <p class="mt-4 text-slate-300 text-base sm:text-lg leading-relaxed max-w-3xl">
        This setup guide shows how to turn a smart TV into a digital signboard with PixelCast. You can open the TV
        browser, pair in seconds, then manage all content and schedules remotely from one dashboard.
      </p>
    </section>

    <section class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 pb-16 space-y-6">
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Step 1: Open the pairing screen</h2>
        <p class="mt-3 text-slate-300">
          On the television, open the browser and visit the pairing URL. PixelCast will generate a secure pairing flow for
          the display.
        </p>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Step 2: Assign the screen</h2>
        <p class="mt-3 text-slate-300">
          In the dashboard, name the screen, assign a location, and connect it to your content playlists or templates.
        </p>
      </article>
      <article class="rounded-2xl border border-white/10 bg-white/5 p-6">
        <h2 class="text-xl font-semibold">Step 3: Publish and monitor</h2>
        <p class="mt-3 text-slate-300">
          Publish your first schedule, monitor heartbeat and status, and push updates remotely whenever content changes.
        </p>
      </article>
      <div class="flex flex-wrap gap-3 pt-2">
        <router-link
          to="/player/connect"
          class="rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-5 py-3 text-sm font-semibold text-white"
        >
          Open pairing now
        </router-link>
        <router-link
          to="/solutions/cloud-digital-signage-tv-browser"
          class="rounded-lg border border-white/20 px-5 py-3 text-sm font-semibold text-white hover:border-white/40"
        >
          Cloud TV browser solution
        </router-link>
      </div>
    </section>
  </main>
</template>
