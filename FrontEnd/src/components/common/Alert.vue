<template>
  <div :class="alertClasses" role="alert" v-bind="$attrs">
    <div class="flex items-start gap-3">
      <component v-if="icon" :is="icon" :class="iconClasses" />
      <div class="flex-1">
        <h4 v-if="title" :class="titleClasses">{{ title }}</h4>
        <p v-if="message" :class="messageClasses">{{ message }}</p>
        <slot></slot>
      </div>
      <button
        v-if="dismissible"
        @click="handleDismiss"
        :class="closeButtonClasses"
        aria-label="Close"
      >
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import {
  InformationCircleIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
} from '@heroicons/vue/24/solid'

const props = defineProps({
  variant: {
    type: String,
    default: 'info',
    validator: (value) => ['info', 'success', 'warning', 'danger'].includes(value),
  },
  title: {
    type: String,
    default: '',
  },
  message: {
    type: String,
    default: '',
  },
  dismissible: {
    type: Boolean,
    default: false,
  },
  icon: {
    type: [Object, String],
    default: null,
  },
})

const emit = defineEmits(['dismiss'])

const handleDismiss = () => {
  emit('dismiss')
}

const defaultIcons = {
  info: InformationCircleIcon,
  success: CheckCircleIcon,
  warning: ExclamationTriangleIcon,
  danger: XCircleIcon,
}

const computedIcon = computed(() => {
  return props.icon || defaultIcons[props.variant]
})

const alertClasses = computed(() => {
  const base = 'rounded-lg border p-4'
  
  const variants = {
    info: 'bg-blue-50 border-blue-200 text-blue-900 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300',
    success: 'bg-green-50 border-green-200 text-green-900 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
    danger: 'bg-red-50 border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
  }
  
  return [
    base,
    variants[props.variant],
  ].join(' ')
})

const iconClasses = computed(() => {
  return 'w-5 h-5 flex-shrink-0 mt-0.5'
})

const titleClasses = computed(() => {
  return 'font-semibold mb-1'
})

const messageClasses = computed(() => {
  return 'text-sm'
})

const closeButtonClasses = computed(() => {
  return 'flex-shrink-0 rounded p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors'
})
</script>

