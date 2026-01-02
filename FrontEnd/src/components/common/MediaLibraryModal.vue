<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
        <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity bg-black/60 backdrop-blur-md" aria-hidden="true"></div>
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
          <div
            class="inline-block align-bottom bg-gray-800 backdrop-blur-lg rounded-2xl text-left overflow-hidden shadow-2xl border border-gray-700 transform transition-all duration-300 sm:my-8 sm:align-middle sm:max-w-5xl sm:w-full"
            style="animation: modalFadeUp 0.3s ease-out;"
          >
            <!-- Header -->
            <div class="bg-gray-800 px-6 pt-6 pb-4 border-b border-gray-700">
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-semibold text-white">Media Library</h3>
                <button
                  @click="$emit('close')"
                  class="text-gray-400 hover:text-white transition-colors duration-200 p-2 rounded-lg hover:bg-gray-700"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <!-- Tabs -->
              <div class="flex gap-2 border-b border-gray-700">
                <button
                  @click="activeTab = 'gallery'"
                  :class="[
                    'px-4 py-2 text-sm font-medium transition-colors duration-200 border-b-2',
                    activeTab === 'gallery'
                      ? 'text-blue-400 border-blue-400'
                      : 'text-gray-400 border-transparent hover:text-gray-300'
                  ]"
                >
                  <span class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    Gallery
                  </span>
                </button>
                <button
                  @click="activeTab = 'upload'"
                  :class="[
                    'px-4 py-2 text-sm font-medium transition-colors duration-200 border-b-2',
                    activeTab === 'upload'
                      ? 'text-blue-400 border-blue-400'
                      : 'text-gray-400 border-transparent hover:text-gray-300'
                  ]"
                >
                  <span class="flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    Upload
                  </span>
                </button>
              </div>
            </div>

            <!-- Tab Content -->
            <div class="bg-gray-800">
              <!-- Gallery Tab -->
              <div v-if="activeTab === 'gallery'" class="px-6 py-4">
                <!-- Search and Filter -->
                <div class="flex gap-3 mb-4">
                  <div class="flex-1">
                    <input
                      v-model="searchQuery"
                      type="text"
                      placeholder="Search media..."
                      class="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    />
                  </div>
                  <select
                    v-model="filterType"
                    class="px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                  >
                    <option :value="null">All Types</option>
                    <option value="image">Images</option>
                    <option value="video">Videos</option>
                  </select>
                </div>

                <!-- Loading State -->
                <div v-if="contentStore.loading" class="flex items-center justify-center py-12">
                  <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
                  <span class="ml-3 text-gray-400">Loading media...</span>
                </div>

                <!-- Error State -->
                <div v-else-if="contentStore.error" class="text-center py-12">
                  <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/10 mb-4">
                    <svg class="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p class="text-red-400 font-medium mb-2">{{ contentStore.error }}</p>
                  <button
                    @click="loadContents"
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors duration-200"
                  >
                    Retry
                  </button>
                </div>

                <!-- Empty State -->
                <div v-else-if="filteredContents.length === 0" class="text-center py-12">
                  <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-700/50 mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <h3 class="text-lg font-medium text-gray-300 mb-2">No media found</h3>
                  <p class="text-gray-400 text-sm mb-4">{{ searchQuery || filterType ? 'Try adjusting your search or filters' : 'Upload some content to get started' }}</p>
                  <button
                    @click="activeTab = 'upload'"
                    class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm transition-colors duration-200"
                  >
                    Upload Media
                  </button>
                </div>

                <!-- Media Grid -->
                <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 max-h-[60vh] overflow-y-auto">
                  <div
                    v-for="content in filteredContents"
                    :key="content.id"
                    @click="selectContent(content)"
                    :class="[
                      'relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200',
                      selectedContentId === content.id
                        ? 'border-blue-500 ring-2 ring-blue-500/50 shadow-lg'
                        : 'border-gray-700 hover:border-gray-600 hover:shadow-md'
                    ]"
                  >
                    <!-- Thumbnail/Preview -->
                    <div class="aspect-square bg-gray-700 relative overflow-hidden">
                      <!-- Image Preview -->
                      <img
                        v-if="content.type === 'image' && content.secure_url"
                        :src="content.secure_url"
                        :alt="content.name || 'Media'"
                        class="w-full h-full object-cover"
                        @error="handleImageError"
                      />
                      <!-- Video Preview -->
                      <div v-else-if="content.type === 'video' && content.secure_url" class="w-full h-full flex items-center justify-center bg-gray-900">
                        <video
                          :src="content.secure_url"
                          class="w-full h-full object-cover"
                          muted
                          preload="metadata"
                        />
                        <div class="absolute inset-0 flex items-center justify-center bg-black/30">
                          <svg class="w-12 h-12 text-white" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M8 5v14l11-7z" />
                          </svg>
                        </div>
                      </div>
                      <!-- Placeholder -->
                      <div v-else class="w-full h-full flex items-center justify-center">
                        <svg class="w-12 h-12 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>

                      <!-- Selection Indicator -->
                      <div
                        v-if="selectedContentId === content.id"
                        class="absolute inset-0 bg-blue-500/20 flex items-center justify-center"
                      >
                        <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
                          <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                          </svg>
                        </div>
                      </div>

                      <!-- Type Badge -->
                      <div class="absolute top-2 right-2">
                        <span
                          :class="[
                            'px-2 py-1 rounded text-xs font-medium',
                            content.type === 'image' ? 'bg-green-500/80 text-white' : 'bg-purple-500/80 text-white'
                          ]"
                        >
                          {{ content.type === 'image' ? 'IMG' : 'VID' }}
                        </span>
                      </div>

                      <!-- Delete Button (on hover) -->
                      <button
                        @click.stop="handleDeleteContent(content)"
                        class="absolute top-2 left-2 w-7 h-7 bg-red-500/80 hover:bg-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        title="Delete"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>

                    <!-- Content Info -->
                    <div class="p-2 bg-gray-900/80">
                      <p class="text-xs text-white font-medium truncate" :title="content.name">
                        {{ content.name || 'Untitled' }}
                      </p>
                      <p v-if="content.description" class="text-xs text-gray-400 truncate mt-1" :title="content.description">
                        {{ content.description }}
                      </p>
                    </div>

                    <!-- Hover Overlay -->
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200 pointer-events-none"></div>
                  </div>
                </div>
              </div>

              <!-- Upload Tab -->
              <div v-if="activeTab === 'upload'" class="px-6 py-4">
                <!-- Drag & Drop Zone -->
                <div
                  @drop.prevent="handleDrop"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @dragenter.prevent="isDragging = true"
                  :class="[
                    'border-2 border-dashed rounded-lg p-8 text-center transition-colors duration-200',
                    isDragging
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-600 bg-gray-700/30 hover:border-gray-500'
                  ]"
                >
                  <input
                    ref="fileInput"
                    type="file"
                    :accept="filterByType === 'image' ? 'image/*' : filterByType === 'video' ? 'video/*' : 'image/*,video/*'"
                    multiple
                    class="hidden"
                    @change="handleFileSelect"
                  />
                  
                  <div v-if="!uploadingFiles.length && !uploadedFiles.length">
                    <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p class="text-gray-300 font-medium mb-2">Drag & drop files here</p>
                    <p class="text-gray-400 text-sm mb-4">or</p>
                    <button
                      @click="fileInput?.click()"
                      class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                    >
                      Browse Files
                    </button>
                    <p class="text-gray-500 text-xs mt-3">
                      Supported: {{ filterByType === 'image' ? 'Images' : filterByType === 'video' ? 'Videos' : 'Images & Videos' }}
                    </p>
                  </div>

                  <!-- Upload Progress -->
                  <div v-if="uploadingFiles.length" class="space-y-3">
                    <div
                      v-for="file in uploadingFiles"
                      :key="file.id"
                      class="bg-gray-700/50 rounded-lg p-4"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <span class="text-sm text-white font-medium truncate flex-1">{{ file.name }}</span>
                        <span class="text-xs text-gray-400 ml-2">{{ Math.round(file.progress) }}%</span>
                      </div>
                      <div class="w-full bg-gray-600 rounded-full h-2">
                        <div
                          class="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          :style="{ width: `${file.progress}%` }"
                        ></div>
                      </div>
                    </div>
                  </div>

                  <!-- Uploaded Files -->
                  <div v-if="uploadedFiles.length" class="space-y-3 mt-4">
                    <div
                      v-for="file in uploadedFiles"
                      :key="file.id"
                      class="bg-green-500/10 border border-green-500/30 rounded-lg p-4 flex items-center justify-between"
                    >
                      <div class="flex items-center gap-3 flex-1 min-w-0">
                        <svg class="w-5 h-5 text-green-500 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                        </svg>
                        <span class="text-sm text-white font-medium truncate">{{ file.name }}</span>
                      </div>
                      <button
                        @click="selectUploadedFile(file)"
                        class="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors duration-200 ml-2"
                      >
                        Use This
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Upload Form (if needed for additional metadata) -->
                <div v-if="selectedFiles.length > 0 && !uploadingFiles.length && !uploadedFiles.length" class="mt-4 space-y-3">
                  <div>
                    <label class="block text-xs font-medium text-gray-400 mb-1.5">Content Name</label>
                    <input
                      v-model="uploadForm.name"
                      type="text"
                      placeholder="Enter a name for the content"
                      class="w-full px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                    />
                  </div>
                  <button
                    @click="handleUpload"
                    :disabled="!uploadForm.name || uploadingFiles.length > 0"
                    class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors duration-200"
                  >
                    Upload {{ selectedFiles.length }} {{ selectedFiles.length === 1 ? 'File' : 'Files' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="bg-gray-800 px-6 py-4 border-t border-gray-700 flex items-center justify-between">
              <div class="text-sm text-gray-400">
                <span v-if="activeTab === 'gallery'">
                  {{ filteredContents.length }} {{ filteredContents.length === 1 ? 'item' : 'items' }}
                  <span v-if="searchQuery || filterType" class="text-gray-500">(filtered)</span>
                </span>
                <span v-else-if="activeTab === 'upload'">
                  {{ selectedFiles.length }} {{ selectedFiles.length === 1 ? 'file' : 'files' }} selected
                </span>
              </div>
              <div class="flex gap-3">
                <button
                  @click="$emit('close')"
                  class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                >
                  {{ activeTab === 'upload' && uploadedFiles.length ? 'Done' : 'Cancel' }}
                </button>
                <button
                  v-if="activeTab === 'gallery' && selectedContentId"
                  @click="confirmSelection"
                  class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors duration-200"
                >
                  Select
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useContentStore } from '@/stores/content'
import { useNotification } from '@/composables/useNotification'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  filterByType: {
    type: String,
    default: null, // 'image' or 'video' to filter by type
    validator: (value) => !value || ['image', 'video'].includes(value)
  },
  widgetId: {
    type: String,
    default: null // Widget ID to associate content with (optional - allows standalone uploads)
  }
})

