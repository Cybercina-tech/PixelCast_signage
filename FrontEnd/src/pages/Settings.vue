<template>
  <AppLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-gray-900">Settings</h1>
      
      <!-- WebSocket & API Settings -->
      <Card title="WebSocket & API Settings">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">API Base URL</label>
            <input
              v-model="settings.apiBaseUrl"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="http://localhost:8000/api"
            />
            <p class="mt-1 text-xs text-gray-500">Base URL for API requests</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">WebSocket URL</label>
            <input
              v-model="settings.wsUrl"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="ws://localhost:8000/ws/dashboard/"
            />
            <p class="mt-1 text-xs text-gray-500">WebSocket connection URL</p>
          </div>
          <button
            @click="saveApiSettings"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save API Settings
          </button>
        </div>
      </Card>
      
      <!-- Storage Settings -->
      <Card title="Storage Configuration">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Storage Backend</label>
            <select v-model="settings.storageBackend" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
              <option value="local">Local File System</option>
              <option value="s3">Amazon S3</option>
            </select>
          </div>
          <div v-if="settings.storageBackend === 's3'">
            <div class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">S3 Bucket Name</label>
                <input
                  v-model="settings.s3Bucket"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="your-bucket-name"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">S3 Region</label>
                <input
                  v-model="settings.s3Region"
                  type="text"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  placeholder="us-east-1"
                />
              </div>
            </div>
          </div>
          <button
            @click="saveStorageSettings"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save Storage Settings
          </button>
        </div>
      </Card>
      
      <!-- Security Settings -->
      <Card title="Security Settings">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Rate Limit (requests/minute)</label>
            <input
              v-model.number="settings.rateLimit"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="60"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Token Expiration (minutes)</label>
            <input
              v-model.number="settings.tokenExpiration"
              type="number"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="60"
            />
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="settings.enableNonce" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Enable Nonce Protection</span>
            </label>
          </div>
          <button
            @click="saveSecuritySettings"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save Security Settings
          </button>
        </div>
      </Card>
      
      <!-- Notifications -->
      <Card title="Notifications">
        <div class="space-y-4">
          <div>
            <label class="flex items-center">
              <input v-model="settings.emailNotifications" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">Email Notifications</span>
            </label>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="settings.smsNotifications" type="checkbox" class="mr-2" />
              <span class="text-sm text-gray-700">SMS Notifications</span>
            </label>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Notification Email</label>
            <input
              v-model="settings.notificationEmail"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg"
              placeholder="admin@example.com"
            />
          </div>
          <button
            @click="saveNotificationSettings"
            class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Save Notification Settings
          </button>
        </div>
      </Card>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'

const toastStore = useToastStore()

const settings = ref({
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  wsUrl: import.meta.env.VITE_WS_HOST || 'ws://localhost:8000/ws/dashboard/',
  storageBackend: 'local',
  s3Bucket: '',
  s3Region: 'us-east-1',
  rateLimit: 60,
  tokenExpiration: 60,
  enableNonce: true,
  emailNotifications: false,
  smsNotifications: false,
  notificationEmail: '',
})

const saveApiSettings = () => {
  // In a real app, this would save to backend or localStorage
  localStorage.setItem('apiBaseUrl', settings.value.apiBaseUrl)
  localStorage.setItem('wsUrl', settings.value.wsUrl)
  toastStore.success('API settings saved')
}

const saveStorageSettings = () => {
  localStorage.setItem('storageBackend', settings.value.storageBackend)
  if (settings.value.storageBackend === 's3') {
    localStorage.setItem('s3Bucket', settings.value.s3Bucket)
    localStorage.setItem('s3Region', settings.value.s3Region)
  }
  toastStore.success('Storage settings saved')
}

const saveSecuritySettings = () => {
  localStorage.setItem('rateLimit', settings.value.rateLimit.toString())
  localStorage.setItem('tokenExpiration', settings.value.tokenExpiration.toString())
  localStorage.setItem('enableNonce', settings.value.enableNonce.toString())
  toastStore.success('Security settings saved')
}

const saveNotificationSettings = () => {
  localStorage.setItem('emailNotifications', settings.value.emailNotifications.toString())
  localStorage.setItem('smsNotifications', settings.value.smsNotifications.toString())
  localStorage.setItem('notificationEmail', settings.value.notificationEmail)
  toastStore.success('Notification settings saved')
}
</script>
