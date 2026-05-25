<template>
  <div class="flex h-screen overflow-hidden starry-background relative text-primary">
    <div class="starry-blobs pointer-events-none" aria-hidden="true">
      <div class="starry-blob starry-blob-1" />
      <div class="starry-blob starry-blob-2" />
      <div class="starry-blob starry-blob-3" />
    </div>

    <!-- Mobile overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed lg:static inset-y-0 left-0 z-40 w-72 max-w-[88vw] shrink-0 flex flex-col backdrop-blur-xl shadow-[var(--shadow-soft)] transition-transform duration-300 ease-out',
        sidebarSurfaceClass,
        sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      ]"
      aria-label="Super Admin navigation"
    >
      <div class="p-4 border-b border-border-color">
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center bg-gradient-to-br from-cyan-500/90 to-violet-600/90 text-white shadow-lg shrink-0"
          >
            <ShieldCheckIcon class="w-6 h-6" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-bold truncate text-primary">Super Admin</p>
            <p class="text-xs truncate text-muted">SaaS control plane</p>
          </div>
          <span :class="['text-[10px] px-2 py-1 rounded-full', isDarkTheme ? 'border-cyan-500/30 bg-cyan-500/12 text-cyan-300' : 'border-cyan-600/30 bg-cyan-600/10 text-cyan-700']">
            LIVE
          </span>
        </div>
        <div class="mt-3 rounded-xl border border-border-color bg-surface-inset px-3 py-2 text-xs text-muted">
          {{ activeGroupLabel }}
          <span class="mx-1">•</span>
          {{ navItemCount }} sections
        </div>
      </div>

      <nav class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-4">
        <div v-for="group in SUPER_ADMIN_NAV_GROUPS" :key="group.id">
          <p class="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
            {{ group.label }}
          </p>
          <ul class="space-y-1">
            <li v-for="link in group.items" :key="link.to">
              <router-link
                :to="link.to"
                class="group flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-all"
                :class="[navClass(link), !isDarkTheme && isNavActive(link) ? 'super-admin-nav-active-light' : '']"
                @click="sidebarOpen = false"
              >
                <component :is="iconFor(link.icon)" class="w-5 h-5 shrink-0 transition-transform group-hover:scale-105" />
                <span class="truncate">{{ link.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <div class="p-3 border-t border-border-color space-y-2">
        <router-link
          to="/dashboard"
          class="flex items-center justify-center gap-2 w-full rounded-xl px-3 py-2.5 text-sm font-medium border border-border-light text-secondary hover:bg-surface-inset hover:text-primary transition-colors"
        >
          <ArrowLeftIcon class="w-4 h-4 shrink-0" />
          Back to app
        </router-link>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col min-w-0 relative z-10">
      <header
        :class="[
          'shrink-0 sticky top-0 z-20 border-b px-4 md:px-6 py-3 flex items-center gap-3 backdrop-blur-md',
          isDarkTheme
            ? 'border-slate-700/70 bg-slate-900/70'
            : 'border-border-light bg-[var(--bg-topbar)]',
        ]"
      >
        <button
          type="button"
          :class="[
            'lg:hidden p-2 rounded-lg border',
            isDarkTheme
              ? 'border-slate-700 text-slate-200 hover:bg-slate-800'
              : 'border-border-light text-secondary hover:bg-surface-inset',
          ]"
          aria-label="Open menu"
          @click="sidebarOpen = true"
        >
          <Bars3Icon class="w-5 h-5" />
        </button>
        <div class="flex-1 min-w-0">
          <p class="text-[11px] uppercase tracking-wider mb-0.5 text-muted">Control Plane</p>
          <h1 class="text-lg md:text-xl font-bold truncate text-primary">{{ pageTitle }}</h1>
          <p v-if="pageSubtitle" class="text-xs truncate mt-0.5 text-muted">{{ pageSubtitle }}</p>
        </div>
        <div :class="['hidden md:flex items-center gap-2 text-xs shrink-0', isDarkTheme ? 'text-slate-300' : 'text-slate-600']">
          <router-link
            to="/settings?tab=billing"
            class="px-2 py-1 rounded-lg border border-cyan-500/30 bg-cyan-500/10 text-cyan-700 dark:text-cyan-300 hover:bg-cyan-500/20 transition-colors inline-flex items-center gap-1"
          >
            <CreditCardIcon class="w-3.5 h-3.5" />
            Plan
          </router-link>
          <span :class="['px-2 py-1 rounded-lg border', isDarkTheme ? 'bg-amber-500/15 text-amber-300 border-amber-500/30' : 'bg-amber-500/12 text-amber-700 border-amber-600/30']">
            Developer
          </span>
          <router-link
            to="/super-admin/system"
            class="px-2 py-1 rounded-lg border border-accent-color/35 bg-accent-color/12 text-accent-color hover:bg-accent-color/20 transition-colors"
          >
            System
          </router-link>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto custom-scrollbar p-4 md:p-6 lg:p-8">
        <div class="mx-auto max-w-[1400px]">
          <PlatformConfigBanner class="mb-4" />
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import {
  ArrowLeftIcon,
  Bars3Icon,
  ShieldCheckIcon,
  Squares2X2Icon,
  BuildingOffice2Icon,
  UsersIcon,
  CurrencyDollarIcon,
  TagIcon,
  ArrowPathIcon,
  BellAlertIcon,
  ChartBarIcon,
  ServerStackIcon,
  ChatBubbleLeftRightIcon,
  ClipboardDocumentListIcon,
  CpuChipIcon,
  FlagIcon,
  Cog6ToothIcon,
  EnvelopeIcon,
  NewspaperIcon,
  SparklesIcon,
  KeyIcon,
  GlobeAltIcon,
  CreditCardIcon,
} from '@heroicons/vue/24/outline'
import { SUPER_ADMIN_NAV_GROUPS } from '@/config/superAdminNav'
import PlatformConfigBanner from '@/components/super-admin/PlatformConfigBanner.vue'

