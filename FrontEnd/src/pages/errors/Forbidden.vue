<template>
  <AppLayout>
    <div class="min-h-screen flex items-center justify-center px-4">
      <div class="text-center">
        <ShieldExclamationIcon class="mx-auto h-24 w-24 text-red-400 dark:text-red-500" />
        <h1 class="text-6xl font-bold text-gray-300 dark:text-gray-400 mt-4">403</h1>
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mt-4">Forbidden</h2>
        <p class="text-gray-600 dark:text-gray-300 mt-4 mb-8">
          You don't have permission to access this resource.
        </p>
        <div class="space-x-4">
          <router-link
            to="/dashboard"
            class="inline-block px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600 transition"
          >
            Go to Dashboard
          </router-link>
          <button
            @click="$router.go(-1)"
            class="inline-block px-6 py-3 bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ShieldExclamationIcon } from '@heroicons/vue/24/outline'
import AppLayout from '@/components/layout/AppLayout.vue'
</script>
