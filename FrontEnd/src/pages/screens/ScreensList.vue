<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-primary">Screens</h1>
        <div class="flex items-center space-x-3">
          <button
            v-if="selectedItems && selectedItems.length > 0"
            @click="showBulkModal = true"
            class="btn-primary px-4 py-2 rounded-lg"
          >
            Bulk Operations ({{ selectedItems.length }})
          </button>
          <button
            @click="$router.push('/screens/add')"
            class="btn-primary px-4 py-2 rounded-lg"
          >
            Add Screen
          </button>
        </div>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="label-base block text-sm mb-1">Search</label>
            <input
              v-model="screensStore.filters.search"
              type="text"
              placeholder="Search by name, device ID, location..."
              class="input-base w-full px-3 py-2 rounded-lg"
              @input="handleSearch"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Status</label>
            <select
              v-model="screensStore.filters.status"
              class="select-base w-full px-3 py-2 rounded-lg"
              @change="handleFilter"
            >
              <option :value="null">All</option>
              <option value="online">Online</option>
              <option value="offline">Offline</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="clearFilters"
              class="btn-outline px-4 py-2 rounded-lg"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </Card>
      
      <!-- Screens Table -->
      <Card>
        <div v-if="screensStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="screensStore.error" class="text-center py-8 text-error">
          {{ screensStore.error }}
        </div>
        <Table
          v-else
          :columns="columns"
          :data="screensStore.filteredScreens"
          :actions="['view', 'edit', 'delete']"
          @view="handleView"
          @edit="handleEdit"
          @delete="handleDelete"
        >
          <template #cell-is_online="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value ? 'badge-success' : 'badge-error',
              ]"
            >
              {{ value ? 'Online' : 'Offline' }}
            </span>
          </template>
          <template #cell-active_template="{ value }">
            <span v-if="value" class="text-primary">{{ value.name || 'N/A' }}</span>
            <span v-else class="text-muted">None</span>
          </template>
          <template #actions="{ row }">
            <div class="flex items-center justify-end gap-1">
              <router-link
                :to="`/screens/${row.id}`"
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
      
      <!-- Create/Edit Modal -->
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit Screen' : 'Add Screen'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Device ID</label>
            <input
              v-model="form.device_id"
              type="text"
              required
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Location</label>
            <input
              v-model="form.location"
              type="text"
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="textarea-base w-full px-3 py-2 rounded-lg"
            ></textarea>
          </div>
        </div>
        <template #footer>
          <button
            type="button"
            @click="handleSubmit"
            class="btn-primary px-4 py-2 rounded-lg"
          >
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button
            type="button"
            @click="closeModal"
            class="btn-outline px-4 py-2 rounded-lg"
          >
            Cancel
          </button>
        </template>
      </Modal>
      
      <!-- Bulk Operations Modal -->
      <BulkOperations
        v-if="showBulkModal"
        title="Bulk Operations"
        operation="delete"
        :selectedItems="selectedItems"
        @close="showBulkModal = false"
        @confirm="handleBulkOperation"
      />
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { EyeIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { useScreensStore } from '@/stores/screens'
import { useNotification } from '@/composables/useNotification'
import { useDeleteConfirmation } from '@/composables/useDeleteConfirmation'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'
import BulkOperations from '@/components/common/BulkOperations.vue'

const router = useRouter()
const screensStore = useScreensStore()
const notify = useNotification()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showBulkModal = ref(false)
const editingScreen = ref(null)
const selectedItems = ref([])

const form = ref({
  name: '',
  device_id: '',
  location: '',
  description: '',
})

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'device_id', label: 'Device ID' },
  { key: 'location', label: 'Location' },
  { key: 'is_online', label: 'Status' },
  { key: 'active_template', label: 'Active Template' },
]

const handleSearch = () => {
  // Filtering is handled by getter
}

const handleFilter = () => {
  // Filtering is handled by getter
}

const clearFilters = () => {
  screensStore.clearFilters()
  screensStore.fetchScreens()
}

const handleView = (row) => {
  router.push(`/screens/${row.id}`)
}

const handleEdit = (row) => {
  editingScreen.value = row
  form.value = {
    name: row.name || '',
    device_id: row.device_id || '',
    location: row.location || '',
    description: row.description || '',
  }
  showEditModal.value = true
}

const handleDelete = async (row) => {
  try {
    const { confirmDelete } = useDeleteConfirmation()
    await confirmDelete(
      row.id,
      async () => {
        await screensStore.deleteScreen(row.id)
      },
      {
        title: 'Delete Screen?',
        message: 'This will permanently delete the screen and all its associated data. This action cannot be undone.',
        itemName: row.name,
        confirmText: 'Yes, Delete Screen',
        cancelText: 'Cancel'
      }
    )
    notify.success('Screen deleted successfully')
  } catch (error) {
    if (error.message !== 'Delete cancelled') {
      notify.error('Failed to delete screen')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      await screensStore.updateScreen(editingScreen.value.id, form.value)
      notify.success('Screen updated successfully')
    } else {
      await screensStore.createScreen(form.value)
      notify.success('Screen created successfully')
    }
    closeModal()
  } catch (error) {
    notify.error(error.response?.data?.detail || 'Operation failed')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingScreen.value = null
  form.value = {
    name: '',
    device_id: '',
    location: '',
    description: '',
  }
}

const handleBulkOperation = async (payload) => {
  try {
    // Handle bulk operations here
    // For now, just close the modal
    showBulkModal.value = false
    selectedItems.value = []
    notify.success('Bulk operation completed')
  } catch (error) {
    notify.error('Failed to perform bulk operation')
  }
}

onMounted(async () => {
  await screensStore.fetchScreens()
})
</script>
