<template>
  <AppLayout>
    <div v-if="screensStore.loading" class="text-center py-8">Loading...</div>
    <div v-else-if="screensStore.error" class="text-center py-8 text-red-600">
      {{ screensStore.error }}
    </div>
    <div v-else-if="screen" class="space-y-6">
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-primary">{{ screen.name }}</h1>
          <p class="text-secondary">{{ screen.device_id }}</p>
        </div>
        <div class="flex gap-2">
          <button
            @click="showCommandModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Send Command
          </button>
          <button
            @click="showTemplateModal = true"
            class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Activate Template
          </button>
        </div>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- General Info -->
        <Card title="General Information">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-muted">Device ID</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.device_id }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Location</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.location || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Status</dt>
              <dd class="mt-1">
                <span
                  :class="[
                    'px-2 py-1 rounded-full text-xs font-medium',
                    screen.is_online ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300',
                  ]"
                >
                  {{ screen.is_online ? 'Online' : 'Offline' }}
                </span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Last Heartbeat</dt>
              <dd class="mt-1 text-sm text-primary">
                {{ screen.last_heartbeat_at ? formatDate(screen.last_heartbeat_at) : 'Never' }}
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Active Template</dt>
              <dd class="mt-1 text-sm text-primary">
                {{ screen.active_template?.name || 'None' }}
              </dd>
            </div>
          </dl>
        </Card>
        
        <!-- Health Metrics -->
        <Card title="Health Metrics">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-muted">CPU Usage</dt>
              <dd class="mt-1">
                <div class="flex items-center">
                  <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                    <div
                      class="bg-blue-600 h-2 rounded-full"
                      :style="{ width: `${healthMetrics.cpu_usage || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-primary">{{ healthMetrics.cpu_usage || 0 }}%</span>
                </div>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Memory Usage</dt>
              <dd class="mt-1">
                <div class="flex items-center">
                  <div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                    <div
                      class="bg-green-600 h-2 rounded-full"
                      :style="{ width: `${healthMetrics.memory_usage || 0}%` }"
                    ></div>
                  </div>
                  <span class="text-sm text-primary">{{ healthMetrics.memory_usage || 0 }}%</span>
                </div>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Latency</dt>
              <dd class="mt-1 text-sm text-primary">
                {{ healthMetrics.latency || 0 }}ms
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Brightness</dt>
              <dd class="mt-1 text-sm text-primary">
                {{ screen.brightness || 'N/A' }}
              </dd>
            </div>
          </dl>
        </Card>
        
        <!-- System Info -->
        <Card title="System Information">
          <dl class="space-y-3">
            <div>
              <dt class="text-sm font-medium text-muted">App Version</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.app_version || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">OS Version</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.os_version || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Device Model</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.device_model || 'N/A' }}</dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Screen Resolution</dt>
              <dd class="mt-1 text-sm text-primary">
                <span v-if="screen.screen_width && screen.screen_height">
                  {{ screen.screen_width }}x{{ screen.screen_height }}
                </span>
                <span v-else>N/A</span>
              </dd>
            </div>
            <div>
              <dt class="text-sm font-medium text-muted">Last IP</dt>
              <dd class="mt-1 text-sm text-primary">{{ screen.last_ip || 'N/A' }}</dd>
            </div>
          </dl>
        </Card>
      </div>
      
      <!-- Commands Queue -->
      <Card title="Commands Queue">
        <div v-if="!pendingCommands || pendingCommands.length === 0" class="text-center text-muted py-4">
          No pending commands
        </div>
        <Table
          v-else
          :columns="commandColumns"
          :data="pendingCommands || []"
        />
      </Card>
      
      <!-- Command History -->
      <Card title="Command History">
        <div class="space-y-2">
          <div
            v-for="cmd in commandHistory"
            :key="cmd.id"
            class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
          >
            <div class="flex justify-between items-start">
              <div>
                <p class="font-medium text-primary">{{ cmd.type }}</p>
                <p class="text-sm text-secondary">{{ cmd.name }}</p>
              </div>
              <span
                :class="[
                  'px-2 py-1 rounded-full text-xs font-medium',
                  cmd.status === 'done' ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' : '',
                  cmd.status === 'failed' ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300' : '',
                  cmd.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' : '',
                  cmd.status === 'executing' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300' : '',
                ]"
              >
                {{ cmd.status }}
              </span>
            </div>
            <p class="text-xs text-muted mt-2">
              {{ formatDate(cmd.created_at) }}
            </p>
          </div>
        </div>
      </Card>
      
      <!-- Logs -->
      <Card title="Recent Logs">
        <div class="space-y-2">
          <div
            v-for="log in recentLogs"
            :key="log.id"
            class="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg"
          >
            <p class="text-sm text-primary">{{ log.message || `${log.status} - ${formatDate(log.recorded_at || log.created_at)}` }}</p>
          </div>
        </div>
      </Card>
      
      <!-- Modals -->
      <Modal :show="showCommandModal" title="Send Command" @close="showCommandModal = false">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Command Type</label>
            <select v-model="commandForm.type" required class="select-base w-full px-3 py-2 rounded-lg">
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
              v-model="commandForm.payload"
              rows="4"
              class="textarea-base w-full px-3 py-2 rounded-lg font-mono text-sm"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Priority</label>
            <input
              v-model.number="commandForm.priority"
              type="number"
              min="1"
              max="10"
              value="5"
              class="input-base w-full px-3 py-2 rounded-lg"
            />
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleSendCommand" class="btn-primary px-4 py-2 rounded-lg">
            Send Command
          </button>
          <button type="button" @click="showCommandModal = false" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
      
      <Modal :show="showTemplateModal" title="Activate Template" @close="showTemplateModal = false">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Template</label>
            <select v-model="templateForm.template_id" required class="select-base w-full px-3 py-2 rounded-lg">
              <option value="">Select a template</option>
              <option v-for="template in templates" :key="template.id" :value="template.id">
                {{ template.name }}
              </option>
            </select>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="templateForm.sync_content" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-secondary">Sync content automatically</span>
            </label>
          </div>
        </div>
        <template #footer>
          <button type="button" @click="handleActivateTemplate" class="btn-primary px-4 py-2 rounded-lg">
            Activate
          </button>
          <button type="button" @click="showTemplateModal = false" class="btn-outline px-4 py-2 rounded-lg">
            Cancel
          </button>
        </template>
      </Modal>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useScreensStore } from '@/stores/screens'
