<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="px-4 py-3 flex items-center justify-between">
      <div class="flex items-center">
        <button
          @click="$emit('toggle-sidebar')"
          class="md:hidden p-2 rounded-lg hover:bg-gray-100"
        >
          <Bars3Icon class="w-6 h-6" />
        </button>
        <h1 class="ml-2 md:ml-0 text-xl font-semibold text-gray-800">
          {{ title }}
        </h1>
      </div>
      
      <div class="flex items-center space-x-4">
        <div class="hidden md:flex items-center space-x-2 text-sm text-gray-600">
          <span>Welcome, {{ user?.username || 'Guest' }}</span>
        </div>
        <button
          @click="handleLogout"
          class="px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Bars3Icon } from '@heroicons/vue/24/outline'
import { useAuthStore } from '@/stores/auth'

defineEmits(['toggle-sidebar'])

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const title = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/screens': 'Screens',
    '/templates': 'Templates',
    '/contents': 'Contents',
    '/schedules': 'Schedules',
    '/commands': 'Commands',
    '/users': 'Users & Roles',
    '/logs': 'Logs & Reports',
    '/settings': 'Settings',
  }
  return titles[route.path] || 'ScreenGram'
})

const user = computed(() => authStore.user)

const handleLogout = () => {
  authStore.logout()
  router.push('/')
}
</script>
