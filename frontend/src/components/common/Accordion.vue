<template>
  <div :class="containerClasses">
    <button
      :class="headerClasses"
      @click="toggle"
      :aria-expanded="isOpen"
      :aria-controls="`accordion-content-${id}`"
    >
      <span class="flex-1 text-left">{{ title }}</span>
      <ChevronDownIcon
        :class="iconClasses"
        :style="{ transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }"
      />
    </button>
    <Transition name="accordion">
      <div
        v-show="isOpen"
        :id="`accordion-content-${id}`"
        :class="contentClasses"
      >
        <slot></slot>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  defaultOpen: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: () => `accordion-${Math.random().toString(36).substr(2, 9)}`,
  },
})

const isOpen = ref(props.defaultOpen)

const toggle = () => {
  isOpen.value = !isOpen.value
}

const containerClasses = computed(() => {
  return 'border border-slate-200 dark:border-slate-700 rounded-lg overflow-hidden bg-white dark:bg-slate-800'
})

const headerClasses = computed(() => {
  return 'w-full flex items-center justify-between px-4 py-3 text-left font-medium text-slate-900 dark:text-slate-100 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors focus:outline-none focus:ring-2 focus:ring-slate-500 focus:ring-inset'
})

const iconClasses = computed(() => {
  return 'w-5 h-5 text-slate-500 dark:text-slate-400 transition-transform duration-200'
})

const contentClasses = computed(() => {
  return 'px-4 py-3 text-slate-700 dark:text-slate-300 border-t border-slate-200 dark:border-slate-700'
})
</script>

<style scoped>
.accordion-enter-active,
.accordion-leave-active {
  transition: max-height 0.3s ease-out, opacity 0.3s ease-out;
  overflow: hidden;
}

.accordion-enter-from,
.accordion-leave-to {
  max-height: 0;
  opacity: 0;
}

.accordion-enter-to,
.accordion-leave-from {
  max-height: 1000px;
  opacity: 1;
}
</style>

