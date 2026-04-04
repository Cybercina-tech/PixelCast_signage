<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 30 }"
    :visible="{ opacity: 1, y: 0 }"
    :transition="{ duration: 500, delay }"
    class="bg-slate-800/60 backdrop-blur-sm p-8 rounded-xl border border-slate-700/50 hover:border-slate-600 transition-all duration-300 hover:bg-slate-800/80"
  >
    <div class="flex items-start">
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center">
          <component :is="icon" class="w-5 h-5 text-white" />
        </div>
      </div>
      <div class="ml-4 flex-1">
        <h3 class="text-xl font-semibold mb-4 text-white">{{ title }}</h3>
        <p class="text-on-starfield leading-relaxed">{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
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
})
</script>