const emit = defineEmits(['close', 'select'])

const contentStore = useContentStore()
const notify = useNotification()

// Tab state
const activeTab = ref('gallery')

// Gallery state
const searchQuery = ref('')
const filterType = ref(props.filterByType)
const selectedContentId = ref(null)

// Upload state
const fileInput = ref(null)
const isDragging = ref(false)
const selectedFiles = ref([])
const uploadingFiles = ref([])
const uploadedFiles = ref([])
const uploadForm = ref({
  name: ''
})

// Filter contents based on search and type
const filteredContents = computed(() => {
  let filtered = contentStore.contents || []

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c =>
      c.name?.toLowerCase().includes(query) ||
      c.description?.toLowerCase().includes(query)
    )
  }

  // Filter by type
  if (filterType.value) {
    filtered = filtered.filter(c => c.type === filterType.value)
  }

  // Only show contents with secure_url (uploaded files)
  filtered = filtered.filter(c => c.secure_url)

  return filtered
})

// Load contents when modal opens
const loadContents = async () => {
  try {
    // Clear filters to fetch all contents (backend will filter by user/org)
    await contentStore.fetchContents()
  } catch (error) {
    console.error('Failed to load contents:', error)
    notify.error('Failed to load media library')
  }
}

// Watch for modal opening
watch(() => props.show, (isOpen) => {
  if (isOpen) {
    activeTab.value = 'gallery'
    selectedContentId.value = null
    searchQuery.value = ''
    filterType.value = props.filterByType
    selectedFiles.value = []
    uploadingFiles.value = []
    uploadedFiles.value = []
    uploadForm.value = { name: '' }
    loadContents()
  }
})

