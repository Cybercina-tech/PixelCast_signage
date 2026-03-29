<template>
  <footer class="bg-slate-950 text-slate-400 py-12 border-t border-slate-800">
    <div class="container mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid md:grid-cols-4 gap-8 mb-8">
        <!-- Product Info -->
        <div class="md:col-span-2">
          <h3 class="text-lg font-bold text-white mb-3">PixelCast Signage</h3>
          <p class="text-sm text-slate-500 leading-relaxed max-w-md">
            Enterprise digital signage management platform for controlling and monitoring displays at scale.
          </p>
        </div>
        
        <!-- Links -->
        <div>
          <h4 class="text-sm font-semibold text-white mb-3 uppercase tracking-wider">Legal</h4>
          <ul class="space-y-2">
            <li>
              <router-link
                to="/privacy"
                class="text-sm hover:text-white transition-colors"
              >
                Privacy Policy
              </router-link>
            </li>
            <li>
              <router-link
                to="/terms"
                class="text-sm hover:text-white transition-colors"
              >
                Terms of Service
              </router-link>
            </li>
          </ul>
        </div>
        
        <div>
          <h4 class="text-sm font-semibold text-white mb-3 uppercase tracking-wider">Support</h4>
          <ul class="space-y-2">
            <li>
              <a
                href="/api/docs"
                class="text-sm hover:text-white transition-colors"
              >
                API Documentation
              </a>
            </li>
            <li>
              <span class="text-sm text-slate-500">Contact Support</span>
            </li>
          </ul>
        </div>
      </div>
      
      <!-- Bottom Bar -->
      <div class="pt-8 border-t border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
        <p class="text-sm text-slate-500">
          © {{ currentYear }} PixelCast Signage. All rights reserved.
        </p>
        <p class="text-xs text-slate-600">
          Version 1.0.0
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'

const currentYear = computed(() => new Date().getFullYear())
</script>

