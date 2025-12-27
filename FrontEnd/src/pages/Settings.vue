<template>
  <AppLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-primary">Settings</h1>
      
      <!-- Appearance Settings -->
      <Card title="Appearance">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium label-base mb-3">Theme</label>
            <div class="flex items-center gap-4">
              <ThemeToggle />
              <div>
                <p class="text-sm text-secondary">Current theme: <span class="font-semibold text-primary">{{ themeStore.theme === 'dark' ? 'Dark' : 'Light' }}</span></p>
                <p class="mt-1 text-xs text-muted">Toggle between light and dark mode</p>
              </div>
            </div>
          </div>
        </div>
      </Card>
      
      <!-- WebSocket & API Settings -->
      <Card title="WebSocket & API Settings">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">API Base URL</label>
            <input
              v-model="settings.apiBaseUrl"
              type="text"
              class="input-base w-full px-3 py-2 rounded-xl"
              placeholder="http://localhost:8000/api"
            />
            <p class="mt-1 text-xs text-muted">Base URL for API requests</p>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">WebSocket URL</label>
            <input
              v-model="settings.wsUrl"
              type="text"
              class="input-base w-full px-3 py-2 rounded-xl"
              placeholder="ws://localhost:8000/ws/dashboard/"
            />
            <p class="mt-1 text-xs text-muted">WebSocket connection URL</p>
          </div>
          <button
            @click="saveApiSettings"
            class="btn-primary px-4 py-2 rounded-xl"
          >
            Save API Settings
          </button>
        </div>
      </Card>
      
      <!-- Storage Settings -->
      <Card title="Storage Configuration">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Storage Backend</label>
            <select v-model="settings.storageBackend" class="select-base w-full px-3 py-2 rounded-xl">
              <option value="local">Local File System</option>
              <option value="s3">Amazon S3</option>
            </select>
          </div>
          <div v-if="settings.storageBackend === 's3'">
            <div class="space-y-3">
              <div>
                <label class="label-base block text-sm mb-1">S3 Bucket Name</label>
                <input
                  v-model="settings.s3Bucket"
                  type="text"
                  class="input-base w-full px-3 py-2 rounded-xl"
                  placeholder="your-bucket-name"
                />
              </div>
              <div>
                <label class="label-base block text-sm mb-1">S3 Region</label>
                <input
                  v-model="settings.s3Region"
                  type="text"
                  class="input-base w-full px-3 py-2 rounded-xl"
                  placeholder="us-east-1"
                />
              </div>
            </div>
          </div>
          <button
            @click="saveStorageSettings"
            class="btn-primary px-4 py-2 rounded-xl"
          >
            Save Storage Settings
          </button>
        </div>
      </Card>
      
      <!-- Security Settings -->
      <Card title="Security Settings">
        <div class="space-y-4">
          <div>
            <label class="label-base block text-sm mb-1">Rate Limit (requests/minute)</label>
            <input
              v-model.number="settings.rateLimit"
              type="number"
              class="input-base w-full px-3 py-2 rounded-xl"
              placeholder="60"
            />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Token Expiration (minutes)</label>
            <input
              v-model.number="settings.tokenExpiration"
              type="number"
              class="input-base w-full px-3 py-2 rounded-xl"
              placeholder="60"
            />
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="settings.enableNonce" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-secondary">Enable Nonce Protection</span>
            </label>
          </div>
          <button
            @click="saveSecuritySettings"
            class="btn-primary px-4 py-2 rounded-xl"
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
              <input v-model="settings.emailNotifications" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-secondary">Email Notifications</span>
            </label>
          </div>
          <div>
            <label class="flex items-center">
              <input v-model="settings.smsNotifications" type="checkbox" class="checkbox-base mr-2" />
              <span class="text-sm text-secondary">SMS Notifications</span>
            </label>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Notification Email</label>
            <input
              v-model="settings.notificationEmail"
              type="email"
              class="input-base w-full px-3 py-2 rounded-xl"
              placeholder="admin@example.com"
            />
          </div>
          <button
            @click="saveNotificationSettings"
            class="btn-primary px-4 py-2 rounded-xl"
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
import { useNotification } from '@/composables/useNotification'
import { useThemeStore } from '@/stores/theme'
import AppLayout from '@/components/layout/AppLayout.vue'
import Card from '@/components/common/Card.vue'
import ThemeToggle from '@/components/common/ThemeToggle.vue'

const notify = useNotification()
const themeStore = useThemeStore()

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
  notify.success('API settings saved')
}

const saveStorageSettings = () => {
  localStorage.setItem('storageBackend', settings.value.storageBackend)
  if (settings.value.storageBackend === 's3') {
    localStorage.setItem('s3Bucket', settings.value.s3Bucket)
    localStorage.setItem('s3Region', settings.value.s3Region)
  }
  notify.success('Storage settings saved')
}

const saveSecuritySettings = () => {
  localStorage.setItem('rateLimit', settings.value.rateLimit.toString())
  localStorage.setItem('tokenExpiration', settings.value.tokenExpiration.toString())
  localStorage.setItem('enableNonce', settings.value.enableNonce.toString())
  notify.success('Security settings saved')
}

const saveNotificationSettings = () => {
  localStorage.setItem('emailNotifications', settings.value.emailNotifications.toString())
  localStorage.setItem('smsNotifications', settings.value.smsNotifications.toString())
  localStorage.setItem('notificationEmail', settings.value.notificationEmail)
  notify.success('Notification settings saved')
}
</script>
