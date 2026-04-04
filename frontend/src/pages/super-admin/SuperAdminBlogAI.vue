<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Blog AI (OpenAI)</h1>
        <p class="text-sm text-muted mt-1">
          Encrypted API key, daily caps, custom prompts. Schedule with
          <code class="text-xs px-1 rounded bg-card border border-border-color">python manage.py blog_ai_daily</code>
          (cron).
        </p>
      </div>
      <router-link to="/super-admin/blog" class="btn-outline px-4 py-2 rounded-lg text-sm"> All posts </router-link>
    </div>

    <p v-if="loadError" class="text-red-400 text-sm">{{ loadError }}</p>

    <Card v-if="settings">
      <h2 class="text-lg font-semibold text-primary mb-4">Settings</h2>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.enabled" type="checkbox" class="rounded border-border-color" />
          <span class="text-sm font-medium text-primary">Enable AI generation</span>
        </label>
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="form.auto_publish" type="checkbox" class="rounded border-border-color" />
          <span class="text-sm font-medium text-primary">Auto-publish generated posts</span>
        </label>
        <div>
          <label class="label-base block text-sm mb-1">OpenAI API key</label>
          <input
            v-model="form.openai_api_key"
            type="password"
            autocomplete="new-password"
            class="input-base w-full px-3 py-2 rounded-lg text-sm font-mono"
            placeholder="Leave blank to keep existing"
          />
          <p v-if="settings.openai_api_key_masked" class="text-xs text-muted mt-1">
            Current: {{ settings.openai_api_key_masked }}
          </p>
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Model</label>
          <input v-model="form.model" type="text" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div class="lg:col-span-2">
          <label class="label-base block text-sm mb-1">API base URL</label>
          <input v-model="form.api_base_url" type="url" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Max posts per calendar day (UTC)</label>
          <input v-model.number="form.max_posts_per_day" type="number" min="1" max="50" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Posts per run (manual + daily job)</label>
          <input v-model.number="form.posts_per_run" type="number" min="1" max="20" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div class="lg:col-span-2">
          <label class="label-base block text-sm mb-1">System prompt</label>
          <textarea v-model="form.system_prompt" rows="4" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div class="lg:col-span-2">
          <label class="label-base block text-sm mb-1">Keyword / topic pool</label>
          <textarea
            v-model="form.keyword_pool"
            rows="5"
            class="input-base w-full px-3 py-2 rounded-lg text-sm"
            placeholder="One topic or keyword phrase per line (SEO)"
          />
        </div>
      </div>
      <div class="mt-4 flex flex-wrap gap-2">
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="saving" @click="saveSettings">
          Save settings
        </button>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="reload">Reload</button>
      </div>
    </Card>

    <Card>
      <h2 class="text-lg font-semibold text-primary mb-4">Generate now</h2>
      <p class="text-sm text-muted mb-3">
        Server applies
        <strong>min(your count, remaining daily quota, posts per run)</strong>
        .
      </p>
      <div class="flex flex-wrap items-end gap-3">
        <div>
          <label class="label-base block text-sm mb-1">Count</label>
          <input v-model.number="genCount" type="number" min="1" max="10" class="input-base w-24 px-3 py-2 rounded-lg text-sm" />
        </div>
        <button type="button" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="generating" @click="runGenerate">
          {{ generating ? 'Generating…' : 'Generate' }}
        </button>
      </div>
      <pre v-if="genResult" class="mt-4 text-xs p-3 rounded-lg bg-card border border-border-color overflow-x-auto text-muted">{{ genResult }}</pre>
    </Card>

    <Card>
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-semibold text-primary">Recent logs</h2>
        <button type="button" class="btn-outline px-3 py-1.5 rounded-lg text-xs" @click="loadLogs">Refresh</button>
      </div>
      <div v-if="!logs.length" class="text-sm text-muted py-4">No runs yet.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-border-color text-left text-muted">
              <th class="py-2 pr-3">When</th>
              <th class="py-2 pr-3">Trigger</th>
              <th class="py-2 pr-3">Status</th>
              <th class="py-2 pr-3">Created</th>
              <th class="py-2">Message</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in logs" :key="row.id" class="border-b border-border-color/60">
              <td class="py-2 pr-3 whitespace-nowrap text-xs">{{ formatDt(row.created_at) }}</td>
              <td class="py-2 pr-3 capitalize">{{ row.trigger }}</td>
              <td class="py-2 pr-3">{{ row.status }}</td>
              <td class="py-2 pr-3">{{ row.created_count }} / {{ row.requested_count }}</td>
              <td class="py-2 text-muted text-xs max-w-md truncate" :title="row.message">{{ row.message }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </Card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { getNotification } from '@/composables/useNotification'

const notify = getNotification()
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)
const loadError = ref('')
const settings = ref(null)
const logs = ref([])
const genCount = ref(1)
const genResult = ref('')

const form = ref({
  enabled: false,
  openai_api_key: '',
  model: '',
  api_base_url: '',
  system_prompt: '',
  keyword_pool: '',
  posts_per_run: 2,
  max_posts_per_day: 2,
  auto_publish: false,
})

function applySettings(s) {
  settings.value = s
  form.value = {
    enabled: !!s.enabled,
    openai_api_key: '',
    model: s.model || '',
    api_base_url: s.api_base_url || '',
    system_prompt: s.system_prompt || '',
    keyword_pool: s.keyword_pool || '',
    posts_per_run: s.posts_per_run ?? 2,
    max_posts_per_day: s.max_posts_per_day ?? 2,
    auto_publish: !!s.auto_publish,
  }
}

async function reload() {
  loading.value = true
  loadError.value = ''
  try {
    const { data } = await platformAPI.blog.ai.getSettings()
    applySettings(data)
  } catch (e) {
    loadError.value = e?.response?.data?.detail || e?.message || 'Failed to load settings'
  } finally {
    loading.value = false
  }
}

async function loadLogs() {
  try {
    const { data } = await platformAPI.blog.ai.logs({ limit: 40 })
    logs.value = Array.isArray(data) ? data : []
  } catch {
    logs.value = []
  }
}

function formatDt(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(iso))
  } catch {
    return iso
  }
}

async function saveSettings() {
  saving.value = true
  try {
    const payload = {
      enabled: form.value.enabled,
      model: form.value.model,
      api_base_url: form.value.api_base_url,
      system_prompt: form.value.system_prompt,
      keyword_pool: form.value.keyword_pool,
      posts_per_run: form.value.posts_per_run,
      max_posts_per_day: form.value.max_posts_per_day,
      auto_publish: form.value.auto_publish,
    }
    if (form.value.openai_api_key?.trim()) {
      payload.openai_api_key = form.value.openai_api_key.trim()
    }
    const { data } = await platformAPI.blog.ai.patchSettings(payload)
    applySettings(data)
    form.value.openai_api_key = ''
    notify?.success?.('Settings saved')
  } catch (e) {
    const d = e?.response?.data
    const msg =
      typeof d === 'object' && d !== null
        ? Object.entries(d)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' ')
        : e?.message
    notify?.error?.(msg || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function runGenerate() {
  generating.value = true
  genResult.value = ''
  try {
    const { data } = await platformAPI.blog.ai.generate({ count: genCount.value })
    genResult.value = JSON.stringify(data, null, 2)
    notify?.success?.(`Done: ${data.log?.status} — created ${data.log?.created_count ?? 0}`)
    await loadLogs()
  } catch (e) {
    notify?.error?.(e?.response?.data?.detail || e?.message || 'Generation failed')
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  await reload()
  await loadLogs()
})
</script>
