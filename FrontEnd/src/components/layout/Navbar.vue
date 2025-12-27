<template>
  <nav class="sticky top-0 z-40 bg-secondary/80 dark:bg-slate-900/80 backdrop-blur-lg border-b border-border-color shadow-sm">
    <div class="px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-14">
        <!-- Left: Logo + Breadcrumb -->
        <div class="flex items-center flex-1 min-w-0">
          <!-- Sidebar Toggle (Mobile) -->
          <button
            @click="$emit('toggle-sidebar')"
            class="md:hidden p-2 -ml-2 rounded-lg hover:bg-card text-slate-900 dark:text-slate-300"
            aria-label="Toggle sidebar"
          >
            <Bars3Icon class="w-5 h-5 text-slate-900 dark:text-slate-300" />
          </button>

          <!-- Logo (Desktop) -->
          <div class="hidden md:flex items-center mr-4">
            <div class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center mr-2">
              <BoltIcon class="w-5 h-5 text-white" />
            </div>
            <span class="text-lg font-semibold text-zinc-900 dark:text-white">ScreenGram</span>
          </div>

          <!-- Breadcrumb -->
          <nav class="flex items-center space-x-2 text-sm text-zinc-600 dark:text-zinc-400 min-w-0 flex-1">
            <router-link
              to="/dashboard"
              class="hover:text-zinc-900 dark:hover:text-white transition-colors duration-200 truncate"
            >
              Dashboard
            </router-link>
            <template v-if="breadcrumbs.length > 0">
              <ChevronRightIcon class="w-4 h-4 flex-shrink-0 text-zinc-400 dark:text-zinc-600" />
              <template v-for="(crumb, index) in breadcrumbs" :key="index">
                <span
                  v-if="index === breadcrumbs.length - 1"
                  class="text-zinc-900 dark:text-white font-medium truncate"
                >
                  {{ crumb.label }}
                </span>
                <router-link
                  v-else
                  :to="crumb.path"
                  class="hover:text-zinc-900 dark:hover:text-white transition-colors duration-200 truncate"
                >
                  {{ crumb.label }}
                </router-link>
                <ChevronRightIcon
                  v-if="index < breadcrumbs.length - 1"
                  class="w-4 h-4 flex-shrink-0"
                />
              </template>
            </template>
          </nav>
        </div>

        <!-- Right: Theme Toggle + System Info + Notifications + User Menu -->
        <div class="flex items-center space-x-3 ml-4">
          <!-- Theme Toggle -->
          <ThemeToggle />
          
          <!-- Environment Badge (optional) -->
          <span
            v-if="environment && environment !== 'production'"
            :class="[
              'hidden lg:inline-flex px-2 py-1 rounded text-xs font-medium',
              environment === 'staging' ? 'bg-yellow-100 text-yellow-700' : 'bg-blue-100 text-blue-700'
            ]"
          >
            {{ environment }}
          </span>

          <!-- API Status Alert (if disconnected) -->
          <div
            v-if="apiStatus === 'disconnected'"
            class="hidden lg:flex items-center gap-1.5 px-2 py-1 bg-red-50 text-red-700 rounded text-xs"
            title="API Connection Lost"
          >
            <ExclamationTriangleIcon class="w-4 h-4" />
            <span>API Offline</span>
          </div>

          <!-- Notifications -->
          <div class="relative">
            <button
              @click="toggleNotifications"
              class="p-2 rounded-lg hover:bg-card text-slate-900 dark:text-slate-300 hover:text-slate-900 dark:hover:text-slate-50 transition-colors relative"
              aria-label="Notifications"
            >
              <BellIcon class="w-5 h-5 text-slate-900 dark:text-slate-300" />
              <span
                v-if="unreadNotifications > 0"
                class="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"
              ></span>
            </button>

            <!-- Notifications Dropdown -->
            <div
              v-if="showNotifications"
              ref="notificationsDropdown"
              class="absolute right-0 mt-2 w-80 bg-card rounded-lg shadow-lg border border-border-color py-2 z-50"
            >
              <div class="px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                <h3 class="text-sm font-semibold text-primary">Notifications</h3>
                <button
                  v-if="unreadNotifications > 0"
                  @click="markAllAsRead"
                  class="text-xs text-blue-600 hover:text-blue-700"
                >
                  Mark all read
                </button>
              </div>
              <div class="max-h-96 overflow-y-auto">
                <div
                  v-if="notifications.length === 0"
                  class="px-4 py-8 text-center text-sm text-muted"
                >
                  No notifications
                </div>
                <div
                  v-for="notification in notifications"
                  :key="notification.id"
                  :class="[
                    'px-4 py-3 hover:bg-secondary border-b border-border-color last:border-0 cursor-pointer',
                    !notification.read ? 'bg-blue-50' : ''
                  ]"
                  @click="handleNotificationClick(notification)"
                >
                  <div class="flex items-start gap-3">
                    <div
                      :class="[
                        'w-2 h-2 rounded-full mt-1.5 flex-shrink-0',
                        notification.type === 'success' ? 'bg-green-500' : '',
                        notification.type === 'error' ? 'bg-red-500' : '',
                        notification.type === 'warning' ? 'bg-yellow-500' : '',
                        notification.type === 'info' ? 'bg-blue-500' : ''
                      ]"
                    ></div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm text-primary font-medium">{{ notification.title }}</p>
                      <p class="text-xs text-secondary mt-0.5">{{ notification.message }}</p>
                      <p class="text-xs text-muted mt-1">{{ formatTime(notification.timestamp) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User Menu -->
          <div class="relative">
            <button
              @click="toggleUserMenu"
              class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-card transition-colors"
              aria-label="User menu"
            >
              <div class="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-white text-sm font-medium">
                {{ userInitials }}
              </div>
              <ChevronDownIcon class="w-4 h-4 text-slate-900 dark:text-slate-300 hidden sm:block" />
            </button>

            <!-- User Dropdown -->
            <div
              v-if="showUserMenu"
              ref="userMenuDropdown"
              class="absolute right-0 mt-2 w-56 bg-card rounded-lg shadow-lg border border-border-color py-2 z-50"
            >
              <div class="px-4 py-3 border-b border-gray-200">
                <p class="text-sm font-semibold text-primary">{{ user?.username || 'Guest' }}</p>
                <p class="text-xs text-muted mt-0.5">{{ user?.email || '' }}</p>
              </div>
              <div class="py-1">
                <router-link
                  to="/profile"
                  class="flex items-center px-4 py-2 text-sm text-slate-900 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                  @click="closeUserMenu"
                >
                  <UserIcon class="w-4 h-4 mr-3 text-slate-900 dark:text-slate-300" />
                  Profile
                </router-link>
                <router-link
                  to="/security"
                  class="flex items-center px-4 py-2 text-sm text-slate-900 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                  @click="closeUserMenu"
                >
                  <ShieldCheckIcon class="w-4 h-4 mr-3 text-slate-900 dark:text-slate-300" />
                  Security
                </router-link>
                <router-link
                  to="/sessions"
                  class="flex items-center px-4 py-2 text-sm text-slate-900 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                  @click="closeUserMenu"
                >
                  <DevicePhoneMobileIcon class="w-4 h-4 mr-3 text-slate-900 dark:text-slate-300" />
                  Sessions
                </router-link>
                <div class="border-t border-border-color my-1"></div>
                <button
                  @click="handleLogout"
                  class="w-full flex items-center px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                >
                  <ArrowRightOnRectangleIcon class="w-4 h-4 mr-3 text-red-600 dark:text-red-400" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Bars3Icon,
  BoltIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  BellIcon,
  UserIcon,
  ShieldCheckIcon,
  DevicePhoneMobileIcon,
  ArrowRightOnRectangleIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// UI State
const showNotifications = ref(false)
const showUserMenu = ref(false)
const apiStatus = ref('connected')
const notificationsDropdown = ref(null)
const userMenuDropdown = ref(null)

// Environment (can be from env variable)
const environment = ref(null) // 'production', 'staging', 'development', or null

// Notifications (TODO: Replace with backend API integration)
// Currently using mock data for UI display only
// Backend should provide: GET /api/notifications/ endpoint
const notifications = ref([
  {
    id: 1,
    title: 'Screen Updated',
    message: 'Screen "Main Hall" has been updated successfully',
    type: 'success',
    read: false,
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    title: 'API Warning',
    message: 'High latency detected on API endpoint',
    type: 'warning',
    read: false,
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  }
])

const unreadNotifications = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

// User initials
const user = computed(() => authStore.user)
const userInitials = computed(() => {
  if (!user.value?.username) return 'G'
  const parts = user.value.username.split(' ')
  if (parts.length > 1) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return user.value.username.substring(0, 2).toUpperCase()
})

// Breadcrumb generation
const breadcrumbs = computed(() => {
  const paths = route.path.split('/').filter(Boolean)
  const crumbs = []
  
  // Skip dashboard from breadcrumb if it's the only path
  if (paths.length <= 1 && paths[0] === 'dashboard') {
    return []
  }

  let currentPath = ''
  paths.forEach((path, index) => {
    currentPath += `/${path}`
    
    // Skip dashboard from breadcrumb
    if (path === 'dashboard') return
    
    // Generate label from path
    const label = path
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
    
    crumbs.push({
      path: currentPath,
      label: label
    })
  })
  
  return crumbs
})

// Toggle functions
const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
  if (showNotifications.value) {
    showUserMenu.value = false
  }
}

const closeNotifications = () => {
  showNotifications.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  if (showUserMenu.value) {
    showNotifications.value = false
  }
}

const closeUserMenu = () => {
  showUserMenu.value = false
}

// Click outside handler
const handleClickOutside = (event) => {
  // Check if click is outside notifications dropdown
  if (showNotifications.value && notificationsDropdown.value) {
    const button = event.target.closest('button[aria-label="Notifications"]')
    if (!notificationsDropdown.value.contains(event.target) && !button) {
      closeNotifications()
    }
  }
  
  // Check if click is outside user menu dropdown
  if (showUserMenu.value && userMenuDropdown.value) {
    const button = event.target.closest('button[aria-label="User menu"]')
    if (!userMenuDropdown.value.contains(event.target) && !button) {
      closeUserMenu()
    }
  }
}

// Notification handlers
const handleNotificationClick = (notification) => {
  // Mark as read
  notification.read = true
  // Navigate if needed
  // router.push(notification.link)
}

const markAllAsRead = () => {
  notifications.value.forEach(n => n.read = true)
}

const formatTime = (date) => {
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

// API Status check
const checkApiStatus = async () => {
  try {
    const response = await fetch('/api/health', { 
      method: 'GET',
      signal: AbortSignal.timeout(3000)
    })
    apiStatus.value = response.ok ? 'connected' : 'disconnected'
  } catch (error) {
    apiStatus.value = 'disconnected'
  }
}

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}

let apiCheckInterval = null

onMounted(() => {
  checkApiStatus()
  apiCheckInterval = setInterval(checkApiStatus, 30000) // Check every 30 seconds
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (apiCheckInterval) {
    clearInterval(apiCheckInterval)
  }
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Sticky navbar */
nav {
  backdrop-filter: blur(8px);
}
</style>
