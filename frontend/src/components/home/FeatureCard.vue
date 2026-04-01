<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 30 }"
    :visible="{ opacity: 1, y: 0 }"
    :delay="delay"
    class="group relative bg-white rounded-2xl p-8 shadow-lg border-2 border-neutral-200 card-hover overflow-hidden"
  >
    <div class="absolute top-0 right-0 w-32 h-32 bg-orange-100 rounded-full -mr-16 -mt-16 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
    
    <div class="relative z-10">
      <div class="flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-orange-500 to-orange-600 mb-6 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3 shadow-lg shadow-orange-500/30">
        <component :is="icon" class="w-8 h-8 text-white icon-hover" />
      </div>
      
      <h3 class="text-2xl font-bold text-neutral-900 mb-3 leading-tight group-hover:text-orange-600 transition-colors">
        {{ title }}
      </h3>
      
      <p class="text-neutral-600 leading-relaxed text-base">
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
    type: [Function, Object],
    required: true
  },
  delay: {
    type: Number,
    default: 0
  }
})
</script>
