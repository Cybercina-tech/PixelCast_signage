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
            to="/blog"
            class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-cyan-400/40 hover:text-cyan-100 transition-colors"
          >
            All articles
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

    <div v-if="loading" class="max-w-3xl mx-auto px-4 py-16 text-center text-white/60">Loading…</div>
    <div v-else-if="error" class="max-w-3xl mx-auto px-4 py-16">
      <p class="rounded-xl border border-red-400/30 bg-red-950/40 px-4 py-3 text-red-100">{{ error }}</p>
      <router-link to="/blog" class="inline-block mt-6 text-cyan-300 hover:text-cyan-200 text-sm">← Back to blog</router-link>
    </div>
    <article v-else-if="post" class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 pb-20">
      <header class="mb-8">
        <p class="text-xs font-semibold uppercase tracking-wider text-purple-300/90 mb-2">Article</p>
        <h1 class="text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight leading-tight">
          {{ post.title }}
        </h1>
        <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-white/55">
          <time v-if="post.published_at" :datetime="post.published_at">{{ formatDate(post.published_at) }}</time>
          <span v-if="post.author_name">· {{ post.author_name }}</span>
          <span v-if="post.reading_time_minutes">· ~{{ post.reading_time_minutes }} min read</span>
        </div>
        <div
          v-if="post.featured_image_url"
          class="mt-8 rounded-2xl overflow-hidden border border-white/10 bg-slate-900/40"
        >
          <img :src="post.featured_image_url" :alt="post.title" class="w-full h-auto object-cover" />
        </div>
      </header>

      <div
        class="blog-article-body prose-blog max-w-none space-y-6"
        v-html="htmlBody"
      />

      <section
        class="mt-12 rounded-2xl border border-cyan-400/20 bg-cyan-950/20 px-5 py-5 sm:px-6 sm:py-6"
        aria-label="Next steps"
      >
        <h2 class="text-base font-semibold text-cyan-100 mb-2">Next steps with PixelCast</h2>
        <p class="text-white/75 text-sm sm:text-base leading-relaxed mb-4">
          Manage templates, schedules, and players from one place — built for serious display networks.
        </p>
        <div class="flex flex-wrap gap-3">
          <router-link
            to="/install"
            class="inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 hover:opacity-95"
          >
            Start installation
          </router-link>
          <router-link
            to="/signup"
            class="inline-flex items-center justify-center rounded-lg border border-white/20 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white hover:border-white/40"
          >
            Create account
          </router-link>
        </div>
      </section>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useHead, useSeoMeta } from '@unhead/vue'
import { publicAPI } from '@/services/api'
import { renderMarkdown } from '@/utils/renderMarkdown'
import { SITE_NAME, getSiteOrigin } from '@/seo/siteConfig'
import { buildBlogPostingGraph } from '@/seo/jsonLd'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const error = ref('')

const htmlBody = computed(() => renderMarkdown(post.value?.body || ''))

function formatDate(iso) {
  try {
    return new Intl.DateTimeFormat(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(new Date(iso))
  } catch {
    return ''
  }
}

const pageTitle = computed(() => {
  if (!post.value) return `Blog — ${SITE_NAME}`
  const t = post.value.meta_title || post.value.title
  return `${t} — ${SITE_NAME}`
})

const pageDescription = computed(() => {
  if (!post.value) return ''
  return post.value.meta_description || post.value.excerpt || ''
})

useSeoMeta({
  title: pageTitle,
  description: pageDescription,
  ogTitle: pageTitle,
  ogDescription: pageDescription,
})

const blogPostingJsonLd = computed(() => {
  const p = post.value
  const origin = getSiteOrigin()
  if (!p || !origin) return null
  const path = `/blog/${p.slug}`
  return buildBlogPostingGraph(origin, {
    path,
    headline: p.meta_title || p.title,
    description: pageDescription.value,
    datePublished: p.published_at ? p.published_at.slice(0, 10) : undefined,
    dateModified: p.updated_at ? p.updated_at.slice(0, 10) : undefined,
  })
})

useHead({
  script: computed(() => {
    const graph = blogPostingJsonLd.value
    if (!graph) return []
    return [
      {
        key: 'blog-post-jsonld',
        type: 'application/ld+json',
        children: JSON.stringify(graph),
      },
    ]
  }),
})

async function load() {
  const slug = route.params.slug
  if (!slug) {
    error.value = 'Missing article.'
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  post.value = null
  try {
    const { data } = await publicAPI.blog.posts.retrieve(slug)
    post.value = data
  } catch (e) {
    if (e?.response?.status === 404) {
      error.value = 'This article could not be found.'
    } else {
      error.value = e?.response?.data?.detail || e?.message || 'Could not load article.'
    }
  } finally {
    loading.value = false
  }
}

watch(
  () => route.params.slug,
  () => load(),
  { immediate: true }
)
</script>

<style scoped>
.blog-page {
  color: rgb(248 250 252);
  isolation: isolate;
}

.prose-blog :deep(h2) {
  font-size: 1.25rem;
  font-weight: 600;
  color: rgb(255 255 255);
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.prose-blog :deep(h3) {
  font-size: 1.1rem;
  font-weight: 600;
  color: rgb(248 250 252);
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}
.prose-blog :deep(p),
.prose-blog :deep(li) {
  color: rgba(248, 250, 252, 0.88);
  line-height: 1.65;
}
.prose-blog :deep(ul) {
  list-style: disc;
  padding-left: 1.25rem;
}
.prose-blog :deep(ol) {
  list-style: decimal;
  padding-left: 1.25rem;
}
.prose-blog :deep(a) {
  color: rgb(103 232 249);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.prose-blog :deep(strong) {
  color: rgb(255 255 255);
}
.prose-blog :deep(pre) {
  background: rgba(15 23 42 / 0.85);
  border: 1px solid rgba(255 255 255 / 0.1);
  border-radius: 0.75rem;
  padding: 1rem;
  overflow-x: auto;
  font-size: 0.875rem;
}
.prose-blog :deep(code) {
  font-size: 0.9em;
}
</style>
