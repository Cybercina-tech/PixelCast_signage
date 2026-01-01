<template>
  <div
    class="layer"
    :style="layerStyle"
  >
    <WidgetRenderer
      v-for="widget in sortedWidgets"
      :key="widget.id"
      :widget="widget"
      :template-width="props.templateWidth"
      :template-height="props.templateHeight"
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
  },
  templateWidth: {
    type: Number,
    default: 1920
  },
  templateHeight: {
    type: Number,
    default: 1080
  }
})

/**
 * Layer style with absolute positioning
 * CRITICAL FIX: Container is now 100vw x 100vh with no scale
 * Layers must use percentage dimensions to fill container properly
 * Pixel dimensions are converted to percentages based on template dimensions
 */
const layerStyle = computed(() => {
  const { x = 0, y = 0, width = 0, height = 0, z_index = 0, background_color, opacity } = props.layer
  
  // CRITICAL: Since template-container is 100vw x 100vh (no scale),
  // we need to convert pixel dimensions to percentages
  // Template dimensions define the "coordinate system" - convert pixels to % of template
  
  // If layer matches template dimensions (or close), use 100%
  // Small dimensions (< 200px) are also treated as placeholders
  const MIN_REALISTIC_SIZE = 200
  const TOLERANCE = 10 // Pixels - allow small differences
  
  const matchesTemplateWidth = Math.abs(width - props.templateWidth) <= TOLERANCE
  const matchesTemplateHeight = Math.abs(height - props.templateHeight) <= TOLERANCE
  const isPlaceholder = (
    width <= 0 || 
    height <= 0 || 
    width < MIN_REALISTIC_SIZE || 
    height < MIN_REALISTIC_SIZE ||
    (width === 100 && height === 100)
  )
  
  // Convert pixel dimensions to percentages
  // If layer matches template or is placeholder, use 100%
  // Otherwise convert pixels to % based on template dimensions
  let layerWidth, layerHeight, layerLeft, layerTop
  
  if (matchesTemplateWidth || isPlaceholder) {
    layerWidth = '100%'
    layerLeft = '0%'
  } else {
    // Convert pixel to percentage: (pixel / template) * 100
    layerWidth = `${(width / props.templateWidth) * 100}%`
    layerLeft = `${(x / props.templateWidth) * 100}%`
  }
  
  if (matchesTemplateHeight || isPlaceholder) {
    layerHeight = '100%'
    layerTop = '0%'
  } else {
    // Convert pixel to percentage: (pixel / template) * 100
    layerHeight = `${(height / props.templateHeight) * 100}%`
    layerTop = `${(y / props.templateHeight) * 100}%`
  }
  
  const safeOpacity = opacity !== undefined && opacity !== null ? Math.max(0, Math.min(1, opacity)) : 1
  
  // Warn if dimensions are invalid or suspiciously small
  if (width <= 0 || height <= 0) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has invalid dimensions: ${width}x${height}`, props.layer)
  } else if (width < MIN_REALISTIC_SIZE || height < MIN_REALISTIC_SIZE) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has suspiciously small dimensions: ${width}x${height}. Using 100%.`, props.layer)
  }
  
  // Warn if opacity is 0 (layer will be invisible)
  if (safeOpacity === 0) {
    console.warn(`[LayerRenderer] Layer ${props.layer.id} has opacity 0 (invisible)`, props.layer)
  }
  
  return {
    position: 'absolute',
    left: layerLeft,
    top: layerTop,
    // CRITICAL: Use percentage dimensions to fill 100vw x 100vh container
    // This ensures layer fills container properly without scaling
    width: layerWidth,
    height: layerHeight,
    zIndex: z_index,
    backgroundColor: background_color || 'transparent',
    opacity: safeOpacity,
    // CRITICAL: overflow: visible allows images larger than layer to render fully
    overflow: 'visible',
    // Hardware acceleration for smooth rendering
    transform: 'translateZ(0)',
    WebkitTransform: 'translateZ(0)',
    // CRITICAL: Remove 'contain' property that might clip content
    contain: 'layout style',
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
  /* CRITICAL: Ensure overflow is visible to prevent image clipping */
  /* Do not set overflow: hidden here - it will clip high-resolution images */
  overflow: visible !important;
}
</style>

