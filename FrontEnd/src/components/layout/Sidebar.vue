<template>
  <aside
    :class="[
      'fixed left-0 top-0 h-full bg-secondary/80 dark:bg-slate-900/80 backdrop-blur-lg border-r border-border-color transition-transform duration-300 z-40',
      isOpen ? 'translate-x-0' : '-translate-x-full',
      'lg:translate-x-0 lg:static lg:z-auto'
    ]"
    class="w-64"
  >
    <div class="flex flex-col h-full">
      <div class="p-4 border-b border-border-color">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-r from-slate-900 via-emerald-700 to-emerald-600 dark:from-emerald-600 dark:via-emerald-500 dark:to-emerald-400 flex items-center justify-center">
            <BoltIcon class="w-5 h-5 text-white" />
          </div>
          <h2 class="text-xl font-semibold text-slate-900 dark:text-slate-50">ScreenGram</h2>
        </div>
      </div>
      
      <nav class="flex-1 overflow-y-auto p-4 custom-scrollbar scroll-container">
        <div v-if="sidebarStore.loading" class="flex items-center justify-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
        </div>
        <ul v-else class="space-y-2">
          <li v-for="item in sidebarStore.items" :key="item.id">
            <!-- Parent item with children (submenu) -->
            <div v-if="item.children && item.children.length > 0">
              <button
                @click="toggleSubmenu(item.id)"
                class="w-full flex items-center justify-between px-4 py-2 rounded-xl hover:bg-card hover:opacity-80 transition-all duration-200 text-slate-900 dark:text-slate-300 group relative"
                :class="{
                  'bg-gradient-to-r from-blue-600/20 to-indigo-600/20 text-blue-400 dark:text-blue-300 font-medium border-l-4 border-blue-600': isParentActive(item),
                }"
              >
                <div class="flex items-center flex-1">
                  <component 
                    :is="getIconComponent(item.icon)" 
                    :class="[
                      'w-5 h-5 mr-3 flex-shrink-0 transition-transform duration-200 group-hover:scale-110',
                      isParentActive(item)
                        ? 'text-blue-400 dark:text-blue-300'
                        : 'text-slate-900 dark:text-slate-300'
                    ]" 
                  />
                  <span class="text-slate-900 dark:text-slate-300">{{ item.title }}</span>
                  <span
                    v-if="item.badge"
                    class="ml-2 px-2 py-0.5 text-xs font-bold rounded-full bg-red-500 text-white"
                  >
                    {{ item.badge }}
                  </span>
                </div>
                <ChevronDownIcon
                  :class="[
                    'w-4 h-4 transition-transform duration-200',
                    openSubmenus.has(item.id) ? 'rotate-180' : ''
                  ]"
                />
              </button>
              <!-- Submenu items -->
              <ul
                v-if="openSubmenus.has(item.id)"
                class="mt-1 ml-4 space-y-1 border-l-2 border-border-color pl-4"
              >
                <li v-for="child in item.children" :key="child.id">
                  <router-link
                    :to="child.path"
                    class="flex items-center px-4 py-2 rounded-lg hover:bg-card hover:opacity-80 transition-all duration-200 text-slate-900 dark:text-slate-300 group relative"
                    :class="{
                      'bg-gradient-to-r from-blue-600/20 to-indigo-600/20 text-blue-400 dark:text-blue-300 font-medium border-l-4 border-blue-600': isActive(child.path),
                    }"
                  >
                    <component 
                      :is="getIconComponent(child.icon)" 
                      :class="[
                        'w-4 h-4 mr-3 flex-shrink-0 transition-transform duration-200 group-hover:scale-110',
                        isActive(child.path)
                          ? 'text-blue-400 dark:text-blue-300'
                          : 'text-slate-900 dark:text-slate-300'
                      ]" 
                    />
                    <span class="text-sm">{{ child.title }}</span>
                    <span
                      v-if="child.badge"
                      class="ml-auto px-2 py-0.5 text-xs font-bold rounded-full bg-red-500 text-white"
                    >
                      {{ child.badge }}
                    </span>
                  </router-link>
                </li>
              </ul>
            </div>
            
            <!-- Regular item without children -->
            <router-link
              v-else-if="item.path"
              :to="item.path"
              class="flex items-center px-4 py-2 rounded-xl hover:bg-card transition-all duration-200 text-slate-900 dark:text-slate-300 group"
              :class="{ 
                'bg-gradient-to-r from-blue-600/20 to-indigo-600/20 text-blue-400 dark:text-blue-300 font-medium border-l-4 border-blue-600': isActive(item.path),
                'font-normal': !isActive(item.path)
              }"
            >
              <component 
                :is="getIconComponent(item.icon)" 
                :class="[
                  'w-5 h-5 mr-3 flex-shrink-0 transition-transform duration-200 group-hover:scale-110',
                  isActive(item.path)
                    ? 'text-emerald-900 dark:text-emerald-300'
                    : 'text-slate-900 dark:text-slate-300'
                ]" 
              />
              <span class="text-slate-900 dark:text-slate-300 flex-1">{{ item.title }}</span>
              <span
                v-if="item.badge"
                class="ml-2 px-2 py-0.5 text-xs font-bold rounded-full bg-red-500 text-white"
              >
                {{ item.badge }}
              </span>
            </router-link>
          </li>
        </ul>
      </nav>
      
      <!-- Super Admin Error Dashboard Toggle -->
      <div v-if="isSuperAdmin" class="p-4 border-t border-border-color">
        <button
          @click="errorDashboardOpen = !errorDashboardOpen"
          class="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 dark:bg-red-500/20 dark:hover:bg-red-500/30 transition-colors text-red-600 dark:text-red-400"
        >
          <ExclamationTriangleIcon class="w-5 h-5" />
          <span class="font-medium">Error Dashboard</span>
        </button>
      </div>
    </div>
  </aside>
  
  <!-- Error Dashboard -->
  <ErrorDashboard
    :is-open="errorDashboardOpen"
    @close="errorDashboardOpen = false"
  />
  
  <!-- Overlay for mobile -->
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm z-30 lg:hidden transition-opacity duration-300"
    @click="$emit('close')"
  ></div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  HomeIcon,
  TvIcon,
  DocumentTextIcon,
  FolderIcon,
  ClockIcon,
  CommandLineIcon,
  UsersIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  ServerIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  ChevronDownIcon,
} from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'
import { useSidebarStore } from '@/stores/sidebar'
import ErrorDashboard from '@/components/admin/ErrorDashboard.vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['close'])

