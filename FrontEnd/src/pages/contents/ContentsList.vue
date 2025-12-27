<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-primary">Contents</h1>
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
            <label class="label-base block text-sm mb-1">Search</label>
            <input
              v-model="contentStore.filters.search"
              type="text"
              placeholder="Search contents..."
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Type</label>
            <select v-model="contentStore.filters.type" class="select-base w-full px-3 py-2 rounded-lg">
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
            <label class="label-base block text-sm mb-1">Download Status</label>
            <select v-model="contentStore.filters.download_status" class="select-base w-full px-3 py-2 rounded-lg">
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
        <div v-else-if="contentStore.error" class="text-center py-8 text-error">
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
            <span class="badge-primary px-2 py-1 rounded text-xs">{{ value }}</span>
          </template>
          <template #cell-download_status="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value === 'success' ? 'badge-success' : '',
                value === 'failed' ? 'badge-error' : '',
                value === 'downloading' ? 'badge-warning' : '',
                value === 'pending' ? 'badge-info' : '',
              ]"
            >
              {{ value || 'pending' }}
            </span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center justify-end gap-1">
              <router-link
                :to="`/contents/${row.id}`"
                class="action-btn-view"
                title="View"
              >
                <EyeIcon class="w-4 h-4" />
              </router-link>
              <button
                @click="handleEdit(row)"
                class="action-btn-edit"
                title="Edit"
              >
                <PencilIcon class="w-4 h-4" />
              </button>
              <button
                @click="handleDelete(row)"
                class="action-btn-delete"
                title="Delete"
              >
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </template>
        </Table>
      </Card>
      
      <!-- Upload Modal -->
      <Modal :show="showUploadModal" title="Upload Content" @close="showUploadModal = false">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Name</label>
            <input v-model="uploadForm.name" type="text" required class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Type</label>
            <select v-model="uploadForm.type" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="image">Image</option>
              <option value="video">Video</option>
              <option value="text">Text</option>
              <option value="webview">WebView</option>
              <option value="chart">Chart</option>
              <option value="json">JSON</option>
            </select>
          </div>
          <div v-if="uploadForm.type === 'text'">
            <label class="label-base block text-sm mb-1">Text Content (Optional)</label>
            <textarea
              v-model="uploadForm.text_content"
              rows="5"
              class="textarea-base w-full px-3 py-2 rounded-lg"
              placeholder="Enter text content manually or upload a text file below"
            ></textarea>
            <p class="mt-1 text-xs text-muted">You can either enter text manually or upload a text file</p>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">
              File
              <span v-if="uploadForm.type !== 'text'" class="text-red-500">*</span>
              <span v-else class="text-muted text-xs">(Optional for text type)</span>
            </label>
            <input
              type="file"
              @change="handleFileSelect"
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Widget <span class="text-red-500">*</span></label>
            <select v-model="uploadForm.widget" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Select widget (required)</option>
              <option v-for="widget in widgets" :key="widget.id" :value="widget.id">
                {{ widget.name }}
              </option>
            </select>
            <p v-if="widgets.length === 0" class="mt-1 text-xs text-warning">
              No widgets available. Please create a widget first.
            </p>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleUpload" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Upload
          </button>
          <button type="button" @click="showUploadModal = false" class="btn-outline px-4 py-2 rounded-lg">
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
import { EyeIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useContentStore } from '@/stores/content'
import { useTemplatesStore } from '@/stores/templates'
import { widgetsAPI } from '@/services/api'
import { useNotification } from '@/composables/useNotification'
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const contentStore = useContentStore()
const templatesStore = useTemplatesStore()
const notify = useNotification()

const showUploadModal = ref(false)
const selectedFile = ref(null)
const widgets = computed(() => templatesStore.widgets)

const uploadForm = ref({
  name: '',
  type: 'image',
  widget: '',
  text_content: '',
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
  notify.info('Edit functionality coming soon')
}

const handleDelete = async (row) => {
  try {
    const { confirmDelete } = useDeleteConfirmation()
    await confirmDelete(
      row.id,
      async () => {
        await contentStore.deleteContent(row.id)
      },
      {
        title: 'Delete Content?',
        message: 'This will permanently delete the content. This action cannot be undone.',
        itemName: row.name,
        confirmText: 'Yes, Delete Content',
        cancelText: 'Cancel'
      }
    )
    notify.success('Content deleted successfully')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete content')
    }
  }
}

const handleUpload = async () => {
  // For text type, either file or text_content must be provided
  if (uploadForm.value.type === 'text') {
    if (!selectedFile.value && !uploadForm.value.text_content?.trim()) {
      notify.error('Please either enter text content or upload a text file')
      return
    }
  } else {
    // For other types, file is required
    if (!selectedFile.value) {
      notify.error('Please select a file')
      return
    }
  }
  
  if (!uploadForm.value.name) {
    notify.error('Please enter a name for the content')
    return
  }
  
  if (!uploadForm.value.widget) {
    notify.error('Please select a widget for the content')
    return
  }
  
  try {
    // First create the content
    const contentData = {
      name: uploadForm.value.name,
      type: uploadForm.value.type,
      widget: uploadForm.value.widget, // Widget is required
    }
    
    // Add text_content if provided (for text type)
    if (uploadForm.value.type === 'text' && uploadForm.value.text_content?.trim()) {
      contentData.text_content = uploadForm.value.text_content.trim()
    }
    
    const content = await contentStore.createContent(contentData)
    
    // Then upload the file if provided
    if (selectedFile.value) {
      console.log('[ContentsList] Uploading file for content', {
        contentId: content.id,
        fileName: selectedFile.value.name,
        fileSize: selectedFile.value.size,
        fileType: selectedFile.value.type,
        contentType: uploadForm.value.type
      })
      
      try {
        await contentStore.uploadContent(content.id, selectedFile.value)
        console.log('[ContentsList] File uploaded successfully')
      } catch (uploadError) {
        console.error('[ContentsList] File upload failed:', uploadError)
        // Error is already handled in uploadContent, but log details here
        const uploadErrorMessage = uploadError.response?.data?.message || 
                                   uploadError.response?.data?.error ||
                                   uploadError.message ||
                                   'Failed to upload file'
        notify.error(`File upload failed: ${uploadErrorMessage}`)
        throw uploadError // Re-throw to prevent success notification
      }
    }
    
    notify.success('Content created successfully')
    showUploadModal.value = false
    uploadForm.value = { name: '', type: 'image', widget: '', text_content: '' }
    selectedFile.value = null
    await contentStore.fetchContents() // Refresh the list
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.response?.data?.errors || 
                         'Failed to upload content'
    notify.error(typeof errorMessage === 'string' ? errorMessage : JSON.stringify(errorMessage))
    console.error('Upload error:', error)
  }
}

onMounted(async () => {
  await contentStore.fetchContents()
  // Fetch all widgets for dropdown
  try {
    const response = await widgetsAPI.list()
    templatesStore.widgets = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to fetch widgets:', error)
    notify.error('Failed to load widgets')
  }
})
</script>