// Watch for filterByType changes
watch(() => props.filterByType, (newType) => {
  filterType.value = newType
})

// Select content
const selectContent = (content) => {
  selectedContentId.value = content.id
}

// Confirm selection and emit
const confirmSelection = () => {
  if (!selectedContentId.value) return

  const selectedContent = contentStore.contents.find(c => c.id === selectedContentId.value)
  if (selectedContent && selectedContent.secure_url) {
    emit('select', {
      url: selectedContent.secure_url,
      content: selectedContent
    })
    emit('close')
  }
}

// Handle file selection
const handleFileSelect = (event) => {
  const files = Array.from(event.target.files || [])
  processFiles(files)
}

// Handle drag and drop
const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files || [])
  processFiles(files)
}

// Process selected files
const processFiles = (files) => {
  // Filter by type if specified
  let filtered = files
  if (props.filterByType === 'image') {
    filtered = files.filter(f => f.type.startsWith('image/'))
  } else if (props.filterByType === 'video') {
    filtered = files.filter(f => f.type.startsWith('video/'))
  }

  if (filtered.length === 0) {
    notify.error(`Please select ${props.filterByType || 'image or video'} files`)
    return
  }

  selectedFiles.value = filtered.map(file => ({
    file,
    id: `${Date.now()}-${Math.random()}`,
    name: file.name,
    type: file.type.startsWith('image/') ? 'image' : 'video'
  }))

  // Auto-generate name from first file if not set
  if (!uploadForm.value.name && selectedFiles.value.length > 0) {
    const firstFile = selectedFiles.value[0]
    uploadForm.value.name = firstFile.name.replace(/\.[^/.]+$/, '')
  }
}

