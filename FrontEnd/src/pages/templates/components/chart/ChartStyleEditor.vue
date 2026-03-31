<template>
  <div class="space-y-3">
    <h4 class="text-xs font-semibold uppercase text-gray-400">Chart Options</h4>

    <div class="grid grid-cols-2 gap-3">
      <label class="text-[11px] text-gray-400 flex items-center gap-2">
        <input type="checkbox" :checked="legendDisplay" @change="updateLegendDisplay($event.target.checked)" />
        Show Legend
      </label>
      <label class="text-[11px] text-gray-400">
        Legend Position
        <select class="select-base w-full px-2 py-1 mt-1 text-xs" :value="legendPosition" @change="updateLegendPosition($event.target.value)">
          <option value="top">Top</option>
          <option value="bottom">Bottom</option>
          <option value="left">Left</option>
          <option value="right">Right</option>
        </select>
      </label>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <label class="text-[11px] text-gray-400">
        Title
        <input class="input-base w-full px-2 py-1 mt-1 text-xs" :value="titleText" @input="updateTitle($event.target.value)" placeholder="Chart title" />
      </label>
      <label class="text-[11px] text-gray-400 flex items-center gap-2 mt-5">
        <input type="checkbox" :checked="titleDisplay" @change="updateTitleDisplay($event.target.checked)" />
        Show Title
      </label>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <label class="text-[11px] text-gray-400 flex items-center gap-2">
        <input type="checkbox" :checked="xGridDisplay" @change="updateXGrid($event.target.checked)" />
        X Grid
      </label>
      <label class="text-[11px] text-gray-400 flex items-center gap-2">
        <input type="checkbox" :checked="yGridDisplay" @change="updateYGrid($event.target.checked)" />
        Y Grid
      </label>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  options: {
    type: Object,
    default: () => ({}),
  },
})

const emit = defineEmits(['update:options'])

const getWithFallback = (getter, fallback) => {
  try {
    const value = getter()
    return value === undefined ? fallback : value
  } catch {
    return fallback
  }
}

const legendDisplay = computed(() => getWithFallback(() => props.options.plugins.legend.display, true))
const legendPosition = computed(() => getWithFallback(() => props.options.plugins.legend.position, 'top'))
const titleDisplay = computed(() => getWithFallback(() => props.options.plugins.title.display, false))
const titleText = computed(() => getWithFallback(() => props.options.plugins.title.text, ''))
const xGridDisplay = computed(() => getWithFallback(() => props.options.scales.x.grid.display, true))
const yGridDisplay = computed(() => getWithFallback(() => props.options.scales.y.grid.display, true))

const cloneOptions = () => {
  const options = props.options && typeof props.options === 'object' ? props.options : {}
  return JSON.parse(JSON.stringify(options))
}

const patchOptions = (mutator) => {
  const next = cloneOptions()
  mutator(next)
  emit('update:options', next)
}

const updateLegendDisplay = (value) => patchOptions((next) => {
  next.plugins = next.plugins || {}
  next.plugins.legend = next.plugins.legend || {}
  next.plugins.legend.display = value
})

const updateLegendPosition = (value) => patchOptions((next) => {
  next.plugins = next.plugins || {}
  next.plugins.legend = next.plugins.legend || {}
  next.plugins.legend.position = value
})

const updateTitleDisplay = (value) => patchOptions((next) => {
  next.plugins = next.plugins || {}
  next.plugins.title = next.plugins.title || {}
  next.plugins.title.display = value
})

const updateTitle = (value) => patchOptions((next) => {
  next.plugins = next.plugins || {}
  next.plugins.title = next.plugins.title || {}
  next.plugins.title.text = value
})

const updateXGrid = (value) => patchOptions((next) => {
  next.scales = next.scales || {}
  next.scales.x = next.scales.x || {}
  next.scales.x.grid = next.scales.x.grid || {}
  next.scales.x.grid.display = value
})

const updateYGrid = (value) => patchOptions((next) => {
  next.scales = next.scales || {}
  next.scales.y = next.scales.y || {}
  next.scales.y.grid = next.scales.y.grid || {}
  next.scales.y.grid.display = value
})
</script>
