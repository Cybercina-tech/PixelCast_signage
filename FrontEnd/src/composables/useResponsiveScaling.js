import { ref, computed, onMounted, onUnmounted } from 'vue'

/**
 * Composable for responsive scaling calculations
 * Handles template scaling to fit any screen size while maintaining aspect ratio
 */
export function useResponsiveScaling(template) {
  const viewportWidth = ref(window.innerWidth)
  const viewportHeight = ref(window.innerHeight)
  
  // Update viewport dimensions on resize
  const updateViewport = () => {
    viewportWidth.value = window.innerWidth
    viewportHeight.value = window.innerHeight
  }
  
  // Debounced resize handler for performance
  let resizeTimeout = null
  const handleResize = () => {
    if (resizeTimeout) {
      clearTimeout(resizeTimeout)
    }
    resizeTimeout = setTimeout(() => {
      updateViewport()
    }, 100) // 100ms debounce
  }
  
  /**
   * Calculate scale factor to cover entire viewport (no black bars)
   * CRITICAL FIX: Changed from "fit" to "cover" mode
   * This ensures template always fills 100% of viewport, eliminating black borders
   * 
   * IMPORTANT: This scale is used when template-container is 100vw x 100vh
   * Scale is applied to template's natural dimensions (e.g. 1920x1080)
   * to make it cover the entire viewport container
   * 
   * Uses larger scale to cover entire viewport (may crop edges if aspect ratios differ)
   * All nested elements (layers → widgets → content) scale proportionally via CSS transform
   */
  const scaleFactor = computed(() => {
    if (!template.value) return 1
    
    const templateWidth = template.value.width || 1920
    const templateHeight = template.value.height || 1080
    
    // Safety check for invalid dimensions
    if (templateWidth <= 0 || templateHeight <= 0) {
      console.warn('Invalid template dimensions, using default scale')
      return 1
    }
    
    // Safety check for viewport dimensions
    if (viewportWidth.value <= 0 || viewportHeight.value <= 0) {
      console.warn('Invalid viewport dimensions, using default scale')
      return 1
    }
    
    const templateAspectRatio = templateWidth / templateHeight
    const viewportAspectRatio = viewportWidth.value / viewportHeight.value
    
    // CRITICAL FIX: Calculate scale to COVER viewport (not fit)
    // Container is 100vw x 100vh, template needs to scale to cover it completely
    // This uses the larger scale factor to ensure 100% of viewport is filled
    // Similar to CSS object-fit: cover - fills entire container, may crop edges
    let scale
    
    if (templateAspectRatio > viewportAspectRatio) {
      // Template is wider than viewport - cover by height
      // Scale template height to match viewport height
      // May crop left/right edges (no black bars top/bottom)
      scale = viewportHeight.value / templateHeight
    } else {
      // Template is taller than viewport - cover by width  
      // Scale template width to match viewport width
      // May crop top/bottom edges (no black bars left/right)
      scale = viewportWidth.value / templateWidth
    }
    
    // Ensure scale is never negative, zero, or excessively large
    // Clamp between 0.01 (very small) and 10 (very large) for safety
    const finalScale = Math.max(0.01, Math.min(scale, 10))
    
    console.log('[useResponsiveScaling] Scale calculated:', {
      templateSize: `${templateWidth}x${templateHeight}`,
      viewportSize: `${viewportWidth.value}x${viewportHeight.value}`,
      templateAspectRatio: templateAspectRatio.toFixed(3),
      viewportAspectRatio: viewportAspectRatio.toFixed(3),
      scale: finalScale.toFixed(6),
      mode: templateAspectRatio > viewportAspectRatio ? 'cover-by-height' : 'cover-by-width'
    })
    
    return finalScale
  })
  
  // Calculate scaled dimensions
  const scaledWidth = computed(() => {
    if (!template.value) return viewportWidth.value
    return (template.value.width || 1920) * scaleFactor.value
  })
  
  const scaledHeight = computed(() => {
    if (!template.value) return viewportHeight.value
    return (template.value.height || 1080) * scaleFactor.value
  })
  
  // Calculate offset to center template
  const offsetX = computed(() => {
    if (!template.value) return 0
    return (viewportWidth.value - scaledWidth.value) / 2
  })
  
  const offsetY = computed(() => {
    if (!template.value) return 0
    return (viewportHeight.value - scaledHeight.value) / 2
  })
  
  // Setup resize listener (call from component's onMounted)
  const setupResizeListener = () => {
    window.addEventListener('resize', handleResize)
    // Also listen to orientation change for mobile devices
    window.addEventListener('orientationchange', handleResize)
  }
  
  // Cleanup (call from component's onUnmounted)
  const cleanupResizeListener = () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
    if (resizeTimeout) {
      clearTimeout(resizeTimeout)
      resizeTimeout = null
    }
  }
  
  return {
    viewportWidth,
    viewportHeight,
    scaleFactor,
    scaledWidth,
    scaledHeight,
    offsetX,
    offsetY,
    updateViewport,
    setupResizeListener,
    cleanupResizeListener
  }
}