import { useTemplatesStore } from '@/stores/templates'
import { useCommandsStore } from '@/stores/commands'
import { useLogsStore } from '@/stores/logs'
import { useNotification } from '@/composables/useNotification'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import Table from '@/components/common/Table.vue'
import Modal from '@/components/common/Modal.vue'

const route = useRoute()
const screensStore = useScreensStore()
const templatesStore = useTemplatesStore()
const commandsStore = useCommandsStore()
const logsStore = useLogsStore()
const notify = useNotification()

const screen = computed(() => screensStore.currentScreen)
const templates = computed(() => templatesStore.templates)
const pendingCommands = ref([])
const commandHistory = ref([])
const recentLogs = ref([])
const healthMetrics = ref({
  cpu_usage: 0,
  memory_usage: 0,
  latency: 0,
})

const showCommandModal = ref(false)
const showTemplateModal = ref(false)

const commandForm = ref({
  type: 'restart',
  payload: '{}',
  priority: 5,
})

const templateForm = ref({
  template_id: '',
  sync_content: true,
})

const commandColumns = [
  { key: 'type', label: 'Type' },
  { key: 'name', label: 'Name' },
  { key: 'status', label: 'Status' },
  { key: 'created_at', label: 'Created' },
]

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}

const handleSendCommand = async () => {
  try {
    let payload = {}
    try {
      payload = JSON.parse(commandForm.value.payload)
    } catch (e) {
      payload = { message: commandForm.value.payload }
    }
    
    await commandsStore.createCommand({
      screen_id: screen.value.id,
      type: commandForm.value.type,
      payload,
      priority: commandForm.value.priority,
    })
    
    notify.success('Command sent successfully')
    showCommandModal.value = false
    commandForm.value = { type: 'restart', payload: '{}', priority: 5 }
    await loadCommands()
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to send command'
    notify.error(errorMsg)
  }
}

const handleActivateTemplate = async () => {
  try {
    await templatesStore.activateOnScreen(
      templateForm.value.template_id,
      screen.value.id,
      templateForm.value.sync_content
    )
    notify.success('Template activated successfully')
    showTemplateModal.value = false
    templateForm.value = { template_id: '', sync_content: true }
    await screensStore.fetchScreen(screen.value.id)
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message || 'Failed to activate template'
    notify.error(errorMsg)
  }
}

const loadCommands = async () => {
  try {
    const response = await commandsStore.fetchCommands({ screen: screen.value.id })
    // Backend returns paginated results or array
    const commands = response.results || response.data?.results || response.data || response || []
    pendingCommands.value = commands.filter(c => c.status === 'pending')
    commandHistory.value = commands.filter(c => c.status !== 'pending').slice(0, 10)
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message
    notify.error(errorMsg || 'Failed to load commands')
  }
}

const loadLogs = async () => {
  try {
    const response = await logsStore.fetchScreenStatusLogs({ screen_id: screen.value.id, page_size: 10 })
    // Backend returns paginated results or array
    recentLogs.value = response.results || response.data?.results || response.data || response || []
    
    // Get latest health metrics from most recent log
    if (recentLogs.value.length > 0) {
      const latestLog = recentLogs.value[0]
      healthMetrics.value = {
        cpu_usage: latestLog.cpu_usage || 0,
        memory_usage: latestLog.memory_usage || 0,
        latency: latestLog.heartbeat_latency || 0,
      }
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || error.response?.data?.message || error.message
    notify.error(errorMsg || 'Failed to load logs')
  }
}

onMounted(async () => {
  const screenId = route.params.id
  await screensStore.fetchScreen(screenId)
  await templatesStore.fetchTemplates()
  await loadCommands()
  await loadLogs()
  
  // Refresh every 30 seconds
  setInterval(async () => {
    await screensStore.fetchScreen(screenId)
    await loadCommands()
    await loadLogs()
  }, 30000)
})
</script>
