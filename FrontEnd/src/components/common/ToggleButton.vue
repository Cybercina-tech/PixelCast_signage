<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="buttonClasses"
    @click="handleToggle"
    :aria-pressed="modelValue"
    :aria-label="ariaLabel || label"
    v-bind="$attrs"
  >
    <span v-if="label && labelPosition === 'left'" class="mr-2">{{ label }}</span>
    <div :class="toggleClasses">
      <span :class="toggleDotClasses"></span>
    </div>
    <span v-if="label && labelPosition === 'right'" class="ml-2">{{ label }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
  labelPosition: {
    type: String,
    default: 'right',
    validator: (value) => ['left', 'right'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'danger', 'warning'].includes(value),
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

const emit = defineEmits(['update:modelValue', 'change'])

const handleToggle = () => {
  if (!props.disabled) {
    const newValue = !props.modelValue
    emit('update:modelValue', newValue)
    emit('change', newValue)
  }
}

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed'
  
  return [
    base,
    props.disabled ? '' : 'cursor-pointer',
  ].filter(Boolean).join(' ')
})

const toggleClasses = computed(() => {
  const base = 'relative inline-flex items-center rounded-full transition-colors duration-200 focus:outline-none'
  
  const sizes = {
    sm: 'h-4 w-7',
    md: 'h-6 w-11',
    lg: 'h-7 w-14',
  }
  
  const variants = {
    primary: props.modelValue
      ? 'bg-slate-900 dark:bg-slate-700'
      : 'bg-slate-300 dark:bg-slate-600',
    success: props.modelValue
      ? 'bg-green-600 dark:bg-green-700'
      : 'bg-slate-300 dark:bg-slate-600',
    danger: props.modelValue
      ? 'bg-red-600 dark:bg-red-700'
      : 'bg-slate-300 dark:bg-slate-600',
    warning: props.modelValue
      ? 'bg-yellow-600 dark:bg-yellow-700'
      : 'bg-slate-300 dark:bg-slate-600',
  }
  
  return [
    base,
    sizes[props.size],
    variants[props.variant],
  ].join(' ')
})

const toggleDotClasses = computed(() => {
  const base = 'inline-block rounded-full bg-white shadow-lg transform transition-transform duration-200'
  
  const sizes = {
    sm: 'h-3 w-3',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  }
  
  const positions = {
    sm: props.modelValue ? 'translate-x-3' : 'translate-x-0',
    md: props.modelValue ? 'translate-x-5' : 'translate-x-0',
    lg: props.modelValue ? 'translate-x-7' : 'translate-x-0',
  }
  
  return [
    base,
    sizes[props.size],
    positions[props.size],
  ].join(' ')
})
</script>

