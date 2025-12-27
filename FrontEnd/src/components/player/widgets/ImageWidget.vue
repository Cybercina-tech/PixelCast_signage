<template>
  <div class="image-widget">
    <div
      v-for="content in sortedContents"
      :key="content.id"
      class="content-item"
      :style="contentStyle"
    >
      <img
        v-if="content.secure_url"
        :src="content.secure_url"
        :alt="content.name || 'Content'"
        :data-content-id="content.id"
        class="content-image"
        :style="imageStyle"
        @load="onImageLoad"
        @error="onImageError"
      />
      <div
        v-else
        class="content-error"
        style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; background: rgba(255,0,0,0.1); color: white; font-size: 12px; padding: 10px; text-align: center;"
      >
        No image URL for content: {{ content.name || content.id }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

const loadedImages = ref(new Set())
const failedImages = ref(new Set())

// Sort contents by order
// Filter only active content (safety check - backend should already filter)
const sortedContents = computed(() => {
  if (!props.widget.contents) {
    console.warn(`[ImageWidget] Widget ${props.widget.id} has no contents array`)
    return []
  }
  
  // Filter active content and sort by order
  const contents = [...props.widget.contents]
    .filter(content => content.is_active !== false) // Only render active content
    .sort((a, b) => (a.order || 0) - (b.order || 0))
  
  if (contents.length === 0) {
    console.warn(`[ImageWidget] Widget ${props.widget.id} has no active contents`, {
      totalContents: props.widget.contents.length,
      contents: props.widget.contents.map(c => ({ id: c.id, name: c.name, is_active: c.is_active, secure_url: c.secure_url }))
    })
  } else {
    console.log(`[ImageWidget] Widget ${props.widget.id} rendering ${contents.length} contents`, {
      contents: contents.map(c => ({ id: c.id, name: c.name, secure_url: c.secure_url ? `${c.secure_url.substring(0, 50)}...` : 'NO URL' }))
    })
  }
  
  return contents
})

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
 * Image style with responsive object-fit
 * Maintains aspect ratio while scaling with widget
 */
const imageStyle = computed(() => {
  const contentJson = props.widget.content_json || {}
  const objectFit = contentJson.objectFit || 'contain'
  
  return {
    width: '100%',
    height: '100%',
    objectFit: objectFit,
    display: 'block',
    // Maintain aspect ratio
    objectPosition: 'center center',
    // Prevent image distortion
    imageRendering: 'auto',
    // Smooth scaling
    imageRendering: '-webkit-optimize-contrast'
  }
})

const onImageLoad = (event) => {
  const img = event.target
  const contentId = img.getAttribute('data-content-id')
  if (contentId) {
    loadedImages.value.add(contentId)
    failedImages.value.delete(contentId)
    console.log(`[ImageWidget] Image loaded successfully for content: ${contentId}`, {
      src: img.src.substring(0, 100),
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight
    })
  }
}

const onImageError = (event) => {
  const img = event.target
  const contentId = img.getAttribute('data-content-id')
  if (contentId) {
    failedImages.value.add(contentId)
    // Hide failed image gracefully without breaking layout
    img.style.display = 'none'
    console.error(`[ImageWidget] Failed to load image for content: ${contentId}`, {
      src: img.src,
      error: event
    })
  }
}
</script>

<style scoped>
.image-widget {
  width: 100%;
  height: 100%;
  position: relative;
  background-color: #000000; /* Black background for TV displays */
}

.content-item {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  background-color: #000000; /* Black background */
}

.content-image {
  width: 100%;
  height: 100%;
  object-fit: contain; /* Maintain aspect ratio, fit within container */
  display: block;
  /* Maintain aspect ratio and prevent distortion */
  object-position: center center;
  /* Hardware acceleration for smooth scaling */
  backface-visibility: hidden;
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform;
  /* Prevent dragging */
  -webkit-user-drag: none;
  -khtml-user-drag: none;
  -moz-user-drag: none;
  -o-user-drag: none;
  user-drag: none;
  pointer-events: auto;
  /* Image rendering optimization */
  image-rendering: auto;
  -webkit-image-rendering: auto;
  /* Prevent layout shifts */
  contain: layout style paint;
  /* Ensure image looks perfect on any TV resolution without stretching */
  max-width: 100%;
  max-height: 100%;
}
</style>

