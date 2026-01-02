<template>
  <AppLayout>
    <!-- Animated Starry Background -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div class="absolute inset-0" ref="starsContainer"></div>
      <div class="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s;"></div>
      <div class="absolute top-1/2 left-1/2 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 2s;"></div>
    </div>

    <div class="relative z-10 min-h-full space-y-6 pb-6">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-3xl md:text-4xl font-bold text-white mb-2">
            <span class="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Media Library
            </span>
          </h1>
          <p class="text-slate-400">Manage and organize your digital assets</p>
        </div>
        <button
          @click="showUploadModal = true"
          class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl font-medium transition-all duration-200 flex items-center gap-2 backdrop-blur-sm border border-indigo-500/30 shadow-lg hover:shadow-xl"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Upload Media
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4">
          <div class="text-sm text-slate-400 mb-1">Total Media</div>
          <div class="text-2xl font-bold text-white">{{ contentStore.contents.length }}</div>
        </div>
        <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4">
          <div class="text-sm text-slate-400 mb-1">Images</div>
          <div class="text-2xl font-bold text-white">{{ imageCount }}</div>
        </div>
        <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4">
          <div class="text-sm text-slate-400 mb-1">Videos</div>
          <div class="text-2xl font-bold text-white">{{ videoCount }}</div>
        </div>
        <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4">
          <div class="text-sm text-slate-400 mb-1">Unassigned</div>
          <div class="text-2xl font-bold text-white">{{ unassignedCount }}</div>
        </div>
      </div>

      <!-- Filters & Search -->
      <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-4">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="md:col-span-2">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search media..."
              class="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
            />
          </div>
          <div>
            <select
              v-model="filterType"
              class="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
            >
              <option :value="null">All Types</option>
              <option value="image">Images</option>
              <option value="video">Videos</option>
            </select>
          </div>
          <div>
            <select
              v-model="filterStatus"
              class="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200"
            >
              <option :value="null">All Status</option>
              <option value="assigned">Assigned</option>
              <option value="unassigned">Unassigned</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Bulk Actions Bar -->
      <div
        v-if="selectedItems.length > 0"
        class="backdrop-blur-md bg-indigo-500/20 border border-indigo-500/30 rounded-2xl p-4 flex items-center justify-between"
      >
        <div class="text-white font-medium">
          {{ selectedItems.length }} {{ selectedItems.length === 1 ? 'item' : 'items' }} selected
        </div>
        <div class="flex gap-2">
          <button
            @click="handleBulkDelete"
            class="px-4 py-2 bg-red-600/80 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete Selected
          </button>
          <button
            @click="selectedItems = []"
            class="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm font-medium transition-colors duration-200"
          >
            Clear Selection
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="contentStore.loading && contentStore.contents.length === 0" class="flex items-center justify-center py-20">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p class="text-slate-400">Loading media library...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="contentStore.error && contentStore.contents.length === 0" class="text-center py-20">
        <div class="backdrop-blur-md bg-red-500/10 border border-red-500/30 rounded-2xl p-8 max-w-md mx-auto">
          <svg class="w-16 h-16 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-red-400 font-medium mb-2">{{ contentStore.error }}</p>
          <button
            @click="loadContents"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm transition-colors duration-200 mt-4"
          >
            Retry
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredContents.length === 0" class="text-center py-20">
        <div class="backdrop-blur-md bg-white/5 border border-white/10 rounded-2xl p-12 max-w-md mx-auto">
          <svg class="w-20 h-20 text-slate-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <h3 class="text-xl font-medium text-white mb-2">No media found</h3>
          <p class="text-slate-400 text-sm mb-6">
            {{ searchQuery || filterType || filterStatus ? 'Try adjusting your filters' : 'Upload some content to get started' }}
          </p>
          <button
            @click="showUploadModal = true"
            class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-xl font-medium transition-all duration-200"
          >
            Upload Media
          </button>
        </div>
      </div>

      <!-- Media Grid -->
      <div
        v-else
        ref="gridContainer"
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4"
        @scroll="handleScroll"
      >
        <div
          v-for="content in filteredContents"
          :key="content.id"
          @click="toggleSelection(content.id)"
          :class="[
            'group relative cursor-pointer rounded-xl overflow-hidden border-2 transition-all duration-200 backdrop-blur-md bg-white/5',
            selectedItems.includes(content.id)
              ? 'border-indigo-500 ring-2 ring-indigo-500/50 shadow-lg scale-105'
              : 'border-white/10 hover:border-white/20 hover:shadow-lg'
          ]"
        >
          <!-- Thumbnail -->
          <div class="aspect-square bg-gray-900 relative overflow-hidden">
            <!-- Smart Media Preview -->
            <SmartMediaPreview
              :file-url="content.secure_url || content.absolute_file_url || content.file_url"
              :file-type="content.type"
              :alt="content.name || 'Media'"
              :video-duration="content.video_duration"
              :enable-hover-zoom="true"
              :play-on-hover="true"
              :show-duration="true"
              class="w-full h-full"
            />

            <!-- Selection Checkbox -->
            <div class="absolute top-2 left-2">
              <div
                :class="[
                  'w-6 h-6 rounded border-2 flex items-center justify-center transition-all duration-200',
                  selectedItems.includes(content.id)
                    ? 'bg-indigo-500 border-indigo-500'
                    : 'bg-black/50 border-white/30 group-hover:border-white/50'
                ]"
              >
                <svg
                  v-if="selectedItems.includes(content.id)"
                  class="w-4 h-4 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            <!-- Status Badge -->
            <div class="absolute top-2 right-2 flex gap-1">
              <span
                :class="[
                  'px-2 py-1 rounded text-xs font-medium',
                  content.is_assigned ? 'bg-green-500/80 text-white' : 'bg-amber-500/80 text-white'
                ]"
              >
                {{ content.is_assigned ? 'Assigned' : 'Unassigned' }}
              </span>
              <span
                :class="[
                  'px-2 py-1 rounded text-xs font-medium',
                  content.type === 'image' ? 'bg-blue-500/80 text-white' : 'bg-purple-500/80 text-white'
                ]"
              >
                {{ content.type === 'image' ? 'IMG' : 'VID' }}
              </span>
            </div>

            <!-- Hover Overlay -->
            <div class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors duration-200 flex items-center justify-center gap-2 opacity-0 group-hover:opacity-100">
              <button
                @click.stop="handlePreview(content)"
                class="px-3 py-2 bg-indigo-600/80 hover:bg-indigo-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
                title="Preview"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                Preview
              </button>
              <button
                @click.stop="handleDelete(content)"
                class="px-3 py-2 bg-red-600/80 hover:bg-red-600 text-white rounded-lg text-sm font-medium transition-colors duration-200 flex items-center gap-2"
                title="Delete"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Delete
              </button>
            </div>
          </div>

          <!-- Content Info -->
          <div class="p-3 bg-white/5">
            <p class="text-sm text-white font-medium truncate" :title="content.name">
              {{ content.name || 'Untitled' }}
            </p>
            <div class="flex items-center justify-between mt-2 text-xs text-slate-400">
              <span v-if="content.image_width && content.image_height">
                {{ content.image_width }}×{{ content.image_height }}
              </span>
              <span v-if="content.file_size">
                {{ formatFileSize(content.file_size) }}
              </span>
            </div>
            <div class="text-xs text-slate-500 mt-1">
              {{ formatDate(content.created_at) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Infinite Scroll Loader -->
      <div v-if="loadingMore" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
      </div>
    </div>

    <!-- Upload Modal -->
    <MediaLibraryModal
      :show="showUploadModal"
      @close="showUploadModal = false"
      @select="handleMediaSelected"
    />

    <!-- Full Screen Preview Modal -->
    <FullScreenPreviewModal
      :show="showPreviewModal"
      :file-url="previewContent?.secure_url || previewContent?.absolute_file_url || previewContent?.file_url"
      :file-type="previewContent?.type"
      :media-name="previewContent?.name"
      :video-duration="previewContent?.video_duration"
      :metadata="{
        width: previewContent?.image_width,
        height: previewContent?.image_height,
        fileSize: previewContent?.file_size,
        duration: previewContent?.video_duration,
        createdAt: previewContent?.created_at
      }"
      @close="showPreviewModal = false"
    />
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useContentStore } from '@/stores/content'
import { useNotification } from '@/composables/useNotification'
import AppLayout from '@/components/layout/AppLayout.vue'
import MediaLibraryModal from '@/components/common/MediaLibraryModal.vue'
import SmartMediaPreview from '@/components/common/SmartMediaPreview.vue'
import FullScreenPreviewModal from '@/components/common/FullScreenPreviewModal.vue'

