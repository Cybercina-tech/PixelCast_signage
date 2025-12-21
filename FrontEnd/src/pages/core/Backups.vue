<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">System Backups</h1>
          <p class="text-sm text-gray-600 mt-1">Manage database and media backups</p>
        </div>
        <div class="flex gap-3">
          <button
            @click="showTriggerModal = true"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Trigger Backup
          </button>
          <button
            @click="handleCleanup"
            class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
          >
            Cleanup Expired
          </button>
        </div>
      </div>

      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Backup Type</label>
            <select
              v-model="filters.backup_type"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              <option value="database">Database</option>
              <option value="media">Media</option>
              <option value="full">Full</option>
              <option value="incremental">Incremental</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="filters.status"
              @change="applyFilters"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="expired">Expired</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="clearFilters"
              class="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </Card>

      <!-- Trigger Backup Modal -->
      <Modal :show="showTriggerModal" title="Trigger Backup" @close="showTriggerModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Backup Type *</label>
            <select v-model="backupForm.backup_type" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Select backup type</option>
              <option value="database">Database</option>
              <option value="media">Media</option>
              <option value="full">Full (Database + Media)</option>
            </select>
          </div>
          <div>
            <label class="flex items-center">
              <input
                v-model="backupForm.compression"
                type="checkbox"
                class="mr-2"
              />
              <span class="text-sm font-medium text-gray-700">Enable Compression</span>
            </label>
          </div>
          <div v-if="backupForm.backup_type === 'database'">
            <label class="flex items-center">
              <input
                v-model="backupForm.include_media"
                type="checkbox"
                class="mr-2"
              />
              <span class="text-sm font-medium text-gray-700">Include Media Files</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button
            type="button"
            @click="handleTriggerBackup"
            :disabled="!backupForm.backup_type || coreStore.loading"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            {{ coreStore.loading ? 'Creating...' : 'Trigger Backup' }}
          </button>
        </template>
      </Modal>

      <!-- Backups Table -->
      <Card>
        <div v-if="coreStore.loading" class="text-center py-8">Loading backups...</div>
        <div v-else-if="coreStore.error" class="text-center py-8 text-red-600">
          {{ coreStore.error }}
        </div>
        <div v-else-if="coreStore.backups.length === 0" class="text-center py-8 text-gray-500">
          No backups found
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Size</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Started</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Completed</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created By</th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="backup in coreStore.backups" :key="backup.id">
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs capitalize">
                    {{ backup.backup_type || 'N/A' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span :class="getStatusClass(backup.status)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ backup.status || 'unknown' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatFileSize(backup.file_size) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(backup.started_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(backup.completed_at) || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDuration(backup.duration_seconds) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ backup.created_by_username || 'System' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    @click="viewBackup(backup)"
                    class="text-indigo-600 hover:text-indigo-900 mr-3"
                  >
                    View
                  </button>
                  <button
                    v-if="backup.status === 'completed'"
                    @click="verifyBackup(backup.id)"
                    class="text-green-600 hover:text-green-900 mr-3"
                  >
                    Verify
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>

      <!-- Backup Detail Modal -->
      <Modal :show="showDetailModal" title="Backup Details" @close="showDetailModal = false">
        <div v-if="selectedBackup" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Backup Type</label>
              <div class="mt-1">
                <span class="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs capitalize">
                  {{ selectedBackup.backup_type }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Status</label>
              <div class="mt-1">
                <span :class="getStatusClass(selectedBackup.status)" class="px-2 py-1 rounded text-xs font-medium">
                  {{ selectedBackup.status }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">File Path</label>
              <div class="mt-1 text-sm text-gray-900 font-mono text-xs break-all">
                {{ selectedBackup.file_path || 'N/A' }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">File Size</label>
              <div class="mt-1 text-sm text-gray-900">
                {{ formatFileSize(selectedBackup.file_size) }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Started At</label>
              <div class="mt-1 text-sm text-gray-900">{{ formatDate(selectedBackup.started_at) }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Completed At</label>
              <div class="mt-1 text-sm text-gray-900">{{ formatDate(selectedBackup.completed_at) || '-' }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Duration</label>
              <div class="mt-1 text-sm text-gray-900">
                {{ formatDuration(selectedBackup.duration_seconds) }}
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Created By</label>
              <div class="mt-1 text-sm text-gray-900">{{ selectedBackup.created_by_username || 'System' }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Compression</label>
              <div class="mt-1">
                <span :class="selectedBackup.compression ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs">
                  {{ selectedBackup.compression ? 'Enabled' : 'Disabled' }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Include Media</label>
              <div class="mt-1">
                <span :class="selectedBackup.include_media ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs">
                  {{ selectedBackup.include_media ? 'Yes' : 'No' }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Scheduled</label>
              <div class="mt-1">
                <span :class="selectedBackup.scheduled ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'" class="px-2 py-1 rounded text-xs">
                  {{ selectedBackup.scheduled ? 'Yes' : 'Manual' }}
                </span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Expires At</label>
              <div class="mt-1 text-sm text-gray-900">{{ formatDate(selectedBackup.expires_at) || 'Never' }}</div>
            </div>
          </div>
          <div v-if="selectedBackup.checksum">
            <label class="block text-sm font-medium text-gray-700">Checksum</label>
            <div class="mt-1 text-sm text-gray-900 font-mono text-xs break-all">
              {{ selectedBackup.checksum }}
            </div>
          </div>
          <div v-if="selectedBackup.error_message">
            <label class="block text-sm font-medium text-gray-700">Error Message</label>
            <div class="mt-1 p-3 bg-red-50 rounded text-sm text-red-900">{{ selectedBackup.error_message }}</div>
          </div>
          <div v-if="selectedBackup.metadata">
            <label class="block text-sm font-medium text-gray-700">Metadata</label>
            <pre class="mt-1 p-3 bg-gray-50 rounded text-xs overflow-auto">{{ JSON.stringify(selectedBackup.metadata, null, 2) }}</pre>
          </div>
        </div>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useCoreStore } from '@/stores/core'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Modal from '@/components/common/Modal.vue'

const coreStore = useCoreStore()

const filters = ref({
  backup_type: '',
  status: '',
})

const showTriggerModal = ref(false)
const showDetailModal = ref(false)
const selectedBackup = ref(null)

const backupForm = ref({
  backup_type: '',
  compression: true,
  include_media: false,
})

const applyFilters = () => {
  const params = {}
  if (filters.value.backup_type) params.backup_type = filters.value.backup_type
  if (filters.value.status) params.status = filters.value.status
  coreStore.fetchBackups(params)
}

const clearFilters = () => {
  filters.value = {
    backup_type: '',
    status: '',
  }
  coreStore.fetchBackups()
}

const handleTriggerBackup = async () => {
  try {
    await coreStore.triggerBackup(backupForm.value.backup_type, {
      compression: backupForm.value.compression,
      include_media: backupForm.value.include_media,
    })
    showTriggerModal.value = false
    backupForm.value = {
      backup_type: '',
      compression: true,
      include_media: false,
    }
  } catch (error) {
    // Error handled in store
  }
}

const handleCleanup = async () => {
  if (!confirm('Are you sure you want to cleanup expired backups?')) return
  try {
    await coreStore.cleanupBackups()
  } catch (error) {
    // Error handled in store
  }
}

const viewBackup = (backup) => {
  selectedBackup.value = backup
  showDetailModal.value = true
}

const verifyBackup = async (id) => {
  try {
    await coreStore.verifyBackup(id)
  } catch (error) {
    // Error handled in store
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB'
}

const formatDuration = (seconds) => {
  if (!seconds) return 'N/A'
  if (seconds < 60) return seconds + 's'
  if (seconds < 3600) return Math.floor(seconds / 60) + 'm ' + (seconds % 60) + 's'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hours}h ${minutes}m ${secs}s`
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    expired: 'bg-gray-100 text-gray-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  coreStore.fetchBackups()
})
</script>
