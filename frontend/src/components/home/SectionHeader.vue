<template>
  <div class="text-center mb-16">
    <h2
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :visible="{ opacity: 1, y: 0 }"
      :delay="delay"
      class="text-4xl md:text-5xl font-bold text-neutral-900 dark:text-neutral-50 mb-4 tracking-tight leading-tight"
    >
      {{ title }}
    </h2>
    <p
      v-if="subtitle"
      v-motion
      :initial="{ opacity: 0, y: 20 }"
      :visible="{ opacity: 1, y: 0 }"
      :delay="delay + 100"
      class="text-lg md:text-xl text-neutral-600 dark:text-neutral-400 max-w-3xl mx-auto leading-relaxed"
    >
      {{ subtitle }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  delay: {
    type: Number,
    default: 0
  }
})
</script>
