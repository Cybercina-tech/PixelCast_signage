<template>
  <AppLayout>
    <div v-if="contentStore.loading" class="text-center py-8">Loading...</div>
    <div v-else-if="contentStore.error" class="text-center py-8 text-red-600">
      {{ contentStore.error }}
    </div>
    <div v-else-if="content" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-primary">{{ content.name }}</h1>
          <p class="text-secondary">{{ content.type }}</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="handleRetryDownload"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry Download
          </button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <!-- Preview -->
        <Card title="Preview">
          <div v-if="content.type === 'image' && content.file_url" class="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
            <img :src="content.file_url" :alt="content.name" class="w-full h-full object-contain" />
          </div>
          <div v-else-if="content.type === 'video' && content.file_url" class="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg">
            <video :src="content.file_url" controls class="w-full h-full"></video>
          </div>
          <div v-else-if="content.type === 'text'" class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p class="whitespace-pre-wrap text-primary">{{ content.text_content || content.content_json?.text || 'No text content' }}</p>
          </div>
          <div v-else class="aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg flex items-center justify-center">
            <span class="text-muted">Preview not available</span>
          </div>
        </Card>
        
        <!-- Details -->
        <Card title="Content Details">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-muted">Type</dt>
              <dd class="mt-1 text-sm text-primary capitalize">{{ content.type }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Download Status</dt>
              <dd class="mt-1">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    content.download_status === 'success' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : '',
                    content.download_status === 'failed' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' : '',
                    content.download_status === 'downloading' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' : '',
                    content.download_status === 'pending' ? 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-300' : '',
                  ]"
                >
                  {{ content.download_status || 'pending' }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">File Size</dt>
              <dd class="mt-1 text-sm text-primary">{{ formatFileSize(content.file_size) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Retry Count</dt>
              <dd class="mt-1 text-sm text-primary">{{ content.retry_count || 0 }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Created</dt>
              <dd class="mt-1 text-sm text-primary">{{ formatDate(content.created_at) }}</dd>
            </div>
          </dl>
        </Card>
      </div>
      
      <!-- Download Status per Screen -->
      <Card title="Download Status by Screen">
        <div v-if="!downloadLogs || downloadLogs.length === 0" class="text-center text-muted py-4">
          No download logs available
        </div>
        <Table
          v-else
          :columns="logColumns"
          :data="downloadLogs || []"
        />
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useContentStore } from '@/stores/content'
import { useLogsStore } from '@/stores/logs'
import { useScreensStore } from '@/stores/screens'
import { useNotification } from '@/composables/useNotification'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'

const route = useRoute()
const contentStore = useContentStore()
const logsStore = useLogsStore()
const screensStore = useScreensStore()
const notify = useNotification()

const content = computed(() => contentStore.currentContent)
const downloadLogs = ref([])

const logColumns = [
  { key: 'screen', label: 'Screen' },
  { key: 'status', label: 'Status' },
  { key: 'retry_count', label: 'Retries' },
  { key: 'downloaded_at', label: 'Downloaded' },
]

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(2)} MB`
}

const handleRetryDownload = async () => {
  if (!content.value) return
  
  try {
    // Get first screen for retry (in real app, you'd select screen)
    const screensResponse = await screensStore.fetchScreens()
    const screens = screensResponse.results || screensResponse.data?.results || screensResponse.data || screensStore.screens || []
    if (screens.length > 0) {
      await contentStore.retryDownload(content.value.id, screens[0].id)
      notify.success('Download retry initiated')
    } else {
      notify.warning('No screens available for download')
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to retry download'
    notify.error(errorMsg)
  }
}

onMounted(async () => {
  const contentId = route.params.id
  await contentStore.fetchContent(contentId)
  
  // Fetch download logs
  try {
    const response = await logsStore.fetchContentDownloadLogs({ content_id: contentId })
    // Backend returns paginated results or array
    downloadLogs.value = response.results || response.data?.results || response.data || response || []
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message
    notify.error(errorMsg || 'Failed to load download logs')
  }
})
</script>
