<template>
  <div
    class="solution-page min-h-screen min-h-[100dvh]"
    :class="{ 'theme-light': !themeStore.isDarkMode }"
  >
    <LandingNav />
    <main class="solution-main pt-16">
      <slot />
    </main>
  </div>
</template>

<script setup>
import LandingNav from '@/components/landing/LandingNav.vue'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.solution-page {
  background: #020617;
  color: #e2e8f0;
  isolation: isolate;
}

/* Override global h1–h3 (light app theme forces dark --text-heading) */
.solution-page :deep(h1),
.solution-page :deep(h2),
.solution-page :deep(h3) {
  color: #f8fafc;
}

.solution-page.theme-light {
  color: #334155;
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #e2e8f0 100%);
}

.solution-page.theme-light :deep(h1),
.solution-page.theme-light :deep(h2),
.solution-page.theme-light :deep(h3) {
  color: #0f172a;
}

:deep(.solution-back-btn) {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(15, 23, 42, 0.42);
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  color: rgba(226, 232, 240, 0.94);
  text-decoration: none;
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}

:deep(.solution-back-btn:hover) {
  border-color: rgba(103, 232, 249, 0.45);
  background: rgba(15, 23, 42, 0.58);
  color: #ffffff;
}

:deep(.solution-kicker) {
  margin-top: 1.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(103, 232, 249, 0.95);
}

:deep(.solution-title) {
  margin-top: 0.75rem;
  font-size: clamp(1.75rem, 4vw, 2.25rem);
  font-weight: 700;
  line-height: 1.2;
  color: #f8fafc;
}

:deep(.solution-lead) {
  margin-top: 1rem;
  font-size: clamp(1rem, 2vw, 1.125rem);
  line-height: 1.65;
  color: rgba(203, 213, 225, 0.92);
  max-width: 48rem;
}

:deep(.solution-cta-primary) {
  display: inline-block;
  border-radius: 0.5rem;
  background: linear-gradient(to right, #06b6d4, #4f46e5);
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #ffffff;
  text-decoration: none;
  box-shadow: 0 8px 22px rgba(6, 182, 212, 0.22);
  transition: filter 0.15s ease, box-shadow 0.15s ease;
}

:deep(.solution-cta-primary:hover) {
  filter: brightness(1.06);
  box-shadow: 0 10px 26px rgba(37, 99, 235, 0.28);
}

:deep(.solution-cta-secondary) {
  display: inline-block;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.22);
  background: rgba(15, 23, 42, 0.35);
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #f8fafc;
  text-decoration: none;
  transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
}

:deep(.solution-cta-secondary:hover) {
  border-color: rgba(255, 255, 255, 0.42);
  background: rgba(15, 23, 42, 0.5);
  color: #ffffff;
}

:deep(.solution-card) {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  padding: 1.5rem;
}

:deep(.solution-card-title) {
  font-size: 1.25rem;
  font-weight: 600;
  color: #f8fafc;
}

:deep(.solution-body-text),
:deep(.solution-card ul),
:deep(.solution-card ol) {
  margin-top: 0.75rem;
  color: rgba(203, 213, 225, 0.92);
  line-height: 1.65;
}

:deep(.solution-card ul) {
  list-style: disc;
  padding-left: 1.5rem;
}

:deep(.solution-card ol) {
  list-style: decimal;
  padding-left: 1.5rem;
}

:deep(.solution-card li + li) {
  margin-top: 0.5rem;
}

:deep(.solution-inline-link) {
  color: rgba(103, 232, 249, 0.95);
  text-decoration: none;
  transition: color 0.15s ease;
}

:deep(.solution-inline-link:hover) {
  color: #a5f3fc;
}

:deep(.solution-links-row) {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  font-size: 0.875rem;
}

/* Light theme */
.solution-page.theme-light :deep(.solution-back-btn) {
  border-color: rgba(148, 163, 184, 0.52);
  background: rgba(255, 255, 255, 0.94);
  color: #334155;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}

.solution-page.theme-light :deep(.solution-back-btn:hover) {
  border-color: rgba(37, 99, 235, 0.42);
  background: #ffffff;
  color: #0f172a;
}

.solution-page.theme-light :deep(.solution-kicker) {
  color: rgba(124, 58, 237, 0.88);
}

.solution-page.theme-light :deep(.solution-title) {
  color: #0f172a;
}

.solution-page.theme-light :deep(.solution-lead) {
  color: #475569;
}

.solution-page.theme-light :deep(.solution-cta-primary) {
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.22);
}

.solution-page.theme-light :deep(.solution-cta-secondary) {
  border-color: rgba(148, 163, 184, 0.5);
  background: rgba(255, 255, 255, 0.92);
  color: #0f172a;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}

.solution-page.theme-light :deep(.solution-cta-secondary:hover) {
  border-color: rgba(37, 99, 235, 0.4);
  background: #ffffff;
  color: #1d4ed8;
}

.solution-page.theme-light :deep(.solution-card) {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

.solution-page.theme-light :deep(.solution-card-title) {
  color: #0f172a;
}

.solution-page.theme-light :deep(.solution-body-text),
.solution-page.theme-light :deep(.solution-card ul),
.solution-page.theme-light :deep(.solution-card ol) {
  color: #475569;
}

.solution-page.theme-light :deep(.solution-inline-link) {
  color: #2563eb;
}

.solution-page.theme-light :deep(.solution-inline-link:hover) {
  color: #1d4ed8;
}
</style>
