<template>
  <div class="widget-preview w-full h-full">
    <!-- Text Widget -->
    <TextWidget
      v-if="widget.type === 'text'"
      :widget="playerWidget"
    />

    <MarqueeWidget
      v-else-if="widget.type === 'marquee'"
      :widget="playerWidget"
    />

    <!-- Image Widget -->
    <ImageWidget
      v-else-if="widget.type === 'image'"
      :widget="playerWidget"
    />

    <!-- Video Widget -->
    <VideoWidget
      v-else-if="widget.type === 'video'"
      :widget="playerWidget"
    />

    <div
      v-else-if="widget.type === 'webview'"
      class="w-full h-full bg-slate-900 text-slate-200 border border-slate-700 rounded p-3 flex flex-col justify-center"
    >
      <div class="text-xs uppercase tracking-wide text-slate-400 mb-2">Webview Preview</div>
      <div class="text-sm break-all">{{ webviewPreviewUrl || 'No URL set' }}</div>
      <div class="text-[11px] text-slate-500 mt-2">Live iframe is disabled in editor preview to avoid browser cross-origin focus warnings.</div>
    </div>

    <ChartWidget
      v-else-if="widget.type === 'chart'"
      :widget="playerWidget"
    />

    <!-- Clock Widget -->
    <div v-else-if="widget.type === 'clock'" class="clock-widget-preview" :style="clockStyle">
      {{ currentTime }}
    </div>

    <!-- Date Widget -->
    <div v-else-if="widget.type === 'date'" class="date-widget-preview" :style="dateStyle">
      {{ currentDate }}
    </div>

    <!-- Default/Unknown Widget -->
    <div v-else class="default-widget-preview flex items-center justify-center w-full h-full bg-gray-300 text-gray-600 text-sm">
      {{ widget.type }}
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import TextWidget from '@/components/player/widgets/TextWidget.vue'
import MarqueeWidget from '@/components/player/widgets/MarqueeWidget.vue'
import ImageWidget from '@/components/player/widgets/ImageWidget.vue'
import VideoWidget from '@/components/player/widgets/VideoWidget.vue'
import ChartWidget from '@/components/player/widgets/ChartWidget.vue'
import { fromWidgetChartPayload } from '@/utils/chartConfig'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

const currentTime = ref(new Date().toLocaleTimeString())
const currentDate = ref(new Date().toLocaleDateString())
let timeInterval = null

const normalizeFontSize = (value, fallbackPx) => {
  if (value === undefined || value === null || value === '') return `${fallbackPx}px`
  if (typeof value === 'number') return `${value}px`
  const raw = String(value).trim()
  if (!raw) return `${fallbackPx}px`
  if (raw.endsWith('px') || raw.endsWith('rem') || raw.endsWith('em') || raw.endsWith('%')) return raw
  const parsed = Number.parseFloat(raw)
  return Number.isFinite(parsed) ? `${parsed}px` : `${fallbackPx}px`
}

const getPreviewText = (widget, style) => {
  if (widget.type !== 'text' && widget.type !== 'marquee') return ''
  const raw = widget.content || style.text || ''
  return typeof raw === 'string' ? raw : ''
}

// Convert editor widget format to player widget format
const playerWidget = computed(() => {
  const widget = props.widget
  const style = widget.style || {}
  const normalizedChart = widget.type === 'chart' ? fromWidgetChartPayload(widget) : null
  const previewText = getPreviewText(widget, style)
  
  // Create a player-compatible widget object
  // Player widgets expect: widget.content_json (for styles) and widget.contents[] (for content data)
  const playerFormat = {
    id: widget.id,
    type: widget.type,
    name: widget.name,
    // content_json contains widget-level style/configuration
    content_json: {
      // Text widget style properties
      color: style.color,
      fontSize: style.fontSize,
      fontFamily: style.fontFamily,
      textAlign: style.textAlign,
      backgroundColor: style.backgroundColor,
      fontWeight: style.fontWeight,
      lineHeight: style.lineHeight,
      // Image/Video widget style properties
      objectFit: style.objectFit,
      // Chart config is passed to player chart renderer
      chart: normalizedChart,
      // Ensure marquee settings are fully forwarded.
      ...style,
    },
    // contents array contains the actual content items
    contents: previewText || (widget.type !== 'text' && widget.type !== 'marquee' && widget.content) ? [{
      id: `preview-content-${widget.id}`,
      name: widget.name || 'Preview Content',
      is_active: true,
      order: 0,
      // Text content
      text_content: (widget.type === 'text' || widget.type === 'marquee') ? previewText : undefined,
      // Image/Video content URL
      secure_url: (widget.type === 'image' || widget.type === 'video') ? widget.content : undefined,
      // Webview URL
      file_url: widget.type === 'webview' ? widget.content : undefined,
      // Content-level JSON (can override widget-level styles)
      content_json: {
        ...style,
        chart: normalizedChart
      }
    }] : []
  }
  
  return playerFormat
})

const webviewPreviewUrl = computed(() => {
  if (props.widget.type !== 'webview') return ''
  return props.widget.content || ''
})

// Clock widget style
const clockStyle = computed(() => {
  const style = props.widget.style || {}
  return {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: style.color || '#ffffff',
    fontSize: normalizeFontSize(style.fontSize, 56),
    fontFamily: style.fontFamily || 'Arial, sans-serif',
    textAlign: style.textAlign || 'center',
    backgroundColor: style.backgroundColor || '#000000',
    padding: '10px',
    boxSizing: 'border-box'
  }
})

// Date widget style
const dateStyle = computed(() => {
  const style = props.widget.style || {}
  return {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: style.color || '#ffffff',
    fontSize: normalizeFontSize(style.fontSize, 40),
    fontFamily: style.fontFamily || 'Arial, sans-serif',
    textAlign: style.textAlign || 'center',
    backgroundColor: style.backgroundColor || '#000000',
    padding: '10px',
    boxSizing: 'border-box'
  }
})

// Update time for clock widget
const updateTime = () => {
  if (props.widget.type === 'clock') {
    const format = props.widget.content || 'HH:mm:ss'
    const timeZone = props.widget.style?.timeZone || 'UTC'
    const now = new Date()

    try {
      if (format.includes('HH')) {
        currentTime.value = now.toLocaleTimeString('en-US', {
          hour12: false,
          timeZone,
        })
      } else {
        currentTime.value = now.toLocaleTimeString('en-US', {
          timeZone,
        })
      }
    } catch {
      // Fallback if an invalid timezone is provided.
      currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
    }
  }
}

// Update date for date widget
const updateDate = () => {
  if (props.widget.type === 'date') {
    const format = props.widget.content || 'YYYY-MM-DD'
    const now = new Date()
    
    if (format.includes('YYYY')) {
      currentDate.value = now.toISOString().split('T')[0]
    } else {
      currentDate.value = now.toLocaleDateString()
    }
  }
}

onMounted(() => {
  if (props.widget.type === 'clock') {
    updateTime()
    timeInterval = setInterval(updateTime, 1000)
  } else if (props.widget.type === 'date') {
    updateDate()
    timeInterval = setInterval(updateDate, 60000) // Update every minute
  }
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.widget-preview {
  pointer-events: none;
  width: 100%;
  height: 100%;
}

.clock-widget-preview,
.date-widget-preview {
  user-select: none;
}
</style>

