<template>
  <div
    v-if="shouldRenderRoot"
    class="countdown-widget"
    :class="themeClass"
    :style="containerStyle"
  >
    <div v-if="invalidTarget" class="cd-zero cd-warn">
      Set a valid target date and time
    </div>
    <template v-else-if="!isFinished">
      <div v-if="eventTitle" class="cd-title">{{ eventTitle }}</div>
      <div class="cd-units" :class="{ 'cd-units--tight': mode === 'hms' }">
        <template v-if="mode === 'dh'">
          <div class="cd-unit">
            <span class="cd-num">{{ parts.d }}</span>
            <span class="cd-lbl">{{ labels.days }}</span>
          </div>
          <div class="cd-unit">
            <span class="cd-num">{{ parts.h }}</span>
            <span class="cd-lbl">{{ labels.hours }}</span>
          </div>
        </template>
        <template v-else>
          <div class="cd-unit">
            <span class="cd-num">{{ parts.hh }}</span>
            <span class="cd-lbl">{{ labels.hours }}</span>
          </div>
          <div class="cd-unit">
            <span class="cd-num">{{ parts.mm }}</span>
            <span class="cd-lbl">{{ labels.minutes }}</span>
          </div>
          <div class="cd-unit">
            <span class="cd-num">{{ parts.ss }}</span>
            <span class="cd-lbl">{{ labels.seconds }}</span>
          </div>
        </template>
      </div>
      <div v-if="showProgressBar" class="cd-progress-wrap" aria-hidden="true">
        <div class="cd-progress-fill" :style="{ width: `${progressPct}%` }" />
      </div>
    </template>
    <div v-else class="cd-zero">
      {{ zeroMessage }}
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { usePlayerStore } from '@/stores/player'

const props = defineProps({
  widget: {
    type: Object,
    required: true,
  },
})

const playerStore = usePlayerStore()
const tick = ref(0)
let timerId = null
const mountedAtMs = ref(null)

const styleJson = computed(() => props.widget?.content_json || {})

const serverOffsetMs = computed(() => Number(playerStore.serverTimeOffsetMs) || 0)

const nowMs = computed(() => {
  tick.value
  return Date.now() + serverOffsetMs.value
})

const targetMs = computed(() => {
  const raw = styleJson.value?.targetAt
  if (!raw) return NaN
  const t = new Date(raw).getTime()
  return Number.isNaN(t) ? NaN : t
})

const invalidTarget = computed(() => Number.isNaN(targetMs.value))

const startMs = computed(() => {
  const raw = styleJson.value?.startAt
  if (raw) {
    const t = new Date(raw).getTime()
    if (!Number.isNaN(t)) return t
  }
  return mountedAtMs.value ?? Date.now()
})

const eventTitle = computed(() => {
  const name = props.widget?.name
  const content = props.widget?.content
  if (typeof content === 'string' && content.trim()) return content.trim()
  if (typeof name === 'string' && name.trim()) return name.trim()
  return ''
})

const labels = computed(() => ({
  days: styleJson.value?.labels?.days || 'Days',
  hours: styleJson.value?.labels?.hours || 'Hours',
  minutes: styleJson.value?.labels?.minutes || 'Minutes',
  seconds: styleJson.value?.labels?.seconds || 'Seconds',
}))

const zeroMode = computed(() => (styleJson.value?.zeroStateMode === 'hideWidget' ? 'hideWidget' : 'showMessage'))

const zeroMessage = computed(() => {
  const m = styleJson.value?.zeroStateMessage
  if (typeof m === 'string' && m.trim()) return m.trim()
  return 'The event has started!'
})

const theme = computed(() => styleJson.value?.theme || 'urgency')

const themeClass = computed(() => ({
  'cd-theme-urgency': theme.value === 'urgency',
  'cd-theme-celebration': theme.value === 'celebration',
  'cd-theme-custom': theme.value === 'custom',
}))

const showProgressBar = computed(() => styleJson.value?.showProgress === true)

const remainingMs = computed(() => {
  if (Number.isNaN(targetMs.value)) return NaN
  return Math.max(0, targetMs.value - nowMs.value)
})

const isFinished = computed(() => {
  if (Number.isNaN(targetMs.value)) return false
  return remainingMs.value <= 0
})

