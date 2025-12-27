<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
    :aria-label="ariaLabel || label"
    v-bind="$attrs"
  >
    <span v-if="loading" class="flex items-center justify-center">
      <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>
    <component v-else :is="icon" :class="iconClasses" />
    <span v-if="badge" class="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-600 rounded-full">
      {{ badge }}
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: {
    type: [Object, String],
    required: true,
  },
  variant: {
    type: String,
    default: 'ghost',
    validator: (value) => ['ghost', 'primary', 'secondary', 'danger', 'success'].includes(value),
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  badge: {
    type: [String, Number],
    default: null,
  },
  label: {
    type: String,
    default: '',
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
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}

const buttonClasses = computed(() => {
  const base = 'relative inline-flex items-center justify-center rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const sizes = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-11 h-11',
  }
  
  const variants = {
    ghost: 'text-slate-600 hover:bg-slate-100 active:bg-slate-200 focus:ring-slate-500 dark:text-slate-400 dark:hover:bg-slate-800 dark:active:bg-slate-700',
    primary: 'bg-slate-900 text-white hover:bg-slate-800 active:bg-slate-950 focus:ring-slate-500 dark:bg-slate-700 dark:hover:bg-slate-600',
    secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200 active:bg-slate-300 focus:ring-slate-500 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
    danger: 'text-red-600 hover:bg-red-50 active:bg-red-100 focus:ring-red-500 dark:text-red-400 dark:hover:bg-red-900/20 dark:active:bg-red-900/30',
    success: 'text-green-600 hover:bg-green-50 active:bg-green-100 focus:ring-green-500 dark:text-green-400 dark:hover:bg-green-900/20 dark:active:bg-green-900/30',
  }
  
  return [
    base,
    sizes[props.size],
    variants[props.variant],
    !props.disabled && !props.loading && 'hover:scale-105 active:scale-95',
  ].filter(Boolean).join(' ')
})

const iconClasses = computed(() => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }
  return sizes[props.size]
})
</script>

