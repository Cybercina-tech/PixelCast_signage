<template>
  <div
    class="blog-page min-h-screen min-h-[100dvh] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 text-white"
  >
    <header class="sticky top-0 z-40 border-b border-white/15 bg-slate-800/90 backdrop-blur-md">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div>
          <p class="text-cyan-300 text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <p class="text-xl sm:text-2xl font-bold text-white">Blog</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link
            to="/docs"
            class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-cyan-400/40 hover:text-cyan-100 transition-colors"
          >
            Documentation
          </router-link>
          <router-link
            to="/"
            class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-white/40 transition-colors"
          >
            Home
          </router-link>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 pb-20">
      <p class="text-xs font-semibold uppercase tracking-wider text-purple-300/90 mb-2">Insights</p>
      <h1 class="text-2xl sm:text-3xl font-bold text-white tracking-tight mb-2">Articles &amp; guides</h1>
      <p class="blog-lead text-sm sm:text-base max-w-2xl mb-8">
        Product updates, digital signage best practices, and how to run your screen network with confidence.
      </p>

      <div v-if="loading" class="text-center py-16 text-white/60">Loading articles…</div>
      <div v-else-if="error" class="rounded-xl border border-amber-500/30 bg-amber-950/30 px-4 py-3 text-amber-100 text-sm">
        {{ error }}
      </div>
      <div v-else-if="!posts.length" class="text-center py-16 rounded-2xl border border-white/10 bg-white/5">
        <p class="text-white/80 font-medium">No articles yet</p>
        <p class="text-white/55 text-sm mt-2">Check back soon for guides and updates.</p>
      </div>
      <div v-else class="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        <article
          v-for="post in posts"
          :key="post.id"
          class="group rounded-2xl border border-white/10 bg-white/[0.06] hover:border-cyan-400/25 hover:bg-white/[0.09] transition-colors overflow-hidden flex flex-col"
        >
          <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }" class="flex flex-col flex-1 min-h-0">
            <div
              v-if="post.featured_image_url"
              class="aspect-[21/9] w-full overflow-hidden bg-slate-900/50"
            >
              <img
                :src="post.featured_image_url"
                :alt="post.title"
                class="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-300"
                loading="lazy"
              />
            </div>
            <div class="p-5 sm:p-6 flex flex-col flex-1">
              <time
                v-if="post.published_at"
                class="text-[11px] uppercase tracking-wider text-cyan-300/80 mb-2"
                :datetime="post.published_at"
              >
                {{ formatDate(post.published_at) }}
              </time>
              <h2 class="text-lg font-semibold text-white group-hover:text-cyan-100 transition-colors leading-snug">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="mt-2 text-sm text-white/70 line-clamp-3 flex-1">{{ post.excerpt }}</p>
              <p v-if="post.author_name" class="mt-4 text-xs text-white/45">By {{ post.author_name }}</p>
              <span class="mt-4 inline-flex items-center text-sm font-medium text-cyan-300 group-hover:text-cyan-200">
                Read article →
              </span>
            </div>
          </router-link>
        </article>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-10 flex-wrap">
        <button
          type="button"
          class="px-4 py-2 rounded-lg text-sm border border-white/20 disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/40"
          :disabled="page <= 1"
          @click="goPage(page - 1)"
        >
          Previous
        </button>
        <span class="px-3 py-2 text-sm text-white/60"> Page {{ page }} of {{ totalPages }} </span>
        <button
          type="button"
          class="px-4 py-2 rounded-lg text-sm border border-white/20 disabled:opacity-40 disabled:cursor-not-allowed hover:border-white/40"
          :disabled="page >= totalPages"
          @click="goPage(page + 1)"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { publicAPI } from '@/services/api'

const posts = ref([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(1)

function formatDate(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(iso))
  } catch {
    return ''
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await publicAPI.blog.posts.list({ page: page.value, page_size: 10 })
    const list = data.results ?? data
    posts.value = Array.isArray(list) ? list : []
    const count = data.count ?? posts.value.length
    const pageSize = 10
    totalPages.value = Math.max(1, Math.ceil(count / pageSize))
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || 'Could not load articles.'
    posts.value = []
  } finally {
    loading.value = false
  }
}

function goPage(p) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  load()
})
</script>

<style scoped>
.blog-page {
  color: rgb(248 250 252);
  isolation: isolate;
}

/* Explicit light text: some browsers/themes ignore Tailwind `text-white/75` on this route; avoid body --text-body winning. */
.blog-page .blog-lead {
  color: rgba(255, 255, 255, 0.82);
  -webkit-text-fill-color: rgba(255, 255, 255, 0.82);
}
</style>
