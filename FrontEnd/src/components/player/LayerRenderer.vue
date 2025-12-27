<template>
  <div
    class="layer"
    :style="layerStyle"
  >
    <WidgetRenderer
      v-for="widget in sortedWidgets"
      :key="widget.id"
      :widget="widget"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import WidgetRenderer from './WidgetRenderer.vue'

const props = defineProps({
  layer: {
    type: Object,
    required: true
  }
})

/**
 * Layer style with absolute positioning
 * All dimensions scale proportionally via parent transform
 */
const layerStyle = computed(() => {
  const { x = 0, y = 0, width = 0, height = 0, z_index = 0, background_color, opacity } = props.layer
  
  // Safety checks for dimensions
  const safeWidth = width > 0 ? width : 100
  const safeHeight = height > 0 ? height : 100
  const safeOpacity = opacity !== undefined && opacity !== null ? Math.max(0, Math.min(1, opacity)) : 1
  
  // Warn if dimensions are invalid
  if (width <= 0 || height <= 0) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has invalid dimensions: ${width}x${height}`, props.layer)
  }
  
  // Warn if opacity is 0 (layer will be invisible)
  if (safeOpacity === 0) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has opacity 0 (invisible)`, props.layer)
  }
  
  return {
    position: 'absolute',
    left: `${x}px`,
    top: `${y}px`,
    width: `${safeWidth}px`,
    height: `${safeHeight}px`,
    zIndex: z_index,
    backgroundColor: background_color || 'transparent',
    opacity: safeOpacity,
    overflow: 'hidden',
    // Hardware acceleration for smooth rendering
    transform: 'translateZ(0)',
    WebkitTransform: 'translateZ(0)',
    // Prevent layout shifts
    contain: 'layout style paint',
    // Ensure layer is visible
    visibility: 'visible',
    display: 'block'
  }
})

// Sort widgets by z_index for proper rendering order
// Filter only active widgets (safety check - backend should already filter)
const sortedWidgets = computed(() => {
  if (!props.layer.widgets || !Array.isArray(props.layer.widgets)) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has no widgets array`)
    return []
  }
  
  // Filter active widgets and sort by z_index
  const widgets = [...props.layer.widgets]
    .filter(widget => widget.is_active !== false) // Only render active widgets
    .sort((a, b) => {
      const zA = a.z_index || 0
      const zB = b.z_index || 0
      if (zA !== zB) return zA - zB
      return (a.name || '').localeCompare(b.name || '')
    })
  
  if (widgets.length === 0) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} (${props.layer.name}) has no active widgets`, {
      totalWidgets: props.layer.widgets.length,
      widgets: props.layer.widgets.map(w => ({ id: w.id, name: w.name, is_active: w.is_active }))
    })
  } else {
    console.log(`[LayerRenderer] Layer ${props.layer.id} rendering ${widgets.length} widgets`, {
      layerName: props.layer.name,
      widgets: widgets.map(w => ({ id: w.id, name: w.name, type: w.type, contentsCount: w.contents?.length || 0 }))
    })
  }
  
  return widgets
})
</script>

<style scoped>
.layer {
  position: absolute;
  /* Ensure layers render correctly with scaling */
  will-change: transform;
  backface-visibility: hidden;
}
</style>