const shouldRenderRoot = computed(() => {
  if (zeroMode.value === 'hideWidget' && isFinished.value) return false
  return true
})

const mode = computed(() => {
  if (Number.isNaN(remainingMs.value)) return 'hms'
  const sec = Math.floor(remainingMs.value / 1000)
  return sec > 86400 ? 'dh' : 'hms'
})

const parts = computed(() => {
  const sec = Number.isNaN(remainingMs.value)
    ? 0
    : Math.max(0, Math.floor(remainingMs.value / 1000))
  const pad = (n) => String(n).padStart(2, '0')
  if (mode.value === 'dh') {
    const d = Math.floor(sec / 86400)
    const h = Math.floor((sec % 86400) / 3600)
    return { d, h, hh: pad(0), mm: pad(0), ss: pad(0) }
  }
  const hh = Math.floor(sec / 3600)
  const mm = Math.floor((sec % 3600) / 60)
  const ss = sec % 60
  return {
    d: 0,
    h: 0,
    hh: pad(hh),
    mm: pad(mm),
    ss: pad(ss),
  }
})

const progressPct = computed(() => {
  if (!showProgressBar.value) return 0
  const end = targetMs.value
  const start = startMs.value
  if (Number.isNaN(end) || end <= start) return 0
  tick.value
  const p = (nowMs.value - start) / (end - start)
  return Math.min(100, Math.max(0, p * 100))
})

const containerStyle = computed(() => {
  const s = styleJson.value
  const fs = typeof s?.fontSize === 'number' ? `${s.fontSize}px` : (s?.fontSize || '32px')
  return {
    width: '100%',
    height: '100%',
    boxSizing: 'border-box',
    padding: '12px 14px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    color: s?.color || '#f8fafc',
    fontSize: fs,
    fontFamily: s?.fontFamily || "'Segoe UI', sans-serif",
    fontWeight: s?.fontWeight || '800',
    textAlign: s?.textAlign || 'center',
    background: s?.backgroundColor || 'transparent',
    borderRadius: s?.borderRadius || '12px',
    textShadow: s?.textShadow || 'none',
    overflow: 'hidden',
  }
})

onMounted(() => {
  mountedAtMs.value = Date.now()
  timerId = window.setInterval(() => {
    tick.value++
  }, 1000)
})

onUnmounted(() => {
  if (timerId) clearInterval(timerId)
})
</script>

<style scoped>
.countdown-widget {
  user-select: none;
  position: relative;
}

.cd-title {
  font-size: 0.45em;
  font-weight: 700;
  opacity: 0.92;
  line-height: 1.2;
  text-align: center;
  max-width: 100%;
}

.cd-units {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: center;
  gap: 0.35em 0.6em;
  width: 100%;
}

.cd-units--tight {
  gap: 0.25em 0.45em;
}

.cd-warn {
  font-size: 0.4em;
  font-weight: 600;
  opacity: 0.9;
}

.cd-unit {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 2.6em;
}

.cd-num {
  font-size: 1em;
  line-height: 1.05;
  font-variant-numeric: tabular-nums;
  letter-spacing: 0.02em;
}

.cd-lbl {
  font-size: 0.28em;
  font-weight: 600;
  opacity: 0.85;
  margin-top: 0.2em;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.cd-progress-wrap {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  overflow: hidden;
  margin-top: 4px;
}

.cd-progress-fill {
  height: 100%;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.85);
  transition: width 1s linear;
}

.cd-zero {
  font-size: 0.55em;
  font-weight: 800;
  text-align: center;
  line-height: 1.35;
  padding: 0.2em;
}

.cd-theme-urgency .cd-num {
  color: inherit;
  text-shadow: 0 0 18px rgba(248, 113, 113, 0.45);
}

.cd-theme-celebration {
  animation: cdCelebrate 3s ease-in-out infinite;
}

.cd-theme-celebration .cd-progress-fill {
  background: linear-gradient(90deg, #fde68a, #fbbf24, #fde68a);
  background-size: 200% 100%;
  animation: cdShimmer 4s linear infinite;
}

@keyframes cdCelebrate {
  0%, 100% { filter: brightness(1); }
  50% { filter: brightness(1.08); }
}

@keyframes cdShimmer {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}
</style>
