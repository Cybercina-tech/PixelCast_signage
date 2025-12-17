<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Commands</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Create Command
        </button>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select v-model="commandsStore.filters.type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option :value="null">All</option>
              <option value="restart">Restart</option>
              <option value="refresh">Refresh</option>
              <option value="change_template">Change Template</option>
              <option value="display_message">Display Message</option>
              <option value="sync_content">Sync Content</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select v-model="commandsStore.filters.status" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option :value="null">All</option>
              <option value="pending">Pending</option>
              <option value="executing">Executing</option>
              <option value="done">Done</option>
              <option value="failed">Failed</option>
            </select>
          </div>
        </div>
      </Card>
      
      <!-- Commands Table -->
      <Card>
        <div v-if="commandsStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="commandsStore.error" class="text-center py-8 text-red-600">
          {{ commandsStore.error }}
        </div>
        <Table
          v-else
          :columns="columns"
          :data="commandsStore.filteredCommands"
          :actions="['view', 'retry', 'delete']"
          @view="handleView"
          @retry="handleRetry"
          @delete="handleDelete"
        >
          <template #cell-status="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value === 'done' ? 'bg-green-100 text-green-800' : '',
                value === 'failed' ? 'bg-red-100 text-red-800' : '',
                value === 'pending' ? 'bg-yellow-100 text-yellow-800' : '',
                value === 'executing' ? 'bg-blue-100 text-blue-800' : '',
              ]"
            >
              {{ value }}
            </span>
          </template>
          <template #cell-screen="{ value, row }">
            <span v-if="row.screen_name">{{ row.screen_name }}</span>
            <span v-else-if="value">{{ value.name || value.device_id || 'N/A' }}</span>
            <span v-else class="text-gray-400">None</span>
          </template>
          <template #actions="{ row }">
            <router-link
              :to="`/commands/${row.id}`"
              class="text-indigo-600 hover:text-indigo-900 mr-3"
            >
              View
            </router-link>
            <button
              v-if="row.status === 'failed'"
              @click="handleRetry(row)"
              class="text-blue-600 hover:text-blue-900 mr-3"
            >
              Retry
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
      
      <!-- Create Modal -->
      <Modal :show="showCreateModal" title="Create Command" @close="showCreateModal = false">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Screen</label>
            <select v-model="form.screen" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Select screen</option>
              <option v-for="screen in screens" :key="screen.id" :value="screen.id">
                {{ screen.name }} ({{ screen.device_id }})
              </option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Command Type</label>
            <select v-model="form.type" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="restart">Restart</option>
              <option value="refresh">Refresh</option>
              <option value="change_template">Change Template</option>
              <option value="display_message">Display Message</option>
              <option value="sync_content">Sync Content</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Payload (JSON)</label>
            <textarea
              v-model="form.payload"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg font-mono text-sm"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <input v-model.number="form.priority" type="number" min="1" max="10" value="5" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Create
          </button>
          <button type="button" @click="showCreateModal = false" class="px-4 py-2 border border-gray-300 rounded-lg">
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
import { useCommandsStore } from '@/stores/commands'
import { useScreensStore } from '@/stores/screens'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const commandsStore = useCommandsStore()
const screensStore = useScreensStore()
const toastStore = useToastStore()

const showCreateModal = ref(false)
const screens = computed(() => screensStore.screens)

const form = ref({
  screen: '',
  type: 'restart',
  payload: '{}',
  priority: 5,
})

const columns = [
  { key: 'type', label: 'Type' },
  { key: 'screen', label: 'Screen' },
  { key: 'status', label: 'Status' },
  { key: 'created_at', label: 'Created' },
]

const handleView = (row) => {
  router.push(`/commands/${row.id}`)
}

const handleRetry = async (row) => {
  try {
    await commandsStore.retryCommand(row.id)
    toastStore.success('Command retry initiated')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to retry command'
    toastStore.error(errorMsg)
  }
}

const handleDelete = async (row) => {
  if (confirm(`Delete command?`)) {
    try {
      await commandsStore.deleteCommand(row.id)
      toastStore.success('Command deleted')
    } catch (error) {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to delete command'
      toastStore.error(errorMsg)
    }
  }
}

const handleSubmit = async () => {
  try {
    let payload = {}
    try {
      payload = JSON.parse(form.value.payload)
    } catch (e) {
      payload = { message: form.value.payload }
    }
    
    await commandsStore.createCommand({
      screen_id: form.value.screen,
      type: form.value.type,
      payload,
      priority: form.value.priority,
    })
    
    toastStore.success('Command created')
    showCreateModal.value = false
    form.value = { screen: '', type: 'restart', payload: '{}', priority: 5 }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to create command'
    toastStore.error(errorMsg)
  }
}

onMounted(async () => {
  await commandsStore.fetchCommands()
  await screensStore.fetchScreens()
})
</script>
