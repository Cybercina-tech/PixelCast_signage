<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 30 }"
    :visible="{ opacity: 1, y: 0 }"
    :transition="{ duration: 500, delay }"
    class="group p-6 border border-slate-200 rounded-xl hover:border-slate-300 hover:shadow-lg transition-all duration-300 bg-white"
  >
    <div class="w-12 h-12 rounded-lg bg-slate-100 group-hover:bg-slate-900 mb-4 flex items-center justify-center transition-colors duration-300">
      <component :is="icon" class="w-6 h-6 text-slate-600 group-hover:text-white transition-colors" />
    </div>
    <h3 class="text-xl font-semibold text-slate-900 mb-3">{{ title }}</h3>
    <p class="text-slate-600 leading-relaxed">{{ description }}</p>
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

