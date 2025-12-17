<template>
  <AppLayout>
    <div v-if="templatesStore.loading" class="text-center py-8">Loading...</div>
    <div v-else-if="templatesStore.error" class="text-center py-8 text-red-600">
      {{ templatesStore.error }}
    </div>
    <div v-else-if="template" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">{{ template.name }}</h1>
          <p class="text-gray-600">{{ template.description || 'No description' }}</p>
        </div>
        <button
          @click="showActivateModal = true"
          class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          Activate on Screen
        </button>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Template Information" class="lg:col-span-2">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-gray-500">Dimensions</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ template.width }}x{{ template.height }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Orientation</dt>
              <dd class="mt-1 text-sm text-gray-900 capitalize">{{ template.orientation }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Version</dt>
              <dd class="mt-1 text-sm text-gray-900">{{ template.version }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-gray-500">Status</dt>
              <dd class="mt-1">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    template.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
                  ]"
                >
                  {{ template.is_active ? 'Active' : 'Inactive' }}
                </span>
              </dd>
            </div>
          </dl>
        </Card>
        
        <Card title="Preview">
          <div class="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
            <span class="text-gray-400">Template Preview</span>
          </div>
        </Card>
      </div>
      
      <!-- Hierarchy: Template → Layer → Widget → Content -->
      <Card title="Template Hierarchy">
        <div class="space-y-4">
          <div v-for="layer in layers" :key="layer.id" class="border-l-4 border-indigo-500 pl-4">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold">{{ layer.name }}</h3>
              <span class="text-xs text-gray-500">Layer</span>
            </div>
            <div v-for="widget in getWidgetsForLayer(layer.id)" :key="widget.id" class="ml-4 mt-2 border-l-4 border-blue-400 pl-4">
              <div class="flex items-center justify-between mb-2">
                <h4 class="text-sm font-medium">{{ widget.name }} ({{ widget.type }})</h4>
                <span class="text-xs text-gray-500">Widget</span>
              </div>
              <div v-for="content in getContentsForWidget(widget.id)" :key="content.id" class="ml-4 mt-1 text-xs text-gray-600">
                • {{ content.name }} ({{ content.type }})
              </div>
            </div>
          </div>
          <div v-if="layers.length === 0" class="text-center text-gray-500 py-4">
            No layers in this template
          </div>
        </div>
      </Card>
      
      <Modal :show="showActivateModal" title="Activate Template on Screen" @close="showActivateModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Select Screen</label>
            <select v-model="activateForm.screen_id" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Select a screen</option>
              <option v-for="screen in screens" :key="screen.id" :value="screen.id">
                {{ screen.name }} ({{ screen.device_id }})
              </option>
            </select>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="activateForm.sync_content" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Sync content automatically</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleActivate" class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Activate
          </button>
          <button type="button" @click="showActivateModal = false" class="px-4 py-2 border border-gray-300 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTemplatesStore } from '@/stores/templates'
import { useScreensStore } from '@/stores/screens'
import { useContentStore } from '@/stores/content'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const route = useRoute()
const templatesStore = useTemplatesStore()
const screensStore = useScreensStore()
const contentStore = useContentStore()
const toastStore = useToastStore()

const template = computed(() => templatesStore.currentTemplate)
const screens = computed(() => screensStore.screens)
const layers = computed(() => templatesStore.layers)
const widgets = computed(() => templatesStore.widgets)
const contents = computed(() => contentStore.contents)

const showActivateModal = ref(false)
const activateForm = ref({
  screen_id: '',
  sync_content: true,
})

const getWidgetsForLayer = (layerId) => {
  return widgets.value.filter(w => w.layer === layerId)
}

const getContentsForWidget = (widgetId) => {
  return contents.value.filter(c => c.widget === widgetId)
}

const handleActivate = async () => {
  try {
    await templatesStore.activateOnScreen(
      template.value.id,
      activateForm.value.screen_id,
      activateForm.value.sync_content
    )
    toastStore.success('Template activated successfully')
    showActivateModal.value = false
  } catch (error) {
    toastStore.error('Failed to activate template')
  }
}

onMounted(async () => {
  const templateId = route.params.id
  await templatesStore.fetchTemplate(templateId)
  await templatesStore.fetchLayers(templateId)
  await screensStore.fetchScreens()
  
  // Fetch widgets for each layer
  for (const layer of layers.value) {
    await templatesStore.fetchWidgets(layer.id)
  }
  
  // Fetch contents for all widgets
  for (const widget of widgets.value) {
    await contentStore.fetchContents({ widget: widget.id })
  }
})
</script>
