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

const widgetStyle = computed(() => {
  const {
    x = 0,
    y = 0,
    width = 100,
    height = 100,
    z_index = 0,
    content_json = {},
  } = props.widget
  const rotation = Number(content_json.rotation || content_json.rotate || 0) || 0

  return {
    position: 'absolute',
    left: `${Number(x) || 0}px`,
    top: `${Number(y) || 0}px`,
    width: `${Math.max(1, Number(width) || 1)}px`,
    height: `${Math.max(1, Number(height) || 1)}px`,
    zIndex: z_index,
    transform: rotation ? `rotate(${rotation}deg)` : undefined,
    transformOrigin: 'center center',
    overflow: 'hidden',
    visibility: 'visible',
    opacity: 1,
    display: 'block',
  }
})
</script>

<style scoped>
.widget {
  position: absolute;
  box-sizing: border-box;
  will-change: transform;
  backface-visibility: hidden;
  overflow: hidden;
}
</style>

