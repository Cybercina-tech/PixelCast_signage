<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 20 }"
    :visible="{ opacity: 1, y: 0 }"
    :delay="delay"
    class="group relative text-center p-8 bg-white rounded-2xl border-2 border-neutral-200 hover-lift hover:border-orange-500 hover:shadow-xl transition-all duration-300 ease-out overflow-hidden"
  >
    <div class="absolute inset-0 bg-gradient-to-br from-orange-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    
    <div class="relative z-10">
      <div class="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 shadow-lg shadow-orange-500/30">
        <component :is="icon" class="w-10 h-10 text-white icon-hover" />
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
