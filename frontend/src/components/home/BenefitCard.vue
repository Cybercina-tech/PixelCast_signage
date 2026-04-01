<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 20 }"
    :visible="{ opacity: 1, y: 0 }"
    :delay="delay"
    class="group relative p-8 bg-white rounded-2xl border-2 border-neutral-200 hover-lift hover:border-orange-500 transition-all duration-300 ease-out overflow-hidden"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-orange-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    
    <div class="relative z-10">
      <div class="mb-6">
        <div class="w-14 h-14 rounded-xl bg-orange-100 flex items-center justify-center group-hover:bg-orange-500 transition-colors duration-300">
          <component :is="icon" class="w-7 h-7 text-orange-600 group-hover:text-white icon-hover transition-colors" />
        </div>
      </div>
      
      <h3 class="text-xl font-bold text-neutral-900 mb-3 leading-tight group-hover:text-orange-600 transition-colors">
        {{ title }}
      </h3>
      
      <p class="text-neutral-600 leading-relaxed">
        {{ description }}
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    required: true
  },
  delay: {
    type: Number,
    default: 0
  }
})
</script>
