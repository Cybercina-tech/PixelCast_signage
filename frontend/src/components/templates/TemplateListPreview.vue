<template>
  <div class="relative w-full h-full min-h-0 bg-black overflow-hidden">
    <div
      v-if="loading"
      class="absolute inset-0 flex items-center justify-center bg-card z-[1]"
    >
      <div
        class="w-7 h-7 rounded-full border-2 border-border-color border-t-[var(--accent-color,#3b82f6)] animate-spin opacity-80"
      />
    </div>
    <TemplatePreviewStage
      v-else-if="previewTemplate && hasActiveLayers"
      :template="previewTemplate"
    />
    <div
      v-else
      class="absolute inset-0 flex flex-col items-center justify-center p-3 text-center bg-slate-100 dark:bg-slate-900"
    >
      <DocumentTextIcon class="w-8 h-8 text-indigo-400/80 mx-auto mb-2 shrink-0" />
      <p class="text-xs text-primary font-medium truncate max-w-full">
        {{ template.name || 'Untitled' }}
      </p>
      <p class="text-[10px] text-muted mt-1">
        {{ template.width }}×{{ template.height }}
      </p>
      <p v-if="template.id && !loading" class="text-[10px] text-muted mt-0.5">No layers yet</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { DocumentTextIcon } from '@heroicons/vue/24/outline'
import { templatesAPI } from '@/services/api'
import { useTemplatesStore } from '@/stores/templates'
import TemplatePreviewStage from '@/components/screens/TemplatePreviewStage.vue'
import { templateHasRenderablePlayback } from '@/utils/templatePlaybackLayers'

const props = defineProps({
  template: {
    type: Object,
    required: true,
  },
})

const templatesStore = useTemplatesStore()
const previewTemplate = ref(null)
const loading = ref(false)

const hasActiveLayers = computed(() => templateHasRenderablePlayback(previewTemplate.value))

async function loadPreviewTemplate() {
  const id = props.template?.id
  if (!id) {
    previewTemplate.value = null
    return
  }

  if (templateHasRenderablePlayback(props.template)) {
    previewTemplate.value = props.template
    return
  }

  const fromStore = templatesStore.templates.find((t) => t.id === id)
  if (fromStore && templateHasRenderablePlayback(fromStore)) {
    previewTemplate.value = fromStore
    return
  }

  if (
    templatesStore.currentTemplate?.id === id &&
    templateHasRenderablePlayback(templatesStore.currentTemplate)
  ) {
    previewTemplate.value = templatesStore.currentTemplate
    return
  }

  loading.value = true
  try {
    const { data } = await templatesAPI.detail(id)
    previewTemplate.value = data
    const idx = templatesStore.templates.findIndex((t) => t.id === id)
    if (idx !== -1) {
      templatesStore.templates[idx] = data
    }
  } catch {
    previewTemplate.value = props.template
  } finally {
    loading.value = false
  }
}

watch(
  () => [
    props.template?.id,
    props.template?.layers?.length,
    props.template?.config_json?.widgets?.length,
  ],
  () => {
    loadPreviewTemplate()
  },
  { immediate: true }
)
</script>