const route = useRoute()
const authStore = useAuthStore()
const sidebarStore = useSidebarStore()

const isSuperAdmin = computed(() => {
  if (!authStore.user) return false
  return authStore.user.role === 'SuperAdmin'
})

const errorDashboardOpen = ref(false)
const openSubmenus = ref(new Set())

// Icon mapping from string to component
const iconMap = {
  HomeIcon,
  TvIcon,
  DocumentTextIcon,
  FolderIcon,
  ClockIcon,
  CommandLineIcon,
  UsersIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
  ChartBarIcon,
  ShieldCheckIcon,
  ServerIcon,
  BoltIcon,
  ExclamationTriangleIcon,
}

const getIconComponent = (iconName) => {
  return iconMap[iconName] || HomeIcon
}

const isActive = (path) => {
  if (!path) return false
  // Exact match
  if (route.path === path) return true
  // Path starts with (for nested routes), but not root
  if (path !== '/' && route.path.startsWith(path)) return true
  return false
}

const isParentActive = (item) => {
  if (!item.children || item.children.length === 0) return false
  return item.children.some(child => isActive(child.path))
}

const toggleSubmenu = (itemId) => {
  if (openSubmenus.value.has(itemId)) {
    openSubmenus.value.delete(itemId)
  } else {
    openSubmenus.value.add(itemId)
  }
}

// Auto-open submenu if child is active
watch(() => route.path, (newPath) => {
  sidebarStore.items.forEach(item => {
    if (item.children && item.children.length > 0) {
      const hasActiveChild = item.children.some(child => isActive(child.path))
      if (hasActiveChild) {
        openSubmenus.value.add(item.id)
      }
    }
  })
}, { immediate: true })

// Fetch sidebar items when component mounts or user changes
onMounted(async () => {
  if (authStore.isAuthenticated && authStore.user) {
    await sidebarStore.fetchSidebarItems()
    // Auto-open submenus with active children
    sidebarStore.items.forEach(item => {
      if (item.children && item.children.length > 0) {
        const hasActiveChild = item.children.some(child => isActive(child.path))
        if (hasActiveChild) {
          openSubmenus.value.add(item.id)
        }
      }
    })
  }
})

// Watch for user changes and refetch sidebar items
watch(() => authStore.user, async (newUser) => {
  if (newUser) {
    await sidebarStore.fetchSidebarItems()
  } else {
    sidebarStore.clearSidebarItems()
  }
}, { immediate: true })
</script>
