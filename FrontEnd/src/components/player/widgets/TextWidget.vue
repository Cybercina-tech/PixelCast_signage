<template>
  <div class="text-widget">
    <div
      v-for="content in sortedContents"
      :key="content.id"
      class="content-item"
      :style="contentStyle"
    >
      <div
        class="text-content"
        :style="textStyle"
        :data-content-id="content.id"
      >
        {{ displayText(content) }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

// Sort contents by order
// Filter only active content (safety check - backend should already filter)
const sortedContents = computed(() => {
  if (!props.widget.contents) {
    console.warn(`[TextWidget] Widget ${props.widget.id} has no contents array`)
    return []
  }
  
  // Filter active content and sort by order
  const contents = [...props.widget.contents]
    .filter(content => content.is_active !== false) // Only render active content
    .sort((a, b) => (a.order || 0) - (b.order || 0))
  
  if (contents.length === 0) {
    console.warn(`[TextWidget] Widget ${props.widget.id} has no active contents`, {
      totalContents: props.widget.contents.length,
      contents: props.widget.contents.map(c => ({ id: c.id, name: c.name, is_active: c.is_active }))
    })
  } else {
    console.log(`[TextWidget] Widget ${props.widget.id} rendering ${contents.length} contents`, {
      contents: contents.map(c => ({ id: c.id, name: c.name, hasText: !!(c.text_content || c.content_json?.text) }))
    })
  }
  
  return contents
})

// Get display text from content
const displayText = (content) => {
  // Priority: text_content > content_json.text > file_url (if text file)
  if (content.text_content) {
    return content.text_content
  }
  if (content.content_json?.text) {
    return content.content_json.text
  }
  // If file_url exists, it might be a text file URL, but we can't load it here
  // The backend should provide the text content in text_content or content_json
  console.warn(`[TextWidget] Content ${content.id} has no text content`, content)
  return '[No text content]'
}

// Content container style
const contentStyle = computed(() => {
  return {
    width: '100%',
    height: '100%',
    position: 'absolute',
    top: 0,
    left: 0
  }
})

/**
 * Text style based on widget configuration
 */
const textStyle = computed(() => {
  const widgetJson = props.widget.content_json || {}
  const fontFamily = widgetJson.fontFamily || 'Arial, sans-serif'
  const fontSize = widgetJson.fontSize || props.widget.font_size || 16
  const color = widgetJson.color || props.widget.color || '#000000'
  const textAlign = widgetJson.textAlign || props.widget.alignment || 'left'
  const fontWeight = widgetJson.fontWeight || 'normal'
  const lineHeight = widgetJson.lineHeight || 1.5
  
  return {
    width: '100%',
    height: '100%',
    fontFamily: fontFamily,
    fontSize: `${fontSize}px`,
    color: color,
    textAlign: textAlign,
    fontWeight: fontWeight,
    lineHeight: lineHeight,
    padding: '10px',
    boxSizing: 'border-box',
    overflow: 'hidden',
    wordWrap: 'break-word',
    whiteSpace: 'pre-wrap', // Preserve line breaks and spaces
    display: 'flex',
    alignItems: textAlign === 'center' ? 'center' : textAlign === 'right' ? 'flex-end' : 'flex-start',
    justifyContent: textAlign === 'center' ? 'center' : textAlign === 'right' ? 'flex-end' : 'flex-start'
  }
})
</script>

<style scoped>
.text-widget {
  width: 100%;
  height: 100%;
  position: relative;
}

.content-item {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

.text-content {
  width: 100%;
  height: 100%;
  /* Hardware acceleration for smooth rendering */
  backface-visibility: hidden;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform;
  /* Prevent text selection */
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
  /* Prevent layout shifts */
  contain: layout style paint;
}
</style>