// Handle upload
const handleUpload = async () => {
  if (selectedFiles.value.length === 0) {
    notify.error('Please select files to upload')
    return
  }

  if (!uploadForm.value.name?.trim()) {
    notify.error('Please enter a name for the content')
    return
  }

  // Upload each file
  for (const fileItem of selectedFiles.value) {
    await uploadSingleFile(fileItem)
  }
}

// Upload single file
const uploadSingleFile = async (fileItem) => {
  const { file, name, type } = fileItem
  
  // Create upload progress tracker
  const uploadTracker = {
    id: fileItem.id,
    name: file.name,
    progress: 0
  }
  uploadingFiles.value.push(uploadTracker)

  try {
    // Step 1: Create content record
    // CRITICAL: Backend requires 'widget' field - Content model has ForeignKey to Widget
    // For standalone media library uploads, we need to handle this requirement
    const contentName = uploadForm.value.name.trim() || name.replace(/\.[^/.]+$/, '')
    
    if (!contentName) {
      throw new Error('Content name is required')
    }

    // Prepare content data - widget is now optional
    const contentData = {
      name: contentName,
      type: type,
    }

    // Only add widget if provided (allows standalone media library uploads)
    if (props.widgetId) {
      contentData.widget = props.widgetId
      
      // Validate widget ID format if provided
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
      const isBackendId = uuidRegex.test(props.widgetId)
      
      if (!isBackendId) {
        // Widget ID is not a UUID - it's likely a local ID
        throw new Error('Widget must be saved to the backend before uploading content. Please save the template first, then try uploading again.')
      }
    }

    console.log('[MediaLibraryModal] Creating content:', contentData)

    let content
    try {
      content = await contentStore.createContent(contentData)
      console.log('[MediaLibraryModal] Content created:', content)
    } catch (createError) {
      // DETAILED ERROR LOGGING - Log the actual server response
      console.error('[MediaLibraryModal] Content creation failed - Full Error Details:', {
        error: createError,
        response: createError.response,
        responseData: createError.response?.data,
        responseStatus: createError.response?.status,
        responseStatusText: createError.response?.statusText,
        requestConfig: {
          url: createError.config?.url,
          method: createError.config?.method,
          headers: createError.config?.headers,
          data: createError.config?.data
        },
        contentData: contentData
      })
      
      // Log validation errors specifically
      console.error('[MediaLibraryModal] Validation Errors:', createError.response?.data)

      // Extract error information - IMPROVED ERROR PARSING
      const errorData = createError.response?.data || {}
      
      // Log the actual error structure for debugging
      console.error('[MediaLibraryModal] Error Data Structure:', JSON.stringify(errorData, null, 2))
      console.error('[MediaLibraryModal] Full Error Response:', createError.response)
      
      // Handle different error response formats
      let errorDetail = ''
      let errorFields = {}
      
      // Check for nested error structure (api_error format from middleware)
      if (errorData.error === 'api_error' || errorData.error) {
        // Handle api_error format: { error: 'api_error', message: '...', details: {...} }
        // The middleware wraps DRF exceptions in this format
        errorDetail = errorData.message || 'An error occurred'
        
        // Extract details - handle both object and string formats
        if (errorData.details) {
          if (typeof errorData.details === 'object' && errorData.details !== null) {
            // DRF exceptions often have a 'detail' field inside details
            if (errorData.details.detail) {
              // This is the actual error message from DRF
              errorDetail = typeof errorData.details.detail === 'string' 
                ? errorData.details.detail 
                : JSON.stringify(errorData.details.detail)
            } else if (errorData.details.errors) {
              // Field-specific errors
              errorFields = errorData.details.errors
            } else if (errorData.details.message) {
              errorDetail = errorData.details.message
            } else {
              // If details is an object with keys, try to extract field errors
              const detailKeys = Object.keys(errorData.details)
              if (detailKeys.length > 0) {
                // Check if it's a field error structure (like { widget: ['This field is required.'] })
                const hasFieldErrors = detailKeys.some(key => 
                  Array.isArray(errorData.details[key]) || 
                  typeof errorData.details[key] === 'string'
                )
                if (hasFieldErrors) {
                  errorFields = errorData.details
                } else {
                  // Stringify the details object to show what's inside
                  try {
                    const detailsStr = JSON.stringify(errorData.details, null, 2)
                    errorDetail = `${errorDetail}\n\nDetails:\n${detailsStr}`
                  } catch (e) {
                    errorDetail = `${errorDetail}\n\nDetails: ${String(errorData.details)}`
                  }
                }
              }
            }
          } else if (typeof errorData.details === 'string') {
            errorDetail = `${errorDetail}\n\nDetails: ${errorData.details}`
          }
        }
      } else if (errorData.detail) {
        // Standard DRF error format: { detail: '...' }
        errorDetail = errorData.detail
        errorFields = errorData.errors || {}
      } else if (errorData.message) {
        // Simple message format: { message: '...' }
        errorDetail = errorData.message
        errorFields = errorData.errors || errorData
      } else if (errorData.error) {
        // Error field format: { error: '...' }
        errorDetail = errorData.error
        errorFields = errorData.errors || errorData
      } else if (typeof errorData === 'object' && Object.keys(errorData).length > 0) {
        // If errorData is an object with keys, try to extract meaningful info
        errorFields = errorData
        // Try to find a message-like field
        const possibleMessages = ['message', 'error', 'detail', 'msg', 'description']
        for (const key of possibleMessages) {
          if (errorData[key]) {
            errorDetail = errorData[key]
            break
          }
        }
        // If no message found, stringify the whole object
        if (!errorDetail) {
          errorDetail = JSON.stringify(errorData, null, 2)
        }
      } else {
        errorDetail = 'An error occurred'
      }

      // Check for specific field errors
      if (errorFields && typeof errorFields === 'object' && Object.keys(errorFields).length > 0) {
        const fieldErrorMessages = Object.keys(errorFields)
          .map(field => {
            const fieldError = errorFields[field]
            if (Array.isArray(fieldError)) {
              return `${field}: ${fieldError.join(', ')}`
            }
            if (typeof fieldError === 'object') {
              return `${field}: ${JSON.stringify(fieldError)}`
            }
            return `${field}: ${fieldError}`
          })
          .join('; ')
        
        if (fieldErrorMessages) {
          throw new Error(`Validation failed: ${fieldErrorMessages}`)
        }
      }

      // Check if error is about missing widget
      if (errorDetail.includes('widget') || errorDetail.includes('Widget') || errorFields?.widget) {
        const widgetError = errorFields?.widget
        const widgetErrorMsg = Array.isArray(widgetError) 
          ? widgetError.join(', ') 
          : (typeof widgetError === 'string' ? widgetError : 'Widget is required')
        throw new Error(`Widget Error: ${widgetErrorMsg}. Please ensure the widget is saved to the backend before uploading content.`)
      }
      
      // Check if error is about invalid widget ID
      if (errorDetail.includes('not found') || errorDetail.includes('does not exist') || errorDetail.includes('Invalid')) {
        throw new Error('Widget not found. The widget may not be saved to the backend yet. Please save the template first, then try uploading again.')
      }

      // Use detailed error message - ensure it's a string
      const errorMessage = typeof errorDetail === 'string' 
        ? errorDetail 
        : JSON.stringify(errorDetail) || 'Failed to create content record'
      throw new Error(errorMessage)
    }

    // Step 2: Upload the file using FormData
    // Backend expects 'file' field in multipart/form-data (see views.py line 1040)
    console.log('[MediaLibraryModal] Starting file upload:', {
      contentId: content.id,
      fileName: file.name,
      fileSize: file.size,
      fileType: file.type
    })

    // Simulate progress (real progress would come from axios upload progress event)
    const progressInterval = setInterval(() => {
      if (uploadTracker.progress < 90) {
        uploadTracker.progress += 10
      }
    }, 200)

    try {
      // uploadContent uses contentsAPI.upload which properly constructs FormData
      await contentStore.uploadContent(content.id, file)
      clearInterval(progressInterval)
      uploadTracker.progress = 100

      console.log('[MediaLibraryModal] File upload successful')

      // Refresh content to get updated secure_url
      await contentStore.fetchContent(content.id)
      const updatedContent = contentStore.currentContent || content

      // Move to uploaded files
      setTimeout(() => {
        const index = uploadingFiles.value.findIndex(f => f.id === fileItem.id)
        if (index > -1) {
          uploadingFiles.value.splice(index, 1)
        }
        
        uploadedFiles.value.push({
          id: updatedContent.id,
          name: updatedContent.name,
          url: updatedContent.secure_url || updatedContent.file_url || updatedContent.absolute_file_url,
          content: updatedContent
        })

        // Refresh gallery
        loadContents()
      }, 500)
    } catch (uploadError) {
      clearInterval(progressInterval)
      
      // DETAILED ERROR LOGGING for file upload
      console.error('[MediaLibraryModal] File upload failed - Full Error Details:', {
        error: uploadError,
        response: uploadError.response,
        responseData: uploadError.response?.data,
        responseStatus: uploadError.response?.status,
        responseStatusText: uploadError.response?.statusText,
        requestConfig: {
          url: uploadError.config?.url,
          method: uploadError.config?.method,
          headers: uploadError.config?.headers,
          data: uploadError.config?.data
        },
        contentId: content.id,
        fileName: file.name
      })
      
      // Log validation errors specifically
      console.error('[MediaLibraryModal] Upload Validation Errors:', uploadError.response?.data)

      const index = uploadingFiles.value.findIndex(f => f.id === fileItem.id)
      if (index > -1) {
        uploadingFiles.value.splice(index, 1)
      }

      // Extract detailed error information
      const errorData = uploadError.response?.data || {}
      const errorDetail = errorData.detail || errorData.message || errorData.error || ''
      const errorFields = errorData.errors || errorData
      const receivedFields = errorData.received_fields || []

      // Build detailed error message
      let errorMessage = errorDetail
      if (errorFields && typeof errorFields === 'object' && Object.keys(errorFields).length > 0) {
        const fieldErrors = Object.keys(errorFields)
          .map(field => {
            const fieldError = errorFields[field]
            if (Array.isArray(fieldError)) {
              return `${field}: ${fieldError.join(', ')}`
            }
            return `${field}: ${fieldError}`
          })
          .join('; ')
        errorMessage = fieldErrors || errorMessage
      }

      if (receivedFields.length > 0 && !receivedFields.includes('file')) {
        errorMessage = `File field not found. Received fields: ${receivedFields.join(', ')}. Expected: 'file'`
      }

      throw new Error(errorMessage || 'Failed to upload file')
    }
  } catch (error) {
    const index = uploadingFiles.value.findIndex(f => f.id === fileItem.id)
    if (index > -1) {
      uploadingFiles.value.splice(index, 1)
    }
    
    // Final error handling with detailed logging
    console.error('[MediaLibraryModal] Upload error summary:', {
      message: error.message,
      fullError: error,
      responseData: error.response?.data,
      validationErrors: error.response?.data
    })

    const errorMessage = error.message || 
                         error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.response?.data?.error ||
                         'Failed to upload file'
    
    notify.error(`Upload failed: ${errorMessage}`)
  }
}

// Select uploaded file
const selectUploadedFile = (file) => {
  if (file.url) {
    emit('select', {
      url: file.url,
      content: file.content
    })
    emit('close')
  }
}

// Handle delete content
const handleDeleteContent = async (content) => {
  if (!confirm(`Are you sure you want to delete "${content.name}"?`)) {
    return
  }

  try {
    await contentStore.deleteContent(content.id)
    notify.success('Content deleted successfully')
    
    // Refresh gallery
    await loadContents()
    
    // Clear selection if deleted
    if (selectedContentId.value === content.id) {
      selectedContentId.value = null
    }
  } catch (error) {
    const errorMessage = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         error.message || 
                         'Failed to delete content'
    notify.error(`Delete failed: ${errorMessage}`)
    console.error('Delete error:', error)
  }
}

// Handle image load errors
const handleImageError = (event) => {
  event.target.style.display = 'none'
}

onMounted(() => {
  // Pre-load contents if not already loaded
  if (contentStore.contents.length === 0) {
    loadContents()
  }
})
</script>

<style scoped>
.modal-enter-active {
  transition: opacity 0.3s ease-out;
}

.modal-leave-active {
  transition: opacity 0.2s ease-in;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@keyframes modalFadeUp {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
</style>
