<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-primary">Templates</h1>
        <button
          @click="showCreateModal = true"
          class="btn-primary px-4 py-2 rounded-lg"
        >
          Create Template
        </button>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="label-base block text-sm mb-1">Search</label>
            <input
              v-model="templatesStore.filters.search"
              type="text"
              placeholder="Search templates..."
              class="input-base w-full px-3 py-2 rounded-lg"
              @input="handleSearch"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Status</label>
            <select
              v-model="templatesStore.filters.is_active"
              class="select-base w-full px-3 py-2 rounded-lg"
              @change="handleFilter"
            >
              <option :value="null">All</option>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
        </div>
      </Card>
      
      <!-- Templates Grid -->
      <Card>
        <div v-if="templatesStore.loading" class="text-center py-8 text-secondary">Loading...</div>
        <div v-else-if="templatesStore.error" class="text-center py-8 text-error">
          {{ templatesStore.error }}
        </div>
        <div v-else-if="templatesStore.filteredTemplates.length === 0" class="text-center py-8 text-muted">
          No templates found
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Card
            v-for="template in templatesStore.filteredTemplates"
            :key="template.id"
            class="cursor-pointer hover:shadow-lg transition"
            @click="$router.push(`/templates/${template.id}`)"
          >
          <div class="flex items-start justify-between mb-4">
            <div>
              <h3 class="text-lg font-semibold text-primary">{{ template.name }}</h3>
              <p class="text-sm text-secondary mt-1">{{ template.description || 'No description' }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                template.is_active ? 'badge-success' : 'badge-info',
              ]"
            >
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm text-muted">
            <span>{{ template.width }}x{{ template.height }}</span>
            <span>v{{ template.version }}</span>
          </div>
          <div class="mt-4 flex gap-2">
            <button
              @click.stop="handleEdit(template)"
              class="btn-secondary flex-1 px-3 py-2 rounded text-sm"
            >
              Edit
            </button>
            <button
              @click.stop="openWidgetsModal(template)"
              class="btn-primary flex-1 px-3 py-2 rounded text-sm"
            >
              Manage Widgets
            </button>
            <button
              @click.stop="handleDelete(template)"
              class="btn-danger flex-1 px-3 py-2 rounded text-sm"
            >
              Delete
            </button>
          </div>
          </Card>
        </div>
      </Card>
      
      <!-- Widgets Management Modal -->
      <Modal
        :show="showWidgetsModal"
        :title="selectedTemplate ? `Manage Widgets - ${selectedTemplate.name}` : 'Manage Widgets'"
        @close="closeWidgetsModal"
        @confirm="closeWidgetsModal"
        size="large"
        :showFooter="true"
      >
        <div v-if="selectedTemplate" class="space-y-4">
          <!-- Layers Section -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-primary">Layers</h3>
              <button
                @click="openCreateLayerModal"
                class="btn-primary px-3 py-1 text-sm rounded"
              >
                + Add Layer
              </button>
            </div>
            <div v-if="templateLayers.length === 0" class="text-center py-4 text-muted text-sm">
              No layers found. Create a layer first to add widgets.
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="layer in templateLayers"
                :key="layer.id"
                class="border-l-4 border-indigo-500 pl-4 py-2 bg-slate-50 dark:bg-slate-800 rounded"
              >
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-primary">{{ layer.name }}</h4>
                  <button
                    @click="openCreateWidgetModal(layer.id)"
                    class="text-xs px-2 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700"
                  >
                    + Add Widget
                  </button>
                </div>
                <!-- Widgets in this layer -->
                <div v-if="getWidgetsForLayer(layer.id).length === 0" class="text-xs text-muted ml-4">
                  No widgets in this layer
                </div>
                <div v-else class="space-y-2 ml-4 mt-2">
                  <div
                    v-for="widget in getWidgetsForLayer(layer.id)"
                    :key="widget.id"
                    class="flex items-center justify-between p-2 bg-white dark:bg-slate-700 rounded border border-slate-200 dark:border-slate-600"
                  >
                    <div>
                      <span class="text-sm font-medium text-primary">{{ widget.name }}</span>
                      <span class="text-xs text-muted ml-2">({{ widget.type }})</span>
                      <span class="text-xs text-secondary ml-2">{{ widget.width }}x{{ widget.height }}</span>
                    </div>
                    <div class="flex gap-1">
                      <button
                        @click="openEditWidgetModal(widget)"
                        class="text-xs px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                      >
                        Edit
                      </button>
                      <button
                        @click="handleDeleteWidget(widget.id)"
                        class="text-xs px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Modal>

      <!-- Create/Edit Widget Modal -->
      <Modal
        :show="showCreateWidgetModal || showEditWidgetModal"
        :title="showEditWidgetModal ? 'Edit Widget' : 'Create Widget'"
        @close="closeWidgetModal"
      >
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Layer <span class="text-red-500">*</span></label>
            <select v-model="widgetForm.layer" required :disabled="showEditWidgetModal" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Select a layer</option>
              <option v-for="layer in templateLayers" :key="layer.id" :value="layer.id">
                {{ layer.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Name <span class="text-red-500">*</span></label>
            <input v-model="widgetForm.name" type="text" required class="input-base w-full px-3 py-2 rounded-lg" placeholder="Widget name" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Type <span class="text-red-500">*</span></label>
            <select v-model="widgetForm.type" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Select widget type</option>
              <option value="text">Text</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="clock">Clock</option>
              <option value="webview">Web View</option>
              <option value="chart">Chart</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label-base block text-sm mb-1">X Position</label>
              <input v-model.number="widgetForm.x" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Y Position</label>
              <input v-model.number="widgetForm.y" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label-base block text-sm mb-1">Width</label>
              <input v-model.number="widgetForm.width" type="number" min="1" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Height</label>
              <input v-model.number="widgetForm.height" type="number" min="1" class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Z-Index</label>
            <input v-model.number="widgetForm.z_index" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="widgetForm.is_active" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-primary">Active</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click.stop="handleSubmitWidget" class="btn-primary px-4 py-2 rounded-lg">
            {{ showEditWidgetModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click.stop="closeWidgetModal" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>

      <!-- Create Layer Modal -->
      <Modal
        :show="showCreateLayerModal"
        title="Create Layer"
        @close="closeLayerModal"
      >
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Name <span class="text-red-500">*</span></label>
            <input v-model="layerForm.name" type="text" required class="input-base w-full px-3 py-2 rounded-lg" placeholder="Layer name" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Description</label>
            <textarea v-model="layerForm.description" rows="3" class="textarea-base w-full px-3 py-2 rounded-lg"></textarea>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Z-Index</label>
            <input v-model.number="layerForm.z_index" type="number" min="0" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="layerForm.is_active" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-primary">Active</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleCreateLayer" class="btn-primary px-4 py-2 rounded-lg">
            Create Layer
          </button>
          <button type="button" @click="closeLayerModal" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>

      <!-- Create/Edit Template Modal -->
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit Template' : 'Create Template'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Name</label>
            <input v-model="form.name" type="text" required class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Description</label>
            <textarea v-model="form.description" rows="3" class="textarea-base w-full px-3 py-2 rounded-lg"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label-base block text-sm mb-1">Width</label>
              <input v-model.number="form.width" type="number" required class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
            <div>
              <label class="label-base block text-sm mb-1">Height</label>
              <input v-model.number="form.height" type="number" required class="input-base w-full px-3 py-2 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Orientation</label>
            <select v-model="form.orientation" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="landscape">Landscape</option>
              <option value="portrait">Portrait</option>
              <option value="reverse">Reverse</option>
            </select>
          </div>
          <div>
            <label class="flex items-center text-primary">
              <input
                v-model="form.is_active"
                type="checkbox"
                class="checkbox-base mr-2"
              />
              <span class="text-sm font-medium">Active</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="btn-primary px-4 py-2 rounded-lg">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useTemplatesStore } from '@/stores/templates'
import { useNotification } from '@/composables/useNotification'
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const templatesStore = useTemplatesStore()
const notify = useNotification()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showWidgetsModal = ref(false)
const showCreateWidgetModal = ref(false)
const showEditWidgetModal = ref(false)
const showCreateLayerModal = ref(false)
const editingTemplate = ref(null)
const selectedTemplate = ref(null)
const editingWidget = ref(null)
const templateLayers = ref([])
const templateWidgets = ref([])

const form = ref({
  name: '',
  description: '',
  width: 1920,
  height: 1080,
  orientation: 'landscape',
  is_active: true,
  config_json: {},
})

const widgetForm = ref({
  layer: '',
  name: '',
  type: '',
  x: 0,
  y: 0,
  width: 100,
  height: 100,
  z_index: 0,
  is_active: true,
})

const layerForm = ref({
  name: '',
  description: '',
  z_index: 0,
  is_active: true,
})

const handleSearch = () => {}
const handleFilter = () => {}

const getWidgetsForLayer = (layerId) => {
  return templateWidgets.value.filter(w => w.layer === layerId)
}

const openWidgetsModal = async (template) => {
  selectedTemplate.value = template
  showWidgetsModal.value = true
  // Clear previous data
  templateLayers.value = []
  templateWidgets.value = []
  
  // Fetch layers and widgets for this template
  try {
    await templatesStore.fetchLayers(template.id)
    // Filter layers to ensure they belong to this template
    templateLayers.value = (templatesStore.layers || []).filter(
      layer => layer.template === template.id || layer.template?.id === template.id
    )
    
    // Fetch widgets for each layer
    templateWidgets.value = []
    for (const layer of templateLayers.value) {
      await templatesStore.fetchWidgets(layer.id)
      const widgets = templatesStore.widgets || []
      // Filter widgets to ensure they belong to this layer
      const layerWidgets = widgets.filter(
        widget => widget.layer === layer.id || widget.layer?.id === layer.id
      )
      templateWidgets.value.push(...layerWidgets)
    }
  } catch (error) {
    console.error('Failed to load template data:', error)
    notify.error('Failed to load template layers and widgets')
  }
}

const closeWidgetsModal = () => {
  showWidgetsModal.value = false
  selectedTemplate.value = null
  templateLayers.value = []
  templateWidgets.value = []
}

const openCreateWidgetModal = (layerId = null) => {
  editingWidget.value = null
  widgetForm.value = {
    layer: layerId || '',
    name: '',
    type: '',
    x: 0,
    y: 0,
    width: 100,
    height: 100,
    z_index: 0,
    is_active: true,
  }
  showCreateWidgetModal.value = true
}

const openEditWidgetModal = (widget) => {
  editingWidget.value = widget
  widgetForm.value = {
    layer: widget.layer,
    name: widget.name || '',
    type: widget.type || '',
    x: widget.x || 0,
    y: widget.y || 0,
    width: widget.width || 100,
    height: widget.height || 100,
    z_index: widget.z_index || 0,
    is_active: widget.is_active ?? true,
  }
  showEditWidgetModal.value = true
}

const closeWidgetModal = () => {
  showCreateWidgetModal.value = false
  showEditWidgetModal.value = false
  editingWidget.value = null
  widgetForm.value = {
    layer: '',
    name: '',
    type: '',
    x: 0,
    y: 0,
    width: 100,
    height: 100,
    z_index: 0,
    is_active: true,
  }
}

const handleSubmitWidget = async (event) => {
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  if (!widgetForm.value.layer) {
    notify.error('Please select a layer')
    return
  }
  if (!widgetForm.value.name || widgetForm.value.name.trim() === '') {
    notify.error('Please enter a widget name')
    return
  }
  if (!widgetForm.value.type) {
    notify.error('Please select a widget type')
    return
  }
  
  try {
    const widgetData = {
      layer: widgetForm.value.layer,
      name: widgetForm.value.name.trim(),
      type: widgetForm.value.type,
      x: widgetForm.value.x || 0,
      y: widgetForm.value.y || 0,
      width: widgetForm.value.width || 100,
      height: widgetForm.value.height || 100,
      z_index: widgetForm.value.z_index || 0,
      is_active: widgetForm.value.is_active ?? true,
    }
    
    if (showEditWidgetModal.value && editingWidget.value) {
      await templatesStore.updateWidget(editingWidget.value.id, widgetData)
      notify.success('Widget updated successfully')
    } else {
      await templatesStore.createWidget(widgetData)
      notify.success('Widget created successfully')
    }
    
    closeWidgetModal()
    
    // Refresh widgets if we have a selected template
    if (selectedTemplate.value) {
      await openWidgetsModal(selectedTemplate.value)
    }
  } catch (error) {
    console.error('Widget save error:', error)
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         (error.response?.data?.errors ? JSON.stringify(error.response.data.errors) : null) ||
                         'Failed to save widget'
    notify.error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage))
  }
}

const handleDeleteWidget = async (widgetId) => {
  if (confirm('Are you sure you want to delete this widget?')) {
    try {
      await templatesStore.deleteWidget(widgetId)
      notify.success('Widget deleted successfully')
      // Refresh widgets
      await openWidgetsModal(selectedTemplate.value)
    } catch (error) {
      notify.error('Failed to delete widget')
      console.error('Delete widget error:', error)
    }
  }
}

const openCreateLayerModal = () => {
  layerForm.value = {
    name: '',
    description: '',
    z_index: 0,
    is_active: true,
  }
  showCreateLayerModal.value = true
}

const closeLayerModal = () => {
  showCreateLayerModal.value = false
  layerForm.value = {
    name: '',
    description: '',
    z_index: 0,
    is_active: true,
  }
}

const handleCreateLayer = async () => {
  // Validate form
  if (!layerForm.value.name || layerForm.value.name.trim() === '') {
    notify.error('Please enter a layer name')
    return
  }
  
  if (!selectedTemplate.value || !selectedTemplate.value.id) {
    notify.error('No template selected')
    return
  }
  
  try {
    const layerData = {
      name: layerForm.value.name.trim(),
      description: layerForm.value.description || '',
      z_index: layerForm.value.z_index || 0,
      is_active: layerForm.value.is_active ?? true,
      template: selectedTemplate.value.id,
    }
    
    await templatesStore.createLayer(layerData)
    notify.success('Layer created successfully')
    
    // Refresh layers for the current template
    await templatesStore.fetchLayers(selectedTemplate.value.id)
    templateLayers.value = (templatesStore.layers || []).filter(
      layer => layer.template === selectedTemplate.value.id || layer.template?.id === selectedTemplate.value.id
    )
    
    // Close the create layer modal
    closeLayerModal()
  } catch (error) {
    console.error('Create layer error:', error)
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         (error.response?.data?.errors ? JSON.stringify(error.response.data.errors) : null) ||
                         'Failed to create layer'
    notify.error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage))
  }
}

