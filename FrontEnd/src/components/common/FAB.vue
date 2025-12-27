<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="fabClasses"
    @click="handleClick"
    :aria-label="ariaLabel || label"
    v-bind="$attrs"
  >
    <component v-if="icon" :is="icon" :class="iconClasses" />
    <span v-else>{{ label }}</span>
    <span v-if="tooltip" :class="tooltipClasses">{{ tooltip }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: [Object, String],
    default: null,
  },
  label: {
    type: String,
    default: '+',
  },
  tooltip: {
    type: String,
    default: '',
  },
  position: {
    type: String,
    default: 'bottom-right',
    validator: (value) => ['bottom-right', 'bottom-left', 'top-right', 'top-left'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'danger'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  ariaLabel: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'button',
  },
})

const emit = defineEmits(['click'])

const handleClick = (event) => {
  if (!props.disabled) {
    emit('click', event)
  }
}

const fabClasses = computed(() => {
  const base = 'fixed z-50 rounded-full shadow-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center'
  
  const sizes = {
    sm: 'w-12 h-12',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  }
  
  const positions = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  }
  
  const variants = {
    primary: 'bg-slate-900 text-white hover:bg-slate-800 active:bg-slate-950 focus:ring-slate-500 dark:bg-slate-700 dark:hover:bg-slate-600',
    secondary: 'bg-slate-100 text-slate-900 hover:bg-slate-200 active:bg-slate-300 focus:ring-slate-500 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700',
    success: 'bg-green-600 text-white hover:bg-green-700 active:bg-green-800 focus:ring-green-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 active:bg-red-800 focus:ring-red-500',
  }
  
  return [
    base,
    sizes[props.size],
    positions[props.position],
    variants[props.variant],
    !props.disabled && 'hover:scale-110 active:scale-95 hover:shadow-xl',
  ].filter(Boolean).join(' ')
})

const iconClasses = computed(() => {
  const sizes = {
    sm: 'w-6 h-6',
    md: 'w-7 h-7',
    lg: 'w-8 h-8',
  }
  return sizes[props.size]
})

const tooltipClasses = computed(() => {
  const base = 'absolute whitespace-nowrap px-3 py-1.5 text-sm font-medium text-white bg-slate-900 rounded-lg shadow-lg opacity-0 pointer-events-none transition-opacity duration-200'
  
  const positions = {
    'bottom-right': 'right-full mr-2 bottom-1/2 translate-y-1/2',
    'bottom-left': 'left-full ml-2 bottom-1/2 translate-y-1/2',
    'top-right': 'right-full mr-2 top-1/2 -translate-y-1/2',
    'top-left': 'left-full ml-2 top-1/2 -translate-y-1/2',
  }
  
  return [
    base,
    positions[props.position],
    'group-hover:opacity-100',
  ].join(' ')
})
</script>

<style scoped>
button:hover span:last-child {
  opacity: 1;
}
</style>

