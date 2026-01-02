<template>
  <div class="widget-preview w-full h-full">
    <!-- Text Widget -->
    <TextWidget
      v-if="widget.type === 'text'"
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
import ImageWidget from '@/components/player/widgets/ImageWidget.vue'
import VideoWidget from '@/components/player/widgets/VideoWidget.vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

const currentTime = ref(new Date().toLocaleTimeString())
const currentDate = ref(new Date().toLocaleDateString())
let timeInterval = null

// Convert editor widget format to player widget format
const playerWidget = computed(() => {
  const widget = props.widget
  const style = widget.style || {}
  
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
    },
    // contents array contains the actual content items
    contents: widget.content ? [{
      id: `preview-content-${widget.id}`,
      name: widget.name || 'Preview Content',
      is_active: true,
      order: 0,
      // Text content
      text_content: widget.type === 'text' ? widget.content : undefined,
      // Image/Video content URL
      secure_url: (widget.type === 'image' || widget.type === 'video') ? widget.content : undefined,
      // Content-level JSON (can override widget-level styles)
      content_json: style
    }] : []
  }
  
  return playerFormat
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
    color: style.color || '#000000',
    fontSize: style.fontSize || '48px',
    fontFamily: style.fontFamily || 'Arial, sans-serif',
    textAlign: style.textAlign || 'center',
    backgroundColor: style.backgroundColor || 'transparent',
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
    color: style.color || '#000000',
    fontSize: style.fontSize || '32px',
    fontFamily: style.fontFamily || 'Arial, sans-serif',
    textAlign: style.textAlign || 'center',
    backgroundColor: style.backgroundColor || 'transparent',
    padding: '10px',
    boxSizing: 'border-box'
  }
})

// Update time for clock widget
const updateTime = () => {
  if (props.widget.type === 'clock') {
    const format = props.widget.content || 'HH:mm:ss'
    const now = new Date()
    
    if (format.includes('HH')) {
      currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
    } else {
      currentTime.value = now.toLocaleTimeString()
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

