<template>
  <div
    v-motion
    :initial="{ opacity: 0, scale: 0.9 }"
    :visible="{ opacity: 1, scale: 1 }"
    :delay="delay"
    class="group inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 hover-lift hover:bg-white/20 hover:border-orange-400 hover:shadow-lg hover:shadow-orange-500/20 transition-all duration-300 ease-out cursor-default"
  >
    <component v-if="icon" :is="icon" class="w-5 h-5 text-white icon-hover group-hover:text-orange-300" />
    <span class="text-base font-semibold text-white group-hover:text-orange-300 transition-colors">{{ name }}</span>
  </div>
</template>

<script setup>
defineProps({
  name: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    default: null
  },
  delay: {
    type: Number,
    default: 0
  }
})
</script>
