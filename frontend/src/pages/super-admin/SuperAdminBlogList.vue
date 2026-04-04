<template>
  <div class="space-y-6">
    <div class="flex flex-wrap justify-between items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold text-primary">Blog posts</h1>
        <p class="text-sm text-muted mt-1">Marketing articles on the public site (Markdown)</p>
      </div>
      <div class="flex gap-2 flex-wrap">
        <router-link to="/super-admin/blog/new" class="btn-primary px-4 py-2 rounded-lg text-sm"> New article </router-link>
        <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm" :disabled="loading" @click="load">
          Refresh
        </button>
      </div>
    </div>

    <Card>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label class="label-base block text-sm mb-1">Search</label>
          <input
            v-model="filters.search"
            type="text"
            class="input-base w-full px-3 py-2 rounded-lg"
            placeholder="Title, slug…"
            @keyup.enter="load"
          />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Status</label>
          <select v-model="filters.status" class="select-base w-full px-3 py-2 rounded-lg" @change="load">
            <option value="">All</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </div>
        <div class="flex items-end">
          <button type="button" class="btn-outline px-4 py-2 rounded-lg text-sm w-full sm:w-auto" @click="load">Apply</button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-8 text-muted">Loading…</div>
      <div v-else-if="error" class="text-center py-8 text-red-400">{{ error }}</div>
      <div v-else-if="!rows.length" class="text-center py-12 text-muted">No posts yet. Create one to appear on /blog.</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-border-color text-left text-muted">
              <th class="py-2 pr-4 font-medium">Title</th>
              <th class="py-2 pr-4 font-medium">Slug</th>
              <th class="py-2 pr-4 font-medium">Status</th>
              <th class="py-2 pr-4 font-medium">Published</th>
              <th class="py-2 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id" class="border-b border-border-color/60">
              <td class="py-3 pr-4 font-medium text-primary max-w-[min(24rem,50vw)] truncate">{{ row.title }}</td>
              <td class="py-3 pr-4 font-mono text-xs text-muted">{{ row.slug }}</td>
              <td class="py-3 pr-4">
                <span
                  class="text-[11px] px-2 py-1 rounded-full border capitalize"
                  :class="row.status === 'published' ? 'border-emerald-500/40 text-emerald-600 dark:text-emerald-400' : 'border-amber-500/40 text-amber-700 dark:text-amber-300'"
                >
                  {{ row.status }}
                </span>
              </td>
              <td class="py-3 pr-4 text-muted text-xs whitespace-nowrap">
                {{ row.published_at ? formatDate(row.published_at) : '—' }}
              </td>
              <td class="py-3 text-right whitespace-nowrap">
                <router-link
                  :to="{ name: 'super-admin-blog-edit', params: { id: row.id } }"
                  class="text-accent-color hover:underline text-xs mr-3"
                >
                  Edit
                </router-link>
                <a :href="`/blog/${row.slug}`" target="_blank" rel="noopener noreferrer" class="text-muted hover:text-primary text-xs mr-3">
                  View
                </a>
                <button type="button" class="text-red-500 hover:underline text-xs" @click="confirmDelete(row)">Delete</button>
              </td>
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

const loading = ref(true)
const error = ref('')
const rows = ref([])
const filters = ref({ search: '', status: '' })

function formatDate(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso))
  } catch {
    return iso
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = { page_size: 100 }
    if (filters.value.search.trim()) params.search = filters.value.search.trim()
    if (filters.value.status) params.status = filters.value.status
    const { data } = await platformAPI.blog.posts.list(params)
    const list = data.results ?? data
    rows.value = Array.isArray(list) ? list : []
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Failed to load posts.'
    rows.value = []
  } finally {
    loading.value = false
  }
}

function confirmDelete(row) {
  const notify = getNotification()
  if (!window.confirm(`Delete “${row.title}”? This cannot be undone.`)) return
  platformAPI.blog.posts
    .remove(row.id)
    .then(() => {
      notify?.success?.('Post deleted')
      load()
    })
    .catch((e) => {
      notify?.error?.(e?.response?.data?.detail || 'Delete failed')
    })
}

onMounted(load)
</script>
