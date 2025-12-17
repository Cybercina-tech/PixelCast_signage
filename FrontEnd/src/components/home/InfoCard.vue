<template>
  <div
    v-motion
    :initial="{ opacity: 0, y: 20 }"
    :visible="{ opacity: 1, y: 0 }"
    :delay="delay"
    class="group p-6 bg-neutral-50 dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800 hover-lift hover:bg-white dark:hover:bg-neutral-950 hover:border-neutral-300 dark:hover:border-neutral-700 hover:shadow-md transition-all duration-300 ease-out"
  >
    <h3 class="font-semibold text-lg text-neutral-900 dark:text-neutral-50 mb-2 leading-tight">
      {{ title }}
    </h3>
    <p class="text-neutral-600 dark:text-neutral-400 leading-relaxed text-[15px]">
      {{ description }}
    </p>
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
  delay: {
    type: Number,
    default: 0
  }
})
</script>
