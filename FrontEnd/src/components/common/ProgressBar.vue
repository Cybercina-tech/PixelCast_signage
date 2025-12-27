<template>
  <div :class="containerClasses">
    <div v-if="label || showPercentage" class="flex items-center justify-between mb-2">
      <span v-if="label" :class="labelClasses">{{ label }}</span>
      <span v-if="showPercentage" :class="percentageClasses">{{ percentage }}%</span>
    </div>
    <div :class="barContainerClasses">
      <div
        :class="barClasses"
        :style="{ width: `${percentage}%` }"
        :aria-valuenow="percentage"
        :aria-valuemin="0"
        :aria-valuemax="100"
        role="progressbar"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  percentage: {
    type: Number,
    required: true,
    validator: (value) => value >= 0 && value <= 100,
  },
  label: {
    type: String,
    default: '',
  },
  showPercentage: {
    type: Boolean,
    default: true,
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'danger'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  animated: {
    type: Boolean,
    default: true,
  },
})

const containerClasses = computed(() => {
  return 'w-full'
})

const labelClasses = computed(() => {
  return 'text-sm font-medium text-slate-700 dark:text-slate-300'
})

const percentageClasses = computed(() => {
  return 'text-sm font-medium text-slate-600 dark:text-slate-400'
})

const barContainerClasses = computed(() => {
  const base = 'w-full rounded-full overflow-hidden'
  
  const sizes = {
    sm: 'h-1.5',
    md: 'h-2',
    lg: 'h-3',
  }
  
  return [
    base,
    sizes[props.size],
    'bg-slate-200 dark:bg-slate-700',
  ].join(' ')
})

const barClasses = computed(() => {
  const base = 'h-full rounded-full transition-all duration-500'
  
  const variants = {
    primary: 'bg-slate-900 dark:bg-slate-600',
    success: 'bg-green-600 dark:bg-green-500',
    warning: 'bg-yellow-600 dark:bg-yellow-500',
    danger: 'bg-red-600 dark:bg-red-500',
  }
  
  const animation = props.animated ? 'ease-out' : ''
  
  return [
    base,
    variants[props.variant],
    animation,
  ].join(' ')
})
</script>

