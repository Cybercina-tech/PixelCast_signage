<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Screens</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Add Screen
        </button>
      </div>
      
      <!-- Filters -->
      <Card>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              v-model="screensStore.filters.search"
              type="text"
              placeholder="Search by name, device ID, location..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              @input="handleSearch"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              v-model="screensStore.filters.status"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
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
              class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </Card>
      
      <!-- Screens Table -->
      <Card>
        <div v-if="screensStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="screensStore.error" class="text-center py-8 text-red-600">
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
                value ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
              ]"
            >
              {{ value ? 'Online' : 'Offline' }}
            </span>
          </template>
          <template #cell-active_template="{ value }">
            <span v-if="value">{{ value.name || 'N/A' }}</span>
            <span v-else class="text-gray-400">None</span>
          </template>
          <template #actions="{ row }">
            <router-link
              :to="`/screens/${row.id}`"
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
      
      <!-- Create/Edit Modal -->
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit Screen' : 'Add Screen'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              v-model="form.name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Device ID</label>
            <input
              v-model="form.device_id"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              v-model="form.location"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              v-model="form.description"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
            ></textarea>
          </div>
        </div>
        <template #footer>
          <button
            type="button"
            @click="handleSubmit"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useScreensStore } from '@/stores/screens'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const screensStore = useScreensStore()
const toastStore = useToastStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingScreen = ref(null)

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
  if (confirm(`Are you sure you want to delete screen "${row.name}"?`)) {
    try {
      await screensStore.deleteScreen(row.id)
      toastStore.success('Screen deleted successfully')
    } catch (error) {
      toastStore.error('Failed to delete screen')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      await screensStore.updateScreen(editingScreen.value.id, form.value)
      toastStore.success('Screen updated successfully')
    } else {
      await screensStore.createScreen(form.value)
      toastStore.success('Screen created successfully')
    }
    closeModal()
  } catch (error) {
    toastStore.error(error.response?.data?.detail || 'Operation failed')
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

onMounted(async () => {
  await screensStore.fetchScreens()
})
</script>
