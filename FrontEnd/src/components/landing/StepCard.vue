<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 30 }"
    :visible="{ opacity: 1, y: 0 }"
    :transition="{ duration: 500, delay }"
    class="relative"
  >
    <!-- Connector line (desktop only) -->
    <div
      v-if="showConnector"
      class="hidden md:block absolute top-12 left-full h-0.5 bg-slate-200 -z-10"
      style="width: calc(100% + 2rem); margin-left: 2rem;"
    >
      <div class="absolute right-0 top-1/2 transform -translate-y-1/2 -translate-x-1/2 w-3 h-3 bg-slate-900 rounded-full"></div>
    </div>
    
    <div class="bg-white p-8 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-300 text-center">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-900 text-white text-xl font-bold mb-6">
        {{ number }}
      </div>
      <div class="w-12 h-12 mx-auto mb-4 text-slate-600">
        <component :is="icon" />
      </div>
      <h3 class="text-xl font-semibold text-slate-900 mb-3">{{ title }}</h3>
      <p class="text-slate-600 leading-relaxed">{{ description }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  number: {
    type: Number,
    required: true,
  },
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  icon: {
    type: [Function, Object],
    required: true,
    validator: (value) => {
      // Accept Vue component (Function) or component definition (Object)
      return typeof value === 'function' || (typeof value === 'object' && value !== null)
    },
  },
  delay: {
    type: Number,
    default: 0,
  },
  showConnector: {
    type: Boolean,
    default: false,
  },
})
</script>