const route = useRoute()
const sidebarOpen = ref(false)
const themeStore = useThemeStore()

const iconMap = {
  Squares2X2Icon,
  BuildingOffice2Icon,
  UsersIcon,
  CurrencyDollarIcon,
  TagIcon,
  ArrowPathIcon,
  BellAlertIcon,
  ChartBarIcon,
  ServerStackIcon,
  ChatBubbleLeftRightIcon,
  ClipboardDocumentListIcon,
  CpuChipIcon,
  FlagIcon,
  Cog6ToothIcon,
  EnvelopeIcon,
  NewspaperIcon,
  SparklesIcon,
  KeyIcon,
  GlobeAltIcon,
}

function iconFor(name) {
  return iconMap[name] || Squares2X2Icon
}

function isTicketsQueueNavActive(path) {
  const p = path.replace(/\/$/, '') || '/'
  if (p === '/super-admin/tickets') return true
  if (!p.startsWith('/super-admin/tickets/')) return false
  const first = p.slice('/super-admin/tickets/'.length).split('/')[0]
  if (!first) return false
  if (first === 'analytics' || first === 'settings') return false
  return true
}

function isNavActive(link) {
  if (link.match === 'exact') {
    return route.path === link.to || route.path === `${link.to}/`
  }
  if (link.match === 'tickets-queue') {
    return isTicketsQueueNavActive(route.path)
  }
  return route.path === link.to || route.path.startsWith(`${link.to}/`)
}

function navClass(link) {
  if (isNavActive(link)) {
    return isDarkTheme.value
      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-[0_0_0_1px_rgba(56,189,248,.25)]'
      : 'border border-border-light shadow-sm'
  }
  return isDarkTheme.value
    ? 'text-slate-300 hover:bg-slate-800/80 hover:text-white border border-transparent'
    : 'text-muted hover:bg-surface-inset hover:text-primary border border-transparent'
}

const pageTitle = computed(() => route.meta.superAdminTitle || 'Super Admin')
const isDarkTheme = computed(() => themeStore.isDarkMode)

const sidebarSurfaceClass = computed(() =>
  isDarkTheme.value
    ? 'border-r border-border-color bg-card/95'
    : 'border-r border-border-light bg-[var(--bg-sidebar)]'
)

const pageSubtitle = computed(() => {
  if (route.meta.superAdminSubtitle) return route.meta.superAdminSubtitle
  const n = route.name
  if (n === 'super-admin-customer-detail' && route.params.id) {
    return `Tenant · ${route.params.id}`
  }
  return ''
})

const navItemCount = computed(() =>
  SUPER_ADMIN_NAV_GROUPS.reduce((acc, group) => acc + group.items.length, 0)
)

const activeGroupLabel = computed(() => {
  const group = SUPER_ADMIN_NAV_GROUPS.find((g) => g.items.some((item) => isNavActive(item)))
  return group?.label || 'Overview'
})
</script>

<style scoped>
.super-admin-nav-active-light {
  background: var(--nav-active-bg);
  color: var(--brand-accent);
}
</style>
