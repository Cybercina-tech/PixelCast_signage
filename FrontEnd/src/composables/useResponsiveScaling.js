import { ref, computed } from 'vue'

/**
 * Use the same pixel box for scaling math as for the player clip rect.
 * `100vh`/`100vw` often differ from `innerWidth`/`innerHeight` (scrollbars, mobile UI).
 * `visualViewport` matches what is actually visible when available.
 */
function readViewportSize() {
  if (typeof window === 'undefined') return { width: 1920, height: 1080 }
  const vv = window.visualViewport
  if (vv && vv.width >= 1 && vv.height >= 1) {
    return { width: vv.width, height: vv.height }
  }
  return { width: window.innerWidth, height: window.innerHeight }
}

/**
 * Composable for responsive scaling calculations
 * Handles template scaling to fit any screen size while maintaining aspect ratio
 */
export function useResponsiveScaling(template) {
  const initial = readViewportSize()
  const viewportWidth = ref(initial.width)
  const viewportHeight = ref(initial.height)
  
  // Update viewport dimensions on resize
  const updateViewport = () => {
    const { width, height } = readViewportSize()
    viewportWidth.value = width
    viewportHeight.value = height
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
   * Horizontal-fit mode:
   * - Always fill viewport width completely.
   * - Keep aspect ratio.
   * - Height may letterbox (if shorter) or crop (if taller).
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
    
    const scaleX = viewportWidth.value / templateWidth
    let scale = scaleX
    // Tiny shrink so float math never places the scaled rect 1px past the clip edge.
    scale *= 1 - 1e-6
    
    const finalScale = Math.max(0.01, Math.min(scale, 10))
    
    console.log('[useResponsiveScaling] Scale calculated (fit-width):', {
      templateSize: `${templateWidth}x${templateHeight}`,
      viewportSize: `${viewportWidth.value}x${viewportHeight.value}`,
      scale: finalScale.toFixed(6),
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
  
  // In fit-width mode, X is always anchored to the left edge.
  const offsetX = computed(() => {
    return 0
  })
  
  // Y is centered only when there is extra vertical room; otherwise top-anchored.
  const offsetY = computed(() => {
    if (!template.value) return 0
    const gap = viewportHeight.value - scaledHeight.value
    return Math.max(0, Math.floor(gap * 0.5 * 1000) / 1000)
  })
  
  // Setup resize listener (call from component's onMounted)
  const setupResizeListener = () => {
    updateViewport()
    window.addEventListener('resize', handleResize)
    // Also listen to orientation change for mobile devices
    window.addEventListener('orientationchange', handleResize)
    const vv = window.visualViewport
    if (vv) {
      vv.addEventListener('resize', handleResize)
      vv.addEventListener('scroll', handleResize)
    }
  }
  
  // Cleanup (call from component's onUnmounted)
  const cleanupResizeListener = () => {
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('orientationchange', handleResize)
    const vv = window.visualViewport
    if (vv) {
      vv.removeEventListener('resize', handleResize)
      vv.removeEventListener('scroll', handleResize)
    }
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

