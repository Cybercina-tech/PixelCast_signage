<template>
  <section :id="id" class="scroll-mt-28">
    <div
      class="rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-5 sm:p-6 lg:p-8 shadow-lg shadow-black/10 space-y-4"
    >
      <h2 class="text-lg sm:text-xl font-bold text-white border-b border-white/10 pb-3 mb-1">
        {{ title }}
      </h2>
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  id: { type: String, required: true },
  title: { type: String, required: true },
})
</script>
