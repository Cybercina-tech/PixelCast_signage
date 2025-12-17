<template>
  <aside
    :class="[
      'fixed left-0 top-0 h-full bg-gray-900 text-white transition-transform duration-300 z-40',
      isOpen ? 'translate-x-0' : '-translate-x-full',
      'md:translate-x-0 md:static md:z-auto'
    ]"
    class="w-64"
  >
    <div class="flex flex-col h-full">
      <div class="p-4 border-b border-gray-700">
        <h2 class="text-xl font-bold">ScreenGram</h2>
      </div>
      
      <nav class="flex-1 overflow-y-auto p-4">
        <ul class="space-y-2">
          <li v-for="item in menuItems" :key="item.path">
            <router-link
              :to="item.path"
              class="flex items-center px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
              :class="{ 'bg-gray-800': $route.path.startsWith(item.path) }"
            >
              <component :is="item.icon" class="w-5 h-5 mr-3" />
              <span>{{ item.label }}</span>
            </router-link>
          </li>
        </ul>
      </nav>
    </div>
  </aside>
  
  <!-- Overlay for mobile -->
  <div
    v-if="isOpen"
    class="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
    @click="$emit('close')"
  ></div>
</template>

<script setup>
import { ref } from 'vue'
import {
  HomeIcon,
  TvIcon,
  DocumentTextIcon,
  FolderIcon,
  ClockIcon,
  CommandLineIcon,
  UsersIcon,
  DocumentReportIcon,
  Cog6ToothIcon,
} from '@heroicons/vue/24/outline'

defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
})

defineEmits(['close'])

const menuItems = [
  { path: '/dashboard', label: 'Dashboard', icon: HomeIcon },
  { path: '/screens', label: 'Screens', icon: TvIcon },
  { path: '/templates', label: 'Templates', icon: DocumentTextIcon },
  { path: '/contents', label: 'Contents', icon: FolderIcon },
  { path: '/schedules', label: 'Schedules', icon: ClockIcon },
  { path: '/commands', label: 'Commands', icon: CommandLineIcon },
  { path: '/users', label: 'Users & Roles', icon: UsersIcon },
  { path: '/logs', label: 'Logs & Reports', icon: DocumentReportIcon },
  { path: '/settings', label: 'Settings', icon: Cog6ToothIcon },
]
</script>
