<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Contents</h1>
        <button
          @click="showUploadModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Upload Content
        </button>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="contentStore.filters.search"
              type="text"
              placeholder="Search contents..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select v-model="contentStore.filters.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option :value="null">All</option>
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="text">Text</option>
              <option value="webview">WebView</option>
              <option value="chart">Chart</option>
              <option value="json">JSON</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Download Status</label>
            <select v-model="contentStore.filters.download_status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option :value="null">All</option>
              <option value="pending">Pending</option>
              <option value="downloading">Downloading</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
      </Card>
      
      <!-- Contents Table -->
      <Card>
        <div v-if="contentStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="contentStore.error" class="text-center py-8 text-red-600">
          {{ contentStore.error }}
        </div>
        <Table
          v-else
          :columns="columns"
          :data="contentStore.filteredContents"
          :actions="['view', 'edit', 'delete']"
          @view="handleView"
          @edit="handleEdit"
          @delete="handleDelete"
        >
          <template #cell-type="{ value }">
            <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">{{ value }}</span>
          </template>
          <template #cell-download_status="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value === 'success' ? 'bg-green-100 text-green-800' : '',
                value === 'failed' ? 'bg-red-100 text-red-800' : '',
                value === 'downloading' ? 'bg-yellow-100 text-yellow-800' : '',
                value === 'pending' ? 'bg-gray-100 text-gray-800' : '',
              ]"
            >
              {{ value || 'pending' }}
            </span>
          </template>
          <template #actions="{ row }">
            <router-link
              :to="`/contents/${row.id}`"
              class="text-indigo-600 hover:text-indigo-900 mr-3"
            >
              View
            </router-link>
            <button
              @click="handleEdit(row)"
              class="text-blue-600 hover:text-blue-900 mr-3"
            >
              Edit
            </button>
            <button
              @click="handleDelete(row)"
              class="text-red-600 hover:text-red-900"
            >
              Delete
            </button>
          </template>
        </Table>
      </Card>
      
      <!-- Upload Modal -->
      <Modal :show="showUploadModal" title="Upload Content" @close="showUploadModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="uploadForm.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select v-model="uploadForm.type" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="text">Text</option>
              <option value="webview">WebView</option>
              <option value="chart">Chart</option>
              <option value="json">JSON</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">File</label>
            <input
              type="file"
              @change="handleFileSelect"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Widget</label>
            <select v-model="uploadForm.widget" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Select widget (optional)</option>
              <option v-for="widget in widgets" :key="widget.id" :value="widget.id">
                {{ widget.name }}
              </option>
            </select>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleUpload" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Upload
          </button>
          <button type="button" @click="showUploadModal = false" class="px-4 py-2 border border-gray-300 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContentStore } from '@/stores/content'
import { useTemplatesStore } from '@/stores/templates'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const contentStore = useContentStore()
const templatesStore = useTemplatesStore()
const toastStore = useToastStore()

const showUploadModal = ref(false)
const selectedFile = ref(null)
const widgets = computed(() => templatesStore.widgets)

const uploadForm = ref({
  name: '',
  type: 'image',
  widget: '',
})

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'type', label: 'Type' },
  { key: 'download_status', label: 'Status' },
  { key: 'created_at', label: 'Created' },
]

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
}

const handleView = (row) => {
  router.push(`/contents/${row.id}`)
}

const handleEdit = (row) => {
  // TODO: Implement edit
  toastStore.info('Edit functionality coming soon')
}

const handleDelete = async (row) => {
  if (confirm(`Delete content "${row.name}"?`)) {
    try {
      await contentStore.deleteContent(row.id)
      toastStore.success('Content deleted')
    } catch (error) {
      toastStore.error('Failed to delete content')
    }
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    toastStore.error('Please select a file')
    return
  }
  
  try {
    // First create the content
    const contentData = {
      name: uploadForm.value.name,
      type: uploadForm.value.type,
      widget: uploadForm.value.widget || null,
    }
    
    const content = await contentStore.createContent(contentData)
    
    // Then upload the file
    await contentStore.uploadContent(content.id, selectedFile.value)
    
    toastStore.success('Content uploaded successfully')
    showUploadModal.value = false
    uploadForm.value = { name: '', type: 'image', widget: '' }
    selectedFile.value = null
  } catch (error) {
    toastStore.error('Failed to upload content')
  }
}

onMounted(async () => {
  await contentStore.fetchContents()
  // Fetch widgets for dropdown
  await templatesStore.fetchTemplates()
  // Note: In a real app, you'd fetch widgets separately or filter by template
})
</script>
