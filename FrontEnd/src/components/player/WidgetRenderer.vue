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
    
    <!-- Video Widget -->
    <VideoWidget
      v-if="widget.type === 'video'"
      :widget="widget"
    />

    <ClockWidget
      v-if="widget.type === 'clock'"
      :widget="widget"
    />

    <WebviewWidget
      v-if="widget.type === 'webview'"
      :widget="widget"
    />

    <ChartWidget
      v-if="widget.type === 'chart'"
      :widget="widget"
    />
    
    <!-- Warn if widget type is not recognized -->
    <div v-if="!['image','text','video','clock','webview','chart'].includes(widget.type)" class="widget-error" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
      Unknown widget type: {{ widget.type }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import ImageWidget from './widgets/ImageWidget.vue'
import TextWidget from './widgets/TextWidget.vue'
import VideoWidget from './widgets/VideoWidget.vue'
import ClockWidget from './widgets/ClockWidget.vue'
import WebviewWidget from './widgets/WebviewWidget.vue'
import ChartWidget from './widgets/ChartWidget.vue'

const props = defineProps({
  widget: {
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
 * CRITICAL FIX: Widgets ALWAYS fill 100% of their parent layer
 * This ensures widgets fill entire screen without gaps or black spaces
 * Pixel dimensions from backend are ignored - widget always uses 100% × 100%
 * 
 * IMPORTANT: Video widgets specifically bypass any fixed pixel/percentage widths
 * (like 52% or 1000px) and always occupy 100% of the parent layer's space
 */
const widgetStyle = computed(() => {
  const { z_index = 0 } = props.widget
  
  // CRITICAL: Widgets must ALWAYS be 100% × 100% to fill entire layer/screen
  // We ignore pixel dimensions from backend (x, y, width, height)
  // Widget should fill the entire parent layer, which fills the entire screen
  // Video widgets specifically bypass fixed widths/percentages and use 100% × 100%
  
  console.log(`[WidgetRenderer] Widget ${props.widget.id} using 100% × 100% to fill entire screen`, {
    widgetId: props.widget.id,
    widgetName: props.widget.name,
    widgetType: props.widget.type,
    zIndex: z_index
  })
  
  return {
    position: 'absolute',
    // CRITICAL: Widget must start at (0, 0) to fill entire parent layer
    // Since widget is 100% × 100%, it fills entire container naturally
    left: '0',
    top: '0',
    // CRITICAL: Always use 100% × 100% to fill entire parent layer
    // This ensures widget fills entire screen without gaps
    // Video widgets bypass any fixed pixel/percentage widths and use 100% × 100%
    width: '100%',
    height: '100%',
    zIndex: z_index,
    // CRITICAL: overflow: visible allows images/videos larger than widget to render fully
    overflow: 'visible',
    // Hardware acceleration
    transform: 'translateZ(0)',
    WebkitTransform: 'translateZ(0)',
    // CRITICAL: Remove 'paint' from contain to allow content overflow
    contain: 'layout style',
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
  /* CRITICAL: Force widget to always fill entire parent layer (100% × 100%) */
  /* Use !important to override any inline styles or computed styles that might try to set pixel values */
  /* Video widgets specifically bypass fixed pixel/percentage widths (52%, 1000px, etc.) and use 100% × 100% */
  width: 100% !important;
  height: 100% !important;
  left: 0 !important;
  top: 0 !important;
  /* Ensure widgets render correctly */
  will-change: transform;
  backface-visibility: hidden;
  /* CRITICAL: Ensure overflow is visible to prevent image/video clipping */
  /* Do not set overflow: hidden here - it will clip high-resolution content */
  overflow: hidden !important; /* Prevent content bleed-out with object-fit: contain */
}

/* Global styles to force object-fit: contain on all images and videos in player */
.widget img,
.widget video {
  object-fit: contain !important;
  object-position: center center !important;
}
</style>

