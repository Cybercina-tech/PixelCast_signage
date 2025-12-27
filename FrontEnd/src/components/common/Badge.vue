<template>
  <span :class="badgeClasses" v-bind="$attrs">
    <component v-if="icon" :is="icon" :class="iconClasses" />
    <slot></slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  icon: {
    type: [Object, String],
    default: null,
  },
  dot: {
    type: Boolean,
    default: false,
  },
})

const badgeClasses = computed(() => {
  const base = 'inline-flex items-center gap-1.5 font-medium rounded-full'
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }
  
  const variants = {
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300',
    primary: 'bg-slate-900 text-white dark:bg-slate-700',
    success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  }
  
  return [
    base,
    sizes[props.size],
    variants[props.variant],
  ].join(' ')
})

const iconClasses = computed(() => {
  const sizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  }
  return sizes[props.size]
})
</script>