const contentStore = useContentStore()
const notify = useNotification()

// State
const showUploadModal = ref(false)
const showPreviewModal = ref(false)
const previewContent = ref(null)
const searchQuery = ref('')
const filterType = ref(null)
const filterStatus = ref(null)
const selectedItems = ref([])
const loadingMore = ref(false)
const gridContainer = ref(null)
const starsContainer = ref(null)
const page = ref(1)
const hasMore = ref(true)

// Computed
const imageCount = computed(() => contentStore.contents.filter(c => c.type === 'image').length)
const videoCount = computed(() => contentStore.contents.filter(c => c.type === 'video').length)
const unassignedCount = computed(() => contentStore.contents.filter(c => !c.is_assigned).length)

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

  // Filter by status
  if (filterStatus.value === 'assigned') {
    filtered = filtered.filter(c => c.is_assigned)
  } else if (filterStatus.value === 'unassigned') {
    filtered = filtered.filter(c => !c.is_assigned)
  }

  return filtered
})

// Methods
const loadContents = async () => {
  try {
    await contentStore.fetchContents({ page: page.value })
  } catch (error) {
    console.error('Failed to load contents:', error)
  }
}

const handleScroll = () => {
  if (!gridContainer.value || loadingMore.value || !hasMore.value) return

  const container = gridContainer.value
  const scrollTop = container.scrollTop
  const scrollHeight = container.scrollHeight
  const clientHeight = container.clientHeight

  // Load more when 80% scrolled
  if (scrollTop + clientHeight >= scrollHeight * 0.8) {
    loadMore()
  }
}

