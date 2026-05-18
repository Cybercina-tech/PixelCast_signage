<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
    <header class="sticky top-0 z-40 border-b border-white/10 bg-slate-950/80 backdrop-blur">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
        <div>
          <p class="text-cyan-300 text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <h1 class="text-xl sm:text-2xl font-bold">Downloads</h1>
        </div>
        <router-link to="/" class="btn-outline px-4 py-2 rounded-lg text-sm">Back to Home</router-link>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <section
        class="rounded-2xl border border-cyan-400/25 bg-gradient-to-br from-cyan-950/40 to-slate-900/90 p-5 sm:p-6 shadow-lg shadow-cyan-950/20"
      >
        <h2 class="text-lg font-semibold text-white mb-2">Android TV app</h2>
        <p class="text-sm text-white/75 mb-3 max-w-3xl">
          One official APK for TVs and boxes that run <strong class="text-white/90">Android TV</strong> or
          <strong class="text-white/90">Google TV</strong>. The same build works across manufacturers—no per-brand
          packages.
        </p>
        <p class="text-xs text-white/55 mb-4 max-w-3xl">
          Displays on <strong class="text-white/70">Tizen</strong>, <strong class="text-white/70">webOS</strong>, or
          other non-Android platforms do not use this APK. Use the
          <router-link to="/player/connect" class="text-cyan-300 underline hover:text-cyan-200">Web Player</router-link>
          in the device browser instead.
        </p>
        <div v-if="apkDownloadUrl" class="flex flex-wrap gap-3 items-center">
          <a
            :href="apkDownloadUrl"
            class="btn-primary px-4 py-2.5 rounded-lg text-sm font-medium inline-flex items-center gap-2"
            rel="noopener noreferrer"
          >
            Download APK
          </a>
          <span class="text-xs text-white/50">Install, then pair the screen from your admin.</span>
        </div>
        <p v-else class="text-sm text-amber-100/90 leading-relaxed">
          Configure a download URL via server env
          <code class="mx-0.5 rounded bg-black/35 px-1.5 py-0.5 font-mono text-xs">ANDROID_TV_APK_URL</code>
          (recommended) or build-time
          <code class="mx-0.5 rounded bg-black/35 px-1.5 py-0.5 font-mono text-xs">VITE_ANDROID_TV_APK_URL</code>
          to show the button here.
        </p>
      </section>

      <section class="rounded-2xl border border-white/10 bg-white/5 p-5 sm:p-6 text-sm text-white/70 leading-relaxed">
        <p>
          For browser-based signage on any display, open the
          <router-link to="/player/connect" class="text-cyan-300 underline hover:text-cyan-200">Web Player</router-link>
          — no APK required.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { publicAPI } from '@/services/api'

const apkDownloadUrl = ref('')

async function loadApkDownloadUrl() {
  try {
    const response = await publicAPI.downloads()
    const url = response?.data?.android_tv_apk_url
    if (url && String(url).trim()) {
      apkDownloadUrl.value = String(url).trim()
      return
    }
  } catch {
    /* optional: server offline or not configured */
  }
  const viteUrl = import.meta.env.VITE_ANDROID_TV_APK_URL
  if (viteUrl) apkDownloadUrl.value = String(viteUrl).trim()
}

onMounted(() => {
  loadApkDownloadUrl()
})
</script>
