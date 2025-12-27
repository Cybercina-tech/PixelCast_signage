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
    <div v-if="showCheckbox" :class="checkboxClasses">
      <CheckIcon v-if="modelValue" class="w-4 h-4 text-white" />
    </div>
    <component v-if="icon && !modelValue" :is="icon" :class="iconClasses" />
    <component v-if="icon && modelValue && checkedIcon" :is="checkedIcon" :class="iconClasses" />
    <span v-if="label" :class="labelClasses">{{ label }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { CheckIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  label: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, String],
    default: null,
  },
  checkedIcon: {
    type: [Object, String],
    default: null,
  },
  showCheckbox: {
    type: Boolean,
    default: true,
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
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'danger'].includes(value),
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
  const base = 'inline-flex items-center gap-2 px-4 py-2 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const sizes = {
    sm: 'text-sm py-1.5 px-3',
    md: 'text-base py-2 px-4',
    lg: 'text-lg py-3 px-6',
  }
  
  const variants = {
    default: props.modelValue
      ? 'border-slate-900 bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-500 dark:border-slate-700 dark:bg-slate-700 dark:hover:bg-slate-600'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
    primary: props.modelValue
      ? 'border-slate-900 bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-500'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-500',
    success: props.modelValue
      ? 'border-green-600 bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-500',
    danger: props.modelValue
      ? 'border-red-600 bg-red-600 text-white hover:bg-red-700 focus:ring-red-500'
      : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 focus:ring-slate-500',
  }
  
  return [
    base,
    sizes[props.size],
    variants[props.variant],
    !props.disabled && 'hover:shadow-md active:scale-[0.98]',
  ].filter(Boolean).join(' ')
})

const checkboxClasses = computed(() => {
  const base = 'flex items-center justify-center rounded border-2 transition-colors'
  
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }
  
  return [
    base,
    sizes[props.size],
    props.modelValue ? 'bg-slate-900 border-slate-900 dark:bg-slate-700 dark:border-slate-700' : 'border-slate-300 dark:border-slate-600',
  ].join(' ')
})

const iconClasses = computed(() => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  }
  return sizes[props.size]
})

const labelClasses = computed(() => {
  return 'font-medium'
})
</script>

