<template>
  <AppLayout>
    <div v-if="schedulesStore.loading" class="text-center py-8">Loading...</div>
    <div v-else-if="schedule" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-primary">{{ schedule.name }}</h1>
          <p class="text-secondary">{{ schedule.description || 'No description' }}</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="handleExecute"
            class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Execute Now
          </button>
          <button
            @click="handleToggleActive"
            :class="[
              'px-4 py-2 rounded-lg',
              schedule.is_active
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-green-600 text-white hover:bg-green-700',
            ]"
          >
            {{ schedule.is_active ? 'Deactivate' : 'Activate' }}
          </button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Schedule Information">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-muted">Template</dt>
              <dd class="mt-1 text-sm text-primary">{{ schedule.template?.name || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Start Time</dt>
              <dd class="mt-1 text-sm text-primary">{{ formatDate(schedule.start_time) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">End Time</dt>
              <dd class="mt-1 text-sm text-primary">{{ formatDate(schedule.end_time) }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Repeat</dt>
              <dd class="mt-1 text-sm text-primary capitalize">{{ schedule.repeat_type || 'none' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Priority</dt>
              <dd class="mt-1 text-sm text-primary">{{ schedule.priority }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Status</dt>
              <dd class="mt-1">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    schedule.is_active ? 'badge-success' : 'badge-info',
                  ]"
                >
                  {{ schedule.is_active ? 'Active' : 'Inactive' }}
                </span>
              </dd>
            </div>
          </dl>
        </Card>
        
        <Card title="Assigned Screens">
          <div v-if="schedule.screens && schedule.screens.length > 0" class="space-y-2">
            <div
              v-for="screen in schedule.screens"
              :key="screen.id"
              class="p-2 bg-gray-50 rounded"
            >
              {{ screen.name }} ({{ screen.device_id }})
            </div>
          </div>
          <div v-else class="text-center text-gray-500 py-4">
            No screens assigned
          </div>
        </Card>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useSchedulesStore } from '@/stores/schedules'
import { useNotification } from '@/composables/useNotification'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'

const route = useRoute()
const schedulesStore = useSchedulesStore()
const notify = useNotification()

const schedule = computed(() => schedulesStore.currentSchedule)

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const handleExecute = async () => {
  try {
    await schedulesStore.executeSchedule(schedule.value.id)
    notify.success('Schedule executed successfully')
  } catch (error) {
    notify.error('Failed to execute schedule')
  }
}

const handleToggleActive = async () => {
  try {
    await schedulesStore.updateSchedule(schedule.value.id, {
      is_active: !schedule.value.is_active,
    })
    notify.success(`Schedule ${schedule.value.is_active ? 'deactivated' : 'activated'}`)
  } catch (error) {
    notify.error('Failed to update schedule')
  }
}

onMounted(async () => {
  const scheduleId = route.params.id
  await schedulesStore.fetchSchedule(scheduleId)
})
</script>
