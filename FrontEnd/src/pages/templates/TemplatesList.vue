<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Templates</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Create Template
        </button>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="templatesStore.filters.search"
              type="text"
              placeholder="Search templates..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              @input="handleSearch"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="templatesStore.filters.is_active"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
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
      <div v-if="templatesStore.loading" class="text-center py-8">Loading...</div>
      <div v-else-if="templatesStore.error" class="text-center py-8 text-red-600">
        {{ templatesStore.error }}
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
              <h3 class="text-lg font-semibold">{{ template.name }}</h3>
              <p class="text-sm text-gray-600 mt-1">{{ template.description || 'No description' }}</p>
            </div>
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                template.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
              ]"
            >
              {{ template.is_active ? 'Active' : 'Inactive' }}
            </span>
          </div>
          <div class="flex items-center justify-between text-sm text-gray-500">
            <span>{{ template.width }}x{{ template.height }}</span>
            <span>v{{ template.version }}</span>
          </div>
          <div class="mt-4 flex gap-2">
            <button
              @click.stop="handleEdit(template)"
              class="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
            >
              Edit
            </button>
            <button
              @click.stop="handleDelete(template)"
              class="flex-1 px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
            >
              Delete
            </button>
          </div>
        </Card>
      </div>
      
      <!-- Create/Edit Modal -->
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit Template' : 'Create Template'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Width</label>
              <input v-model.number="form.width" type="number" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Height</label>
              <input v-model.number="form.height" type="number" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Orientation</label>
            <select v-model="form.orientation" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="landscape">Landscape</option>
              <option value="portrait">Portrait</option>
              <option value="reverse">Reverse</option>
            </select>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="form.is_active" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Active</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useTemplatesStore } from '@/stores/templates'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const templatesStore = useTemplatesStore()
const toastStore = useToastStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingTemplate = ref(null)

const form = ref({
  name: '',
  description: '',
  width: 1920,
  height: 1080,
  orientation: 'landscape',
  is_active: true,
  config_json: {},
})

const handleSearch = () => {}
const handleFilter = () => {}

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
  if (confirm(`Delete template "${template.name}"?`)) {
    try {
      await templatesStore.deleteTemplate(template.id)
      toastStore.success('Template deleted')
    } catch (error) {
      toastStore.error('Failed to delete template')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      await templatesStore.updateTemplate(editingTemplate.value.id, form.value)
      toastStore.success('Template updated')
    } else {
      await templatesStore.createTemplate(form.value)
      toastStore.success('Template created')
    }
    closeModal()
  } catch (error) {
    toastStore.error('Operation failed')
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