const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return

  loadingMore.value = true
  try {
    page.value++
    const response = await contentStore.fetchContents({ page: page.value })
    const results = response?.results || response || []
    if (results.length === 0) {
      hasMore.value = false
    }
  } catch (error) {
    console.error('Failed to load more:', error)
    page.value-- // Revert page on error
  } finally {
    loadingMore.value = false
  }
}

const toggleSelection = (id) => {
  const index = selectedItems.value.indexOf(id)
  if (index > -1) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(id)
  }
}

const handleBulkDelete = async () => {
  if (selectedItems.value.length === 0) return

  if (!confirm(`Are you sure you want to delete ${selectedItems.value.length} item(s)?`)) {
    return
  }

  try {
    for (const id of selectedItems.value) {
      await contentStore.deleteContent(id)
    }
    notify.success(`Deleted ${selectedItems.value.length} item(s) successfully`)
    selectedItems.value = []
  } catch (error) {
    notify.error('Failed to delete items')
  }
}

const handlePreview = (content) => {
  previewContent.value = content
  showPreviewModal.value = true
}

const handleDelete = async (content) => {
  if (!confirm(`Are you sure you want to delete "${content.name}"?`)) {
    return
  }

  try {
    await contentStore.deleteContent(content.id)
    notify.success('Content deleted successfully')
    if (selectedItems.value.includes(content.id)) {
      selectedItems.value = selectedItems.value.filter(id => id !== content.id)
    }
  } catch (error) {
    notify.error('Failed to delete content')
  }
}

const handleMediaSelected = (data) => {
  // Media was selected from library - refresh list
  loadContents()
}


const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const formatDuration = (seconds) => {
  if (!seconds) return ''
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Create animated stars
const createStars = () => {
  if (!starsContainer.value) return

  const container = starsContainer.value
  const starCount = 50

  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div')
    star.className = 'absolute rounded-full bg-white'
    star.style.width = `${Math.random() * 3 + 1}px`
    star.style.height = star.style.width
    star.style.left = `${Math.random() * 100}%`
    star.style.top = `${Math.random() * 100}%`
    star.style.opacity = Math.random() * 0.5 + 0.5
    star.style.animation = `starry-twinkle ${Math.random() * 3 + 2}s ease-in-out infinite`
    star.style.animationDelay = `${Math.random() * 2}s`
    container.appendChild(star)
  }
}

onMounted(async () => {
  await loadContents()
  createStars()
})

onUnmounted(() => {
  if (starsContainer.value) {
    starsContainer.value.innerHTML = ''
  }
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
