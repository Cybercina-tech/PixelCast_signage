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
        :src="ensureAbsoluteUrl(content.secure_url)"
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
import { ensureAbsoluteUrl } from '@/utils/url'

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
    left: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'visible'
  }
})

/**
 * Image style with responsive object-fit
 * CRITICAL FIX: Changed default from 'contain' to 'cover'
 * 'contain' creates empty black spaces when aspect ratios don't match
 * 'cover' fills entire widget area, cropping edges if needed (no black bars)
 */
const imageStyle = computed(() => {
  const contentJson = props.widget.content_json || {}
  // CRITICAL: Default to 'cover' instead of 'contain' to prevent black spaces
  // User can still override via content_json.objectFit if needed
  const objectFit = contentJson.objectFit || 'cover'
  
  return {
    width: '100%',
    height: '100%',
    objectFit: objectFit,
    display: 'block',
    // Center the image (important for cover mode - centers the crop area)
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
    
    // Enhanced error logging with full details
    const errorDetails = {
      contentId: contentId,
      attemptedUrl: img.src,
      widgetId: props.widget.id,
      widgetName: props.widget.name,
      widgetType: props.widget.type,
      content: props.widget.contents?.find(c => c.id === contentId),
      error: event.type,
      timestamp: new Date().toISOString()
    }
    
    console.error(`[ImageWidget] Failed to load image for content: ${contentId}`, errorDetails)
    
    // Log the full URL that failed
    console.error(`[ImageWidget] Broken image URL: ${img.src}`)
    
    // Check if URL is relative vs absolute
    if (!img.src.startsWith('http://') && !img.src.startsWith('https://')) {
      console.warn(`[ImageWidget] Image URL is relative, might need absolute URL: ${img.src}`)
    }
  }
}
</script>

<style scoped>
.image-widget {
  width: 100%;
  height: 100%;
  position: relative;
  /* CRITICAL FIX: Transparent background instead of black
     With object-fit: cover, images fill widget completely, so background shouldn't show
     But if it does show (e.g., during loading), transparent is better than black */
  background-color: transparent;
}

.content-item {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
  /* CRITICAL: Use flexbox to center image content */
  display: flex;
  align-items: center;
  justify-content: center;
  /* CRITICAL FIX: Transparent background
     With object-fit: cover, images fill completely, so no black spaces
     Transparent ensures no visible background if image doesn't cover perfectly */
  background-color: transparent;
  overflow: visible;
}

.content-image {
  width: 100%;
  height: 100%;
  /* CRITICAL FIX: Changed from 'contain' to 'cover'
     'contain' creates empty black spaces when aspect ratios don't match widget
     'cover' fills entire widget, cropping edges if needed (eliminates black spaces) */
  object-fit: cover;
  display: block;
  /* CRITICAL: Center the image both horizontally and vertically
     object-position centers the crop area in cover mode
     This ensures image is perfectly centered in widget container */
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
  /* Prevent layout shifts but allow content overflow */
  contain: layout style;
  /* Ensure image fills widget completely */
  max-width: 100%;
  max-height: 100%;
}
</style>

