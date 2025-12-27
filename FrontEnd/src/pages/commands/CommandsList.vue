<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-primary">Commands</h1>
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
            <label class="label-base block text-sm mb-1">Type</label>
            <select v-model="commandsStore.filters.type" class="select-base w-full px-3 py-2 rounded-lg">
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
            <label class="label-base block text-sm mb-1">Status</label>
            <select v-model="commandsStore.filters.status" class="select-base w-full px-3 py-2 rounded-lg">
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
                value === 'done' ? 'badge-success' : '',
                value === 'failed' ? 'badge-error' : '',
                value === 'pending' ? 'badge-warning' : '',
                value === 'executing' ? 'badge-primary' : '',
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
            <div class="flex items-center justify-end gap-1">
              <router-link
                :to="`/commands/${row.id}`"
                class="action-btn-view"
                title="View"
              >
                <EyeIcon class="w-4 h-4" />
              </router-link>
              <button
                v-if="row.status === 'failed'"
                @click="handleRetry(row)"
                class="action-btn-retry"
                title="Retry"
              >
                <ArrowPathIcon class="w-4 h-4" />
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
      
      <!-- Create Modal -->
      <Modal :show="showCreateModal" title="Create Command" @close="showCreateModal = false">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Screen</label>
            <select v-model="form.screen" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Select screen</option>
              <option v-for="screen in screens" :key="screen.id" :value="screen.id">
                {{ screen.name }} ({{ screen.device_id }})
              </option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Command Type</label>
            <select v-model="form.type" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="restart">Restart</option>
              <option value="refresh">Refresh</option>
              <option value="change_template">Change Template</option>
              <option value="display_message">Display Message</option>
              <option value="sync_content">Sync Content</option>
              <option value="custom">Custom</option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Payload (JSON)</label>
            <textarea
              v-model="form.payload"
              rows="4"
              class="textarea-base w-full px-3 py-2 rounded-lg font-mono text-sm"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Priority</label>
            <input v-model.number="form.priority" type="number" min="1" max="10" value="5" class="input-base w-full px-3 py-2 rounded-lg" />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            Create
          </button>
          <button type="button" @click="showCreateModal = false" class="btn-outline px-4 py-2 rounded-lg">
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
import { EyeIcon, TrashIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import { useCommandsStore } from '@/stores/commands'
import { useScreensStore } from '@/stores/screens'
import { useNotification } from '@/composables/useNotification'
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const commandsStore = useCommandsStore()
const screensStore = useScreensStore()
const notify = useNotification()

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
    notify.success('Command retry initiated')
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to retry command'
    notify.error(errorMsg)
  }
}

const handleDelete = async (row) => {
  try {
    const { confirmDelete } = useDeleteConfirmation()
    await confirmDelete(
      row.id,
      async () => {
        await commandsStore.deleteCommand(row.id)
      },
      {
        title: 'Delete Command?',
        message: 'This will permanently delete the command. This action cannot be undone.',
        itemName: row.name || `Command ${row.type}`,
        confirmText: 'Yes, Delete Command',
        cancelText: 'Cancel'
      }
    )
    notify.success('Command deleted successfully')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to delete command'
      notify.error(errorMsg)
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
    
    notify.success('Command created')
    showCreateModal.value = false
    form.value = { screen: '', type: 'restart', payload: '{}', priority: 5 }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to create command'
    notify.error(errorMsg)
  }
}

onMounted(async () => {
  await commandsStore.fetchCommands()
  await screensStore.fetchScreens()
})
</script>
