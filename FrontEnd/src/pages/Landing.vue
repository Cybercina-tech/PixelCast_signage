<template>
  <div class="min-h-screen bg-gradient-to-br from-indigo-50 to-white">
    <Navbar />
    <div class="container mx-auto px-4 py-16">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-4">ScreenGram</h1>
        <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          A comprehensive digital signage management system for controlling and monitoring display screens remotely.
        </p>
        <div class="flex justify-center gap-4">
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/login"
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Login
          </router-link>
          <router-link
            v-if="!authStore.isAuthenticated"
            to="/signup"
            class="px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition"
          >
            Sign Up
          </router-link>
          <router-link
            v-else
            to="/dashboard"
            class="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Go to Dashboard
          </router-link>
        </div>
      </div>
      
      <!-- Features Section -->
      <div class="grid md:grid-cols-3 gap-8 mb-16">
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-semibold mb-2">Screen Management</h3>
          <p class="text-gray-600">Manage and monitor all your digital displays from a central dashboard.</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-semibold mb-2">Content Control</h3>
          <p class="text-gray-600">Upload, organize, and schedule content across all your screens.</p>
        </div>
        <div class="bg-white p-6 rounded-lg shadow">
          <h3 class="text-xl font-semibold mb-2">Real-time Monitoring</h3>
          <p class="text-gray-600">Track screen status, health metrics, and content delivery in real-time.</p>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/home/Navbar.vue'
import Footer from '@/components/home/Footer.vue'

const authStore = useAuthStore()
</script>
