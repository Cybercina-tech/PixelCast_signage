<template>
  <div class="webview-widget">
    <iframe
      v-if="safeUrl"
      :src="safeUrl"
      class="webview-frame"
      sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
      referrerpolicy="no-referrer"
      loading="lazy"
    />
    <div v-else class="webview-error">
      Invalid webview URL
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ensureAbsoluteUrl } from '@/utils/url'

const props = defineProps({
  widget: {
    type: Object,
    required: true
  }
})

const rawUrl = computed(() => {
  const firstContent = props.widget?.contents?.[0]
  return (
    firstContent?.secure_url ||
    firstContent?.file_url ||
    props.widget?.content_url ||
    props.widget?.content_json?.url ||
    props.widget?.content ||
    ''
  )
})

const safeUrl = computed(() => {
  if (!rawUrl.value) return null
  try {
    const absolute = ensureAbsoluteUrl(rawUrl.value)
    const parsed = new URL(absolute, window.location.origin)
    if (!['http:', 'https:'].includes(parsed.protocol)) return null
    return parsed.toString()
  } catch {
    return null
  }
})
</script>

<style scoped>
.webview-widget {
  width: 100%;
  height: 100%;
  background: #111827;
}

.webview-frame {
  width: 100%;
  height: 100%;
  border: 0;
}

.webview-error {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
}
</style>
