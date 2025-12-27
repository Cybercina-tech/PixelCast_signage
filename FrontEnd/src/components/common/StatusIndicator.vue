<template>
  <div :class="containerClasses">
    <span :class="dotClasses"></span>
    <span v-if="label" :class="labelClasses">{{ label }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: {
    type: String,
    required: true,
    validator: (value) => ['online', 'offline', 'pending', 'error', 'warning', 'success'].includes(value),
  },
  label: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  pulse: {
    type: Boolean,
    default: false,
  },
})

const containerClasses = computed(() => {
  return 'inline-flex items-center gap-2'
})

const dotClasses = computed(() => {
  const base = 'rounded-full'
  
  const sizes = {
    sm: 'w-2 h-2',
    md: 'w-2.5 h-2.5',
    lg: 'w-3 h-3',
  }
  
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-slate-400',
    pending: 'bg-yellow-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    success: 'bg-green-500',
  }
  
  const pulseClass = props.pulse ? 'animate-pulse' : ''
  
  return [
    base,
    sizes[props.size],
    statusColors[props.status],
    pulseClass,
  ].join(' ')
})

const labelClasses = computed(() => {
  const base = 'text-sm font-medium'
  
  const statusColors = {
    online: 'text-green-700 dark:text-green-400',
    offline: 'text-slate-600 dark:text-slate-400',
    pending: 'text-yellow-700 dark:text-yellow-400',
    error: 'text-red-700 dark:text-red-400',
    warning: 'text-yellow-700 dark:text-yellow-400',
    success: 'text-green-700 dark:text-green-400',
  }
  
  return [
    base,
    statusColors[props.status],
  ].join(' ')
})
</script>

