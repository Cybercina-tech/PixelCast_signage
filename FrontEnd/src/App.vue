<template>
  <div class="h-screen w-screen overflow-hidden">
    <RouterView />
    <NotificationContainer />
    <DeleteConfirmation />
  </div>
</template>

<script setup>
import { onBeforeMount, onMounted, watch } from 'vue'
import { RouterView, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'
import { useSidebarStore } from './stores/sidebar'
import { useNotificationStore } from './stores/notification'
import NotificationContainer from './components/common/NotificationContainer.vue'
import DeleteConfirmation from './components/common/DeleteConfirmation.vue'

const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const sidebarStore = useSidebarStore()
const notificationStore = useNotificationStore()

// Initialize notification store (ensure it's reactive)
// This ensures the store is properly initialized when the app starts

// Initialize theme BEFORE component mounts to prevent flash
onBeforeMount(() => {
  themeStore.initTheme()
})

onMounted(async () => {
  // Skip auth initialization on player route (player uses its own authentication)
  if (route.name !== 'player') {
    // Initialize auth state on app startup (restore session if token exists)
    await authStore.initialize()
    
    // Initialize sidebar items if user is authenticated
    if (authStore.isAuthenticated && authStore.user) {
      await sidebarStore.fetchSidebarItems()
    }
  }
})

// Watch for user changes and update sidebar (skip on player route)
watch(() => authStore.user, async (newUser) => {
  // Skip sidebar updates on player route
  if (route.name === 'player') return
  
  if (newUser) {
    await sidebarStore.fetchSidebarItems()
  } else {
    sidebarStore.clearSidebarItems()
  }
})
</script>
