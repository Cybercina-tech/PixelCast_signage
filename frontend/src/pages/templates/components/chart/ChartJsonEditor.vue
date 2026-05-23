<template>
  <div class="space-y-2">
    <h4 class="text-xs font-semibold uppercase text-muted">Advanced JSON</h4>
    <textarea
      :value="modelValue"
      rows="10"
      class="textarea-base w-full px-3 py-2 rounded-lg text-xs text-primary placeholder:text-muted focus:ring-brand/40 font-mono"
      @input="$emit('update:modelValue', $event.target.value)"
    />
    <p v-if="error" class="text-xs text-red-400">{{ error }}</p>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  error: {
    type: String,
    default: '',
  },
})

defineEmits(['update:modelValue'])
</script>