const handleEdit = (template) => {
  editingTemplate.value = template
  form.value = {
    name: template.name || '',
    description: template.description || '',
    width: template.width || 1920,
    height: template.height || 1080,
    orientation: template.orientation || 'landscape',
    is_active: template.is_active ?? true,
    config_json: template.config_json || {},
  }
  showEditModal.value = true
}

const handleDelete = async (template) => {
  try {
    const { confirmDelete } = useDeleteConfirmation()
    await confirmDelete(
      template.id,
      async () => {
        await templatesStore.deleteTemplate(template.id)
      },
      {
        title: 'Delete Template?',
        message: 'This will permanently delete the template and all its layers, widgets, and content. This action cannot be undone.',
        itemName: template.name,
        confirmText: 'Yes, Delete Template',
        cancelText: 'Cancel'
      }
    )
    notify.success('Template deleted successfully')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete template')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      await templatesStore.updateTemplate(editingTemplate.value.id, form.value)
      notify.success('Template updated')
    } else {
      await templatesStore.createTemplate(form.value)
      notify.success('Template created')
    }
    closeModal()
  } catch (error) {
    notify.error('Operation failed')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingTemplate.value = null
  form.value = {
    name: '',
    description: '',
    width: 1920,
    height: 1080,
    orientation: 'landscape',
    is_active: true,
    config_json: {},
  }
}

onMounted(async () => {
  await templatesStore.fetchTemplates()
})
</script>
