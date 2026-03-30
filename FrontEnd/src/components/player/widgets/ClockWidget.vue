<template>
  <div class="clock-widget" :style="clockStyle">
    {{ formattedValue }}
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

const now = ref(new Date())
let timerId = null

const formatPattern = computed(() => {
  const raw = props.widget?.content_json?.format || props.widget?.content || 'HH:mm:ss'
  return typeof raw === 'string' && raw.trim() ? raw.trim() : 'HH:mm:ss'
})

const clockStyle = computed(() => {
  const style = props.widget?.content_json || {}
  const resolvedFontSize = typeof style.fontSize === 'number'
    ? `${style.fontSize}px`
    : (typeof style.fontSize === 'string' && style.fontSize.trim() ? style.fontSize : '48px')
  return {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: style.textAlign === 'right' ? 'flex-end' : style.textAlign === 'left' ? 'flex-start' : 'center',
    color: style.color || '#ffffff',
    fontSize: resolvedFontSize,
    fontFamily: style.fontFamily || 'Arial, sans-serif',
    backgroundColor: style.backgroundColor || 'transparent',
    padding: '12px',
    boxSizing: 'border-box',
    textAlign: style.textAlign || 'center'
  }
})

const pad2 = (n) => String(n).padStart(2, '0')

const formattedValue = computed(() => {
  const d = now.value
  const tokenMap = {
    YYYY: String(d.getFullYear()),
    MM: pad2(d.getMonth() + 1),
    DD: pad2(d.getDate()),
    HH: pad2(d.getHours()),
    mm: pad2(d.getMinutes()),
    ss: pad2(d.getSeconds())
  }
  let value = formatPattern.value
  Object.entries(tokenMap).forEach(([k, v]) => {
    value = value.replaceAll(k, v)
  })
  return value
})

onMounted(() => {
  timerId = setInterval(() => {
    now.value = new Date()
  }, 1000)
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})
</script>

<style scoped>
.clock-widget {
  user-select: none;
  overflow: hidden;
  white-space: nowrap;
}
</style>
