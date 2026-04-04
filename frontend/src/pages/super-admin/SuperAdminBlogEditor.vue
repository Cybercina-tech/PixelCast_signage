<template>
  <div class="space-y-6">
    <div class="flex flex-wrap gap-2">
      <router-link to="/super-admin/blog" class="btn-outline px-4 py-2 rounded-lg text-sm">← All posts</router-link>
    </div>

    <div v-if="loading" class="text-center py-12 text-muted">Loading…</div>
    <form v-else class="grid grid-cols-1 xl:grid-cols-2 gap-6" @submit.prevent="save">
      <Card class="space-y-4">
        <h2 class="text-lg font-semibold text-primary">Content</h2>
        <div>
          <label class="label-base block text-sm mb-1">Title *</label>
          <input v-model="form.title" type="text" required class="input-base w-full px-3 py-2 rounded-lg" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Slug</label>
          <input v-model="form.slug" type="text" class="input-base w-full px-3 py-2 rounded-lg font-mono text-sm" placeholder="auto from title if empty" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Excerpt</label>
          <textarea v-model="form.excerpt" rows="3" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Body (Markdown)</label>
          <textarea v-model="form.body" rows="18" class="input-base w-full px-3 py-2 rounded-lg text-sm font-mono" />
        </div>
        <div>
          <label class="label-base block text-sm mb-1">Featured image URL</label>
          <input v-model="form.featured_image_url" type="url" class="input-base w-full px-3 py-2 rounded-lg text-sm" placeholder="https://…" />
        </div>
      </Card>

      <div class="space-y-6">
        <Card class="space-y-4">
          <h2 class="text-lg font-semibold text-primary">Publishing</h2>
          <div>
            <label class="label-base block text-sm mb-1">Status</label>
            <select v-model="form.status" class="select-base w-full px-3 py-2 rounded-lg">
              <option value="draft">Draft</option>
              <option value="published">Published</option>
            </select>
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Published at (ISO datetime, optional)</label>
            <input v-model="form.published_at" type="datetime-local" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
            <p class="text-xs text-muted mt-1">Leave empty to set automatically when publishing.</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <button type="submit" class="btn-primary px-4 py-2 rounded-lg text-sm" :disabled="saving">
              {{ isNew ? 'Create' : 'Save' }}
            </button>
            <button
              v-if="!isNew"
              type="button"
              class="btn-outline px-4 py-2 rounded-lg text-sm"
              :disabled="saving || publishing"
              @click="publishNow"
            >
              Publish now
            </button>
          </div>
        </Card>

        <Card class="space-y-4">
          <h2 class="text-lg font-semibold text-primary">SEO</h2>
          <div>
            <label class="label-base block text-sm mb-1">Meta title</label>
            <input v-model="form.meta_title" type="text" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
          </div>
          <div>
            <label class="label-base block text-sm mb-1">Meta description</label>
            <textarea v-model="form.meta_description" rows="3" class="input-base w-full px-3 py-2 rounded-lg text-sm" />
          </div>
        </Card>

        <Card>
          <h2 class="text-lg font-semibold text-primary mb-3">Preview</h2>
          <div class="blog-preview prose max-w-none rounded-lg border border-border-color p-4 text-sm bg-card/40" v-html="previewHtml" />
        </Card>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Card from '@/components/common/Card.vue'
import { platformAPI } from '@/services/api'
import { getNotification } from '@/composables/useNotification'
import { renderMarkdown } from '@/utils/renderMarkdown'

const route = useRoute()
const router = useRouter()
const notify = getNotification()

const loading = ref(true)
const saving = ref(false)
const publishing = ref(false)

const isNew = computed(() => route.name === 'super-admin-blog-new')

const form = ref({
  title: '',
  slug: '',
  excerpt: '',
  body: '',
  status: 'draft',
  published_at: '',
  featured_image_url: '',
  meta_title: '',
  meta_description: '',
})

const previewHtml = computed(() => renderMarkdown(form.value.body))

function toDatetimeLocal(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch {
    return ''
  }
}

function fromDatetimeLocal(local) {
  if (!local || !local.trim()) return null
  const d = new Date(local)
  return Number.isNaN(d.getTime()) ? null : d.toISOString()
}

function payload() {
  const p = {
    title: form.value.title.trim(),
    slug: form.value.slug.trim(),
    excerpt: form.value.excerpt,
    body: form.value.body,
    status: form.value.status,
    featured_image_url: form.value.featured_image_url.trim(),
    meta_title: form.value.meta_title.trim(),
    meta_description: form.value.meta_description.trim(),
  }
  const pub = fromDatetimeLocal(form.value.published_at)
  if (pub) p.published_at = pub
  else if (form.value.status === 'published' && !isNew.value) {
    /* keep existing server value on partial — omit for simplicity */
  }
  return p
}

function resetForm() {
  form.value = {
    title: '',
    slug: '',
    excerpt: '',
    body: '',
    status: 'draft',
    published_at: '',
    featured_image_url: '',
    meta_title: '',
    meta_description: '',
  }
}

async function load() {
  if (route.name === 'super-admin-blog-new') {
    resetForm()
    loading.value = false
    return
  }
  const id = route.params.id
  loading.value = true
  try {
    const { data } = await platformAPI.blog.posts.retrieve(id)
    form.value = {
      title: data.title || '',
      slug: data.slug || '',
      excerpt: data.excerpt || '',
      body: data.body || '',
      status: data.status || 'draft',
      published_at: toDatetimeLocal(data.published_at),
      featured_image_url: data.featured_image_url || '',
      meta_title: data.meta_title || '',
      meta_description: data.meta_description || '',
    }
  } catch (e) {
    notify?.error?.(e?.response?.data?.detail || 'Failed to load post')
    router.push({ name: 'super-admin-blog' })
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    const body = payload()
    if (isNew.value) {
      const { data } = await platformAPI.blog.posts.create(body)
      notify?.success?.('Article created')
      await router.replace({ name: 'super-admin-blog-edit', params: { id: data.id } })
    } else {
      await platformAPI.blog.posts.patch(route.params.id, body)
      notify?.success?.('Saved')
      await load()
    }
  } catch (e) {
    const msg = e?.response?.data
    const detail =
      typeof msg === 'object' && msg !== null
        ? Object.entries(msg)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`)
            .join(' ')
        : e?.message
    notify?.error?.(detail || 'Save failed')
  } finally {
    saving.value = false
  }
}

async function publishNow() {
  publishing.value = true
  try {
    await platformAPI.blog.posts.publish(route.params.id)
    notify?.success?.('Published')
    await load()
  } catch (e) {
    notify?.error?.(e?.response?.data?.detail || 'Publish failed')
  } finally {
    publishing.value = false
  }
}

watch(() => route.fullPath, load, { immediate: true })
</script>

<style scoped>
.blog-preview :deep(h1),
.blog-preview :deep(h2) {
  font-weight: 600;
  margin-top: 0.75rem;
  margin-bottom: 0.5rem;
}
.blog-preview :deep(p) {
  margin-bottom: 0.5rem;
}
.blog-preview :deep(ul) {
  list-style: disc;
  padding-left: 1.25rem;
}
</style>
