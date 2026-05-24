<template>
  <div
    class="data-center-page min-h-screen min-h-[100dvh]"
    :class="{ 'theme-light': !themeStore.isDarkMode }"
  >
    <header class="data-center-header sticky top-0 z-40 border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between gap-4">
        <div>
          <p class="data-center-kicker text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <h1 class="data-center-title text-xl sm:text-2xl font-bold">Downloads</h1>
        </div>
        <router-link to="/" class="data-center-nav-btn px-4 py-2 rounded-lg text-sm">Back to Home</router-link>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-6 pb-16">
      <section class="data-center-card data-center-card-featured rounded-2xl border p-5 sm:p-6">
        <h2 class="data-center-card-title text-lg font-semibold mb-2">Android TV app</h2>
        <p class="data-center-body text-sm mb-3 max-w-3xl">
          One official APK for TVs and boxes that run <strong>Android TV</strong> or
          <strong>Google TV</strong>. The same build works across manufacturers—no per-brand packages.
        </p>
        <p class="data-center-muted text-xs mb-4 max-w-3xl">
          Displays on <strong>Tizen</strong>, <strong>webOS</strong>, or other non-Android platforms do not use this
          APK. Use the
          <router-link to="/player/connect" class="data-center-link">Web Player</router-link>
          in the device browser instead.
        </p>
        <div v-if="apkDownloadUrl" class="flex flex-wrap gap-3 items-center">
          <a
            :href="apkDownloadUrl"
            class="data-center-cta-primary px-4 py-2.5 rounded-lg text-sm font-medium inline-flex items-center gap-2"
            rel="noopener noreferrer"
          >
            Download APK
          </a>
          <span class="data-center-hint text-xs">Install, then pair the screen from your admin.</span>
        </div>
        <p v-else class="data-center-notice text-sm leading-relaxed">
          Configure a download URL via server env
          <code class="data-center-code">ANDROID_TV_APK_URL</code>
          (recommended) or build-time
          <code class="data-center-code">VITE_ANDROID_TV_APK_URL</code>
          to show the button here.
        </p>
      </section>

      <section class="data-center-card rounded-2xl border p-5 sm:p-6 text-sm leading-relaxed">
        <p class="data-center-body">
          For browser-based signage on any display, open the
          <router-link to="/player/connect" class="data-center-link">Web Player</router-link>
          — no APK required.
        </p>
      </section>
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { publicAPI } from '@/services/api'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
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

<style scoped>
.data-center-page {
  background: linear-gradient(135deg, #020617 0%, #0f172a 50%, #020617 100%);
  color: #e2e8f0;
  isolation: isolate;
}

.data-center-page :deep(h1),
.data-center-page :deep(h2) {
  color: #f8fafc;
}

.data-center-header {
  border-bottom-color: rgba(255, 255, 255, 0.12);
  background: rgba(2, 6, 23, 0.9);
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.data-center-kicker {
  color: rgba(103, 232, 249, 0.95);
}

.data-center-title {
  color: #f8fafc;
}

.data-center-nav-btn {
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(15, 23, 42, 0.42);
  color: rgba(226, 232, 240, 0.94);
  text-decoration: none;
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}

.data-center-nav-btn:hover {
  border-color: rgba(103, 232, 249, 0.45);
  background: rgba(15, 23, 42, 0.58);
  color: #ffffff;
}

.data-center-card {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
}

.data-center-card-featured {
  border-color: rgba(34, 211, 238, 0.28);
  background: linear-gradient(135deg, rgba(8, 47, 73, 0.55) 0%, rgba(15, 23, 42, 0.88) 100%);
  box-shadow: 0 12px 32px rgba(8, 47, 73, 0.35);
}

.data-center-card-title {
  color: #f8fafc;
}

.data-center-body {
  color: rgba(248, 250, 252, 0.88);
  line-height: 1.65;
}

.data-center-body strong {
  color: rgba(248, 250, 252, 0.95);
  font-weight: 600;
}

.data-center-muted {
  color: rgba(203, 213, 225, 0.78);
  line-height: 1.6;
}

.data-center-muted strong {
  color: rgba(226, 232, 240, 0.9);
  font-weight: 600;
}

.data-center-link {
  color: rgba(103, 232, 249, 0.95);
  text-decoration: underline;
  text-underline-offset: 2px;
  transition: color 0.15s ease;
}

.data-center-link:hover {
  color: #a5f3fc;
}

.data-center-hint {
  color: rgba(148, 163, 184, 0.9);
}

.data-center-notice {
  color: rgba(254, 243, 199, 0.92);
}

.data-center-code {
  margin-inline: 0.125rem;
  border-radius: 0.25rem;
  background: rgba(0, 0, 0, 0.35);
  padding: 0.125rem 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.75rem;
  color: rgba(226, 232, 240, 0.95);
}

.data-center-cta-primary {
  background: linear-gradient(to right, #06b6d4, #4f46e5);
  color: #ffffff;
  text-decoration: none;
  box-shadow: 0 8px 22px rgba(6, 182, 212, 0.22);
  transition: filter 0.15s ease, box-shadow 0.15s ease;
}

.data-center-cta-primary:hover {
  filter: brightness(1.06);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.28);
}

/* Light theme */
.data-center-page.theme-light {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #e2e8f0 100%);
  color: #334155;
}

.data-center-page.theme-light :deep(h1),
.data-center-page.theme-light :deep(h2) {
  color: #0f172a;
}

.data-center-page.theme-light .data-center-header {
  border-bottom-color: rgba(148, 163, 184, 0.36);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.94) 0%, rgba(248, 250, 252, 0.9) 100%);
}

.data-center-page.theme-light .data-center-kicker {
  color: #0284c7;
}

.data-center-page.theme-light .data-center-title {
  color: #0f172a;
}

.data-center-page.theme-light .data-center-nav-btn {
  border-color: rgba(148, 163, 184, 0.52);
  background: rgba(255, 255, 255, 0.94);
  color: #334155;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}

.data-center-page.theme-light .data-center-nav-btn:hover {
  border-color: rgba(37, 99, 235, 0.42);
  background: #ffffff;
  color: #0f172a;
}

.data-center-page.theme-light .data-center-card {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

.data-center-page.theme-light .data-center-card-featured {
  border-color: rgba(37, 99, 235, 0.28);
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.95) 0%, rgba(255, 255, 255, 0.92) 100%);
  box-shadow: 0 12px 30px rgba(37, 99, 235, 0.12);
}

.data-center-page.theme-light .data-center-card-title {
  color: #0f172a;
}

.data-center-page.theme-light .data-center-body {
  color: #475569;
}

.data-center-page.theme-light .data-center-body strong {
  color: #0f172a;
}

.data-center-page.theme-light .data-center-muted {
  color: #64748b;
}

.data-center-page.theme-light .data-center-muted strong {
  color: #334155;
}

.data-center-page.theme-light .data-center-link {
  color: #2563eb;
}

.data-center-page.theme-light .data-center-link:hover {
  color: #1d4ed8;
}

.data-center-page.theme-light .data-center-hint {
  color: #64748b;
}

.data-center-page.theme-light .data-center-notice {
  color: #92400e;
}

.data-center-page.theme-light .data-center-code {
  background: rgba(241, 245, 249, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: #334155;
}

.data-center-page.theme-light .data-center-cta-primary {
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
}
</style>
