import { computed, onMounted, onUnmounted, ref, unref } from 'vue'

/**
 * Fit a fixed template pixel size into a container (letterbox / contain), for mini previews and VirtualMonitor.
 */
export function usePreviewContainScale(containerRef, templateWidthRef, templateHeightRef) {
  const containerSize = ref({ width: 400, height: 225 })
  let resizeObserver = null
  let windowResizeHandler = null

  const tw = () => Number(unref(templateWidthRef)) || 1920
  const th = () => Number(unref(templateHeightRef)) || 1080

  const previewScale = computed(() => {
    const w = tw()
    const h = th()
    const cw = Math.max(1, containerSize.value.width)
    const ch = Math.max(1, containerSize.value.height)
    if (w <= 0 || h <= 0) return 1
    return Math.min(cw / w, ch / h) * (1 - 1e-6)
  })

  const clipWrapperStyle = computed(() => {
    const s = previewScale.value
    const W = tw()
    const H = th()
    return {
      width: `${W * s}px`,
      height: `${H * s}px`,
      position: 'relative',
      overflow: 'hidden',
    }
  })

  const innerStageStyle = computed(() => {
    const s = previewScale.value
    const W = tw()
    const H = th()
    return {
      position: 'absolute',
      left: '0',
      top: '0',
      width: `${W}px`,
      height: `${H}px`,
      transform: `scale(${s})`,
      transformOrigin: '0 0',
      willChange: 'transform',
    }
  })

  const bindResize = () => {
    const el = unref(containerRef)
    if (!el) return
    const apply = () => {
      const w = el.clientWidth
      const h = el.clientHeight
      if (w > 0 && h > 0) {
        containerSize.value = { width: w, height: h }
      }
    }
    apply()
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => apply())
      resizeObserver.observe(el)
    } else {
      windowResizeHandler = apply
      window.addEventListener('resize', windowResizeHandler)
    }
  }

  onMounted(() => bindResize())

  onUnmounted(() => {
    resizeObserver?.disconnect()
    resizeObserver = null
    if (windowResizeHandler) {
      window.removeEventListener('resize', windowResizeHandler)
      windowResizeHandler = null
    }
  })

  return {
    containerSize,
    previewScale,
    clipWrapperStyle,
    innerStageStyle,
  }
}
