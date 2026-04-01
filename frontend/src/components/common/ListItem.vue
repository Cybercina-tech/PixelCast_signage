<template>
  <div
    :class="itemClasses"
    @click="handleClick"
    v-bind="$attrs"
  >
    <div v-if="selectable" class="flex-shrink-0">
      <CheckboxButton
        :model-value="selected"
        @update:model-value="handleSelect"
        size="sm"
        :aria-label="`Select ${title}`"
      />
    </div>
    <div v-if="icon" class="flex-shrink-0">
      <div :class="iconContainerClasses">
        <component :is="icon" :class="iconClasses" />
      </div>
    </div>
    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between">
        <h4 :class="titleClasses">{{ title }}</h4>
        <div v-if="$slots.actions" class="flex items-center gap-2">
          <slot name="actions"></slot>
        </div>
      </div>
      <p v-if="description" :class="descriptionClasses">{{ description }}</p>
      <div v-if="$slots.meta" class="mt-2">
        <slot name="meta"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import CheckboxButton from './CheckboxButton.vue'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, String],
    default: null,
  },
  selectable: {
    type: Boolean,
    default: false,
  },
  selected: {
    type: Boolean,
    default: false,
  },
  clickable: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['click', 'select'])

const handleClick = () => {
  if (props.clickable) {
    emit('click')
  }
}

const handleSelect = (value) => {
  emit('select', value)
}

const itemClasses = computed(() => {
  const base = 'flex items-start gap-3 p-4 rounded-lg border transition-all duration-200'
  
  const state = props.selected
    ? 'border-slate-900 bg-slate-50 dark:border-slate-600 dark:bg-slate-800/50'
    : 'border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800'
  
  const hover = props.clickable && !props.selected
    ? 'hover:border-slate-300 hover:shadow-md dark:hover:border-slate-600'
    : ''
  
  const cursor = props.clickable ? 'cursor-pointer' : ''
  
  return [base, state, hover, cursor].filter(Boolean).join(' ')
})

const iconContainerClasses = computed(() => {
  return 'w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-700 flex items-center justify-center'
})

const iconClasses = computed(() => {
  return 'w-5 h-5 text-slate-600 dark:text-slate-400'
})

const titleClasses = computed(() => {
  return 'text-base font-semibold text-slate-900 dark:text-slate-100'
})

const descriptionClasses = computed(() => {
  return 'mt-1 text-sm text-slate-600 dark:text-slate-400'
})
</script>

