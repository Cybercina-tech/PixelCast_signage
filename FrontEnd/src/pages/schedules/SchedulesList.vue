<template>
  <AppLayout>
    <div class="space-y-6">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Schedules</h1>
        <button
          @click="showCreateModal = true"
          class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
        >
          Create Schedule
        </button>
      </div>
      
      <Card>
        <div v-if="schedulesStore.loading" class="text-center py-8">Loading...</div>
        <div v-else-if="schedulesStore.error" class="text-center py-8 text-red-600">
          {{ schedulesStore.error }}
        </div>
        <Table
          v-else
          :columns="columns"
          :data="schedulesStore.filteredSchedules"
          :actions="['view', 'edit', 'delete']"
          @view="handleView"
          @edit="handleEdit"
          @delete="handleDelete"
        >
          <template #cell-is_active="{ value }">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-medium',
                value ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800',
              ]"
            >
              {{ value ? 'Active' : 'Inactive' }}
            </span>
          </template>
          <template #cell-template="{ value }">
            <span v-if="value">{{ value.name || 'N/A' }}</span>
            <span v-else class="text-gray-400">None</span>
          </template>
          <template #cell-repeat_type="{ value }">
            <span class="capitalize">{{ value || 'none' }}</span>
          </template>
          <template #actions="{ row }">
            <router-link
              :to="`/schedules/${row.id}`"
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
              @click="handleExecute(row)"
              class="text-green-600 hover:text-green-900 mr-3"
            >
              Execute
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
      
      <Modal
        :show="showCreateModal || showEditModal"
        :title="showEditModal ? 'Edit Schedule' : 'Create Schedule'"
        @close="closeModal"
      >
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input v-model="form.name" type="text" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Template</label>
            <select v-model="form.template" required class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="">Select template</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">
                {{ template.name }}
              </option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Time</label>
              <input v-model="form.start_time" type="datetime-local" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Time</label>
              <input v-model="form.end_time" type="datetime-local" required class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Repeat</label>
            <select v-model="form.repeat_type" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="none">None</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <input v-model.number="form.priority" type="number" min="1" max="10" value="5" class="w-full px-3 py-2 border border-gray-300 rounded-lg" />
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="form.is_active" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Active</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSubmit" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
            {{ showEditModal ? 'Update' : 'Create' }}
          </button>
          <button type="button" @click="closeModal" class="px-4 py-2 border border-gray-300 rounded-lg">
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
import { useSchedulesStore } from '@/stores/schedules'
import { useTemplatesStore } from '@/stores/templates'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const router = useRouter()
const schedulesStore = useSchedulesStore()
const templatesStore = useTemplatesStore()
const toastStore = useToastStore()

const showCreateModal = ref(false)
const showEditModal = ref(false)
const editingSchedule = ref(null)
const templates = computed(() => templatesStore.templates)

const form = ref({
  name: '',
  template: '',
  start_time: '',
  end_time: '',
  repeat_type: 'none',
  priority: 5,
  is_active: true,
})

const columns = [
  { key: 'name', label: 'Name' },
  { key: 'template', label: 'Template' },
  { key: 'start_time', label: 'Start Time' },
  { key: 'end_time', label: 'End Time' },
  { key: 'repeat_type', label: 'Repeat' },
  { key: 'is_active', label: 'Status' },
]

const handleView = (row) => {
  router.push(`/schedules/${row.id}`)
}

const handleEdit = (row) => {
  editingSchedule.value = row
  form.value = {
    name: row.name || '',
    template: row.template?.id || row.template || '',
    start_time: row.start_time ? new Date(row.start_time).toISOString().slice(0, 16) : '',
    end_time: row.end_time ? new Date(row.end_time).toISOString().slice(0, 16) : '',
    repeat_type: row.repeat_type || 'none',
    priority: row.priority || 5,
    is_active: row.is_active ?? true,
  }
  showEditModal.value = true
}

const handleExecute = async (row) => {
  try {
    await schedulesStore.executeSchedule(row.id)
    toastStore.success('Schedule executed')
  } catch (error) {
    toastStore.error('Failed to execute schedule')
  }
}

const handleDelete = async (row) => {
  if (confirm(`Delete schedule "${row.name}"?`)) {
    try {
      await schedulesStore.deleteSchedule(row.id)
      toastStore.success('Schedule deleted')
    } catch (error) {
      toastStore.error('Failed to delete schedule')
    }
  }
}

const handleSubmit = async () => {
  try {
    if (showEditModal.value) {
      await schedulesStore.updateSchedule(editingSchedule.value.id, form.value)
      toastStore.success('Schedule updated')
    } else {
      await schedulesStore.createSchedule(form.value)
      toastStore.success('Schedule created')
    }
    closeModal()
  } catch (error) {
    toastStore.error('Operation failed')
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingSchedule.value = null
  form.value = {
    name: '',
    template: '',
    start_time: '',
    end_time: '',
    repeat_type: 'none',
    priority: 5,
    is_active: true,
  }
}

onMounted(async () => {
  await schedulesStore.fetchSchedules()
  await templatesStore.fetchTemplates()
})
</script>
