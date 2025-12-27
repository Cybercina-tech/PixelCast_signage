<template>
  <div
    class="widget"
    :style="widgetStyle"
  >
    <!-- Debug overlay (remove in production) -->
    <div v-if="false" class="debug-widget-overlay" style="position: absolute; top: 0; left: 0; z-index: 10000; background: rgba(0,255,0,0.1); border: 1px solid green; pointer-events: none; padding: 2px; font-size: 10px; color: white;">
      {{ widget.type }}: {{ widget.name }}
    </div>
    
    <!-- Image Widget -->
    <ImageWidget
      v-if="widget.type === 'image'"
      :widget="widget"
    />
    
    <!-- Text Widget -->
    <TextWidget
      v-if="widget.type === 'text'"
      :widget="widget"
    />
    
    <!-- Placeholder for future widget types -->
    <!-- Video Widget (Phase 3) -->
    
    <!-- Warn if widget type is not recognized -->
    <div v-if="widget.type !== 'image' && widget.type !== 'text'" class="widget-error" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
      Unknown widget type: {{ widget.type }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import ImageWidget from './widgets/ImageWidget.vue'
import TextWidget from './widgets/TextWidget.vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

onMounted(() => {
  console.log(`[WidgetRenderer] Widget ${props.widget.id} (${props.widget.name}) mounted`, {
    type: props.widget.type,
    x: props.widget.x,
    y: props.widget.y,
    width: props.widget.width,
    height: props.widget.height,
    contentsCount: props.widget.contents?.length || 0,
    contents: props.widget.contents?.map(c => ({
      id: c.id,
      name: c.name,
      type: c.type,
      is_active: c.is_active,
      secure_url: c.secure_url ? `${c.secure_url.substring(0, 50)}...` : null
    }))
  })
})

/**
 * Widget style with absolute positioning
 * Scales proportionally with parent layer via CSS transform
 */
const widgetStyle = computed(() => {
  const { x = 0, y = 0, width = 0, height = 0, z_index = 0 } = props.widget
  
  // Safety checks for dimensions
  const safeWidth = width > 0 ? width : 100
  const safeHeight = height > 0 ? height : 100
  
  // Warn if dimensions are invalid
  if (width <= 0 || height <= 0) {
    console.warn(`[WidgetRenderer] Widget ${props.widget.id} has invalid dimensions: ${width}x${height}`, props.widget)
  }
  
  return {
    position: 'absolute',
    left: `${x}px`,
    top: `${y}px`,
    width: `${safeWidth}px`,
    height: `${safeHeight}px`,
    zIndex: z_index,
    overflow: 'hidden',
    // Hardware acceleration
    transform: 'translateZ(0)',
    WebkitTransform: 'translateZ(0)',
    // Prevent layout shifts
    contain: 'layout style paint',
    // Ensure widget is visible
    visibility: 'visible',
    opacity: 1,
    display: 'block'
  }
})
</script>

<style scoped>
.widget {
  position: absolute;
  /* Ensure widgets render correctly with scaling */
  will-change: transform;
  backface-visibility: hidden;
}
</style>

