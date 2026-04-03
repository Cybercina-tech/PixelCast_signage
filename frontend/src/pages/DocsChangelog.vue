<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
    <header class="sticky top-0 z-40 border-b border-white/10 bg-slate-950/85 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <p class="text-cyan-300 text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <h1 class="text-xl sm:text-2xl font-bold">Changelog</h1>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link
            to="/docs"
            class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-cyan-400/40 hover:text-cyan-100 transition-colors"
          >
            ← Documentation
          </router-link>
          <router-link to="/" class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-white/40 transition-colors">
            Landing
          </router-link>
        </div>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 pb-16 space-y-8">
      <section class="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/80 to-slate-950/90 p-6 sm:p-8 shadow-xl shadow-black/20">
        <p
          class="inline-flex rounded-full border border-purple-400/30 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-200 mb-4"
        >
          Release notes
        </p>
        <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight mb-3">PicxelCast changelog</h2>
        <p class="text-white/70 text-sm sm:text-base leading-relaxed">
          Major features, improvements, and fixes by version.
        </p>
      </section>

      <section
        v-for="entry in entries"
        :key="entry.version"
        class="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-5 sm:p-6 space-y-4"
      >
        <h3 class="text-lg sm:text-xl font-bold text-white border-b border-white/10 pb-3">{{ entry.version }}</h3>
        <ul class="list-disc pl-5 space-y-2 text-white/80 text-sm sm:text-base">
          <li v-for="(line, i) in entry.lines" :key="i">{{ line }}</li>
        </ul>
        <div class="flex flex-wrap gap-2 pt-1">
          <span
            v-for="tag in entry.tags"
            :key="tag"
            class="inline-flex rounded-full border border-violet-400/25 bg-violet-950/35 px-2.5 py-1 text-xs text-violet-100/90"
          >
            {{ tag }}
          </span>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

const entries = [
  {
    version: 'Version 1.0.1 — March 2026',
    lines: [
      'Unified API error envelope for form and validation failures',
      'Frontend error normalizer for consistent field and form messages',
      'Reduced duplicate panic toasts on validation errors',
      'Inline validation feedback on core CRUD and auth forms',
    ],
    tags: ['Validation UX', 'Error normalization', 'Form reliability'],
  },
  {
    version: 'Version 1.0.0 — March 2026',
    lines: [
      'Initial release',
      'Multi-screen management',
      'Content scheduler with recurring campaigns',
      'SaaS / multi-tenant controls',
      'Template builder and layout components',
      'Error handling and operational logging',
    ],
    tags: ['Docker', 'Multi-tenant', 'Scheduler', 'Templates'],
  },
]

onMounted(() => {
  document.title = 'PicxelCast Changelog'
})
</script>
