<template>
  <div
    class="blog-page min-h-screen min-h-[100dvh] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 text-white"
    :class="{ 'theme-light': !themeStore.isDarkMode }"
  >
    <header class="blog-post-header sticky top-0 z-40 border-b border-white/15 bg-slate-800/90 backdrop-blur-md">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div>
          <p class="blog-post-kicker text-cyan-300 text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <p class="blog-post-title text-xl sm:text-2xl font-bold text-white">Blog</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link
            to="/blog"
            class="blog-post-nav-btn px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-cyan-400/40 hover:text-cyan-100 transition-colors"
          >
            All articles
          </router-link>
          <router-link
            to="/"
            class="blog-post-nav-btn px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-white/40 transition-colors"
          >
            Home
          </router-link>
        </div>
      </div>
    </header>

    <div v-if="loading" class="blog-post-loading max-w-3xl mx-auto px-4 py-16 text-center text-white/60">Loading…</div>
    <div v-else-if="error" class="max-w-3xl mx-auto px-4 py-16">
      <p class="blog-post-error rounded-xl border border-red-400/30 bg-red-950/40 px-4 py-3 text-red-100">{{ error }}</p>
      <router-link to="/blog" class="blog-post-back inline-block mt-6 text-cyan-300 hover:text-cyan-200 text-sm">← Back to blog</router-link>
    </div>
    <article v-else-if="post" class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 pb-20">
      <header class="mb-8">
        <p class="blog-article-kicker text-xs font-semibold uppercase tracking-wider text-purple-300/90 mb-2">Article</p>
        <h1 class="blog-article-title text-2xl sm:text-3xl lg:text-4xl font-bold text-white tracking-tight leading-tight">
          {{ post.title }}
        </h1>
        <div class="blog-article-meta mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-white/55">
          <time v-if="post.published_at" :datetime="post.published_at">{{ formatDate(post.published_at) }}</time>
          <span v-if="post.author_name">· {{ post.author_name }}</span>
          <span v-if="post.reading_time_minutes">· ~{{ post.reading_time_minutes }} min read</span>
        </div>
        <div
          v-if="post.featured_image_url"
          class="blog-article-image mt-8 rounded-2xl overflow-hidden border border-white/10 bg-slate-900/40"
        >
          <img :src="post.featured_image_url" :alt="post.title" class="w-full h-auto object-cover" />
        </div>
      </header>

      <div
        class="blog-article-body prose-blog max-w-none space-y-6"
        v-html="htmlBody"
      />

      <section
        class="blog-next-panel mt-12 rounded-2xl border border-cyan-400/20 bg-cyan-950/20 px-5 py-5 sm:px-6 sm:py-6"
        aria-label="Next steps"
      >
        <h2 class="blog-next-title text-base font-semibold text-cyan-100 mb-2">Next steps with PixelCast</h2>
        <p
          v-if="isInstalled"
          class="blog-next-installed text-emerald-200/90 text-sm font-medium mb-2"
        >
          PixelCast is already installed on this server.
        </p>
        <p class="blog-next-copy text-white/75 text-sm sm:text-base leading-relaxed mb-4">
          Manage templates, schedules, and players from one place — built for serious display networks.
        </p>
        <div class="flex flex-wrap gap-3">
          <router-link
            to="/signup"
            class="blog-next-cta-primary inline-flex items-center justify-center rounded-lg bg-gradient-to-r from-cyan-500 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 hover:opacity-95"
          >
            Create account
          </router-link>
          <router-link
            to="/login"
            class="blog-next-cta-secondary inline-flex items-center justify-center rounded-lg border border-white/20 bg-white/5 px-4 py-2.5 text-sm font-semibold text-white hover:border-white/40"
          >
            Log in
          </router-link>
          <router-link
            to="/pricing"
            class="blog-next-cta-accent inline-flex items-center justify-center rounded-lg border border-cyan-400/40 bg-cyan-500/10 px-4 py-2.5 text-sm font-semibold text-cyan-100 hover:bg-cyan-500/20"
          >
            Pricing
          </router-link>
        </div>
        <div class="mt-4 flex flex-wrap gap-3 text-xs sm:text-sm">
          <router-link class="blog-next-link text-cyan-300 hover:text-cyan-200" to="/solutions/browser-based-digital-signage-software">
            Browser-based digital signage software
          </router-link>
          <router-link class="blog-next-link text-cyan-300 hover:text-cyan-200" to="/solutions/free-digital-signage-menu-boards">
            Free digital signage for menu boards
          </router-link>
          <router-link class="blog-next-link text-cyan-300 hover:text-cyan-200" to="/solutions/cloud-digital-signage-tv-browser">
            Cloud digital signage for TV browser
          </router-link>
        </div>
      </section>
    </article>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useHead, useSeoMeta } from '@unhead/vue'
import { publicAPI, setupAPI } from '@/services/api'
import { useThemeStore } from '@/stores/theme'
import { renderMarkdown } from '@/utils/renderMarkdown'
import { SITE_NAME, getSiteOrigin } from '@/seo/siteConfig'
import { buildBlogPostingGraph, buildBreadcrumbGraph } from '@/seo/jsonLd'

const route = useRoute()
const post = ref(null)
const loading = ref(true)
const error = ref('')
/** When true, this instance has completed install (installed.lock / env). */
const isInstalled = ref(true)
const themeStore = useThemeStore()

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

const canonicalUrl = computed(() => {
  const p = post.value
  const origin = getSiteOrigin()
  if (!p || !origin) return ''
  return `${origin}/blog/${p.slug}`
})

const articleImage = computed(() => post.value?.featured_image_url || undefined)
const twitterCardType = computed(() => (articleImage.value ? 'summary_large_image' : 'summary'))

useSeoMeta({
  title: pageTitle,
  description: pageDescription,
  ogTitle: pageTitle,
  ogDescription: pageDescription,
  ogType: 'article',
  ogUrl: canonicalUrl,
  ogImage: articleImage,
  twitterCard: twitterCardType,
  twitterTitle: pageTitle,
  twitterDescription: pageDescription,
  twitterImage: articleImage,
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
    image: p.featured_image_url || undefined,
  })
})

useHead({
  link: computed(() => {
    const href = canonicalUrl.value
    if (!href) return []
    return [{ rel: 'canonical', href }]
  }),
  script: computed(() => {
    const graph = blogPostingJsonLd.value
    const origin = getSiteOrigin()
    const p = post.value
    if (!graph || !origin || !p) return []
    const breadcrumbs = buildBreadcrumbGraph(origin, `/blog/${p.slug}`, [
      { name: 'Home', path: '/' },
      { name: 'Blog', path: '/blog' },
      { name: p.title, path: `/blog/${p.slug}` },
    ])
    return [
      {
        key: 'blog-post-jsonld',
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@graph': [...graph['@graph'], breadcrumbs],
        }),
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

onMounted(() => {
  setupAPI
    .status()
    .then((response) => {
      isInstalled.value = Boolean(response?.data?.installed)
    })
    .catch(() => {
      isInstalled.value = true
    })
})
</script>

<style scoped>
.blog-page {
  color: rgb(248 250 252);
  isolation: isolate;
}

.blog-post-header {
  border-bottom-color: rgba(255, 255, 255, 0.15);
  background: rgba(30, 41, 59, 0.9);
}

.blog-post-kicker {
  color: #67e8f9;
}

.blog-post-title,
.blog-article-title {
  color: #ffffff;
}

.blog-post-nav-btn {
  border-color: rgba(255, 255, 255, 0.22);
  background: rgba(15, 23, 42, 0.35);
  color: rgba(226, 232, 240, 0.92);
}

.blog-post-nav-btn:hover {
  border-color: rgba(148, 163, 184, 0.45);
  color: #ffffff;
}

.blog-post-loading {
  color: rgba(226, 232, 240, 0.78);
}

.blog-post-error {
  border-color: rgba(248, 113, 113, 0.4);
  background: rgba(127, 29, 29, 0.5);
  color: #fecaca;
}

.blog-post-back {
  color: #67e8f9;
}

.blog-post-back:hover {
  color: #a5f3fc;
}

.blog-article-kicker {
  color: rgba(216, 180, 254, 0.95);
}

.blog-article-meta {
  color: rgba(203, 213, 225, 0.76);
}

.blog-article-image {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(15, 23, 42, 0.4);
}

.blog-next-panel {
  border-color: rgba(34, 211, 238, 0.24);
  background: rgba(8, 47, 73, 0.34);
}

.blog-next-title {
  color: rgba(224, 242, 254, 0.95);
}

.blog-next-installed {
  color: rgba(167, 243, 208, 0.95);
}

.blog-next-copy {
  color: rgba(226, 232, 240, 0.9);
}

.blog-next-link {
  color: rgba(103, 232, 249, 0.95);
}

.blog-next-link:hover {
  color: #a5f3fc;
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

.blog-page.theme-light {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #e2e8f0 100%);
  color: #0f172a;
}

.blog-page.theme-light .blog-post-header {
  border-bottom-color: rgba(148, 163, 184, 0.34);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(248, 250, 252, 0.86) 100%);
}

.blog-page.theme-light .blog-post-kicker {
  color: #0284c7;
}

.blog-page.theme-light .blog-post-title,
.blog-page.theme-light .blog-article-title {
  color: #0f172a;
}

.blog-page.theme-light .blog-post-nav-btn {
  border-color: rgba(148, 163, 184, 0.5);
  background: rgba(255, 255, 255, 0.92);
  color: #334155;
  box-shadow: 0 3px 12px rgba(15, 23, 42, 0.08);
}

.blog-page.theme-light .blog-post-nav-btn:hover {
  border-color: rgba(51, 65, 85, 0.4);
  color: #0f172a;
}

.blog-page.theme-light .blog-post-loading {
  color: rgba(51, 65, 85, 0.8);
}

.blog-page.theme-light .blog-post-error {
  border-color: rgba(248, 113, 113, 0.34);
  background: rgba(254, 226, 226, 0.85);
  color: #b91c1c;
}

.blog-page.theme-light .blog-post-back {
  color: #2563eb;
}

.blog-page.theme-light .blog-post-back:hover {
  color: #1d4ed8;
}

.blog-page.theme-light .blog-article-kicker {
  color: rgba(124, 58, 237, 0.9);
}

.blog-page.theme-light .blog-article-meta {
  color: #64748b;
}

.blog-page.theme-light .blog-article-image {
  border-color: rgba(148, 163, 184, 0.3);
  background: rgba(226, 232, 240, 0.8);
}

.blog-page.theme-light .blog-next-panel {
  border-color: rgba(37, 99, 235, 0.22);
  background: linear-gradient(180deg, rgba(219, 234, 254, 0.85) 0%, rgba(224, 231, 255, 0.75) 100%);
  box-shadow: 0 12px 26px rgba(37, 99, 235, 0.1);
}

.blog-page.theme-light .blog-next-title {
  color: #1e3a8a;
}

.blog-page.theme-light .blog-next-installed {
  color: #047857;
}

.blog-page.theme-light .blog-next-copy {
  color: #334155;
}

.blog-page.theme-light .blog-next-cta-secondary {
  border-color: rgba(148, 163, 184, 0.45);
  background: rgba(255, 255, 255, 0.9);
  color: #0f172a;
}

.blog-page.theme-light .blog-next-cta-secondary:hover {
  border-color: rgba(51, 65, 85, 0.38);
}

.blog-page.theme-light .blog-next-cta-accent {
  border-color: rgba(37, 99, 235, 0.36);
  background: rgba(37, 99, 235, 0.08);
  color: #1e40af;
}

.blog-page.theme-light .blog-next-cta-accent:hover {
  background: rgba(37, 99, 235, 0.14);
}

.blog-page.theme-light .blog-next-link {
  color: #2563eb;
}

.blog-page.theme-light .blog-next-link:hover {
  color: #1d4ed8;
}

.blog-page.theme-light .prose-blog :deep(h2),
.blog-page.theme-light .prose-blog :deep(h3),
.blog-page.theme-light .prose-blog :deep(strong) {
  color: #0f172a;
}

.blog-page.theme-light .prose-blog :deep(p),
.blog-page.theme-light .prose-blog :deep(li) {
  color: #334155;
}

.blog-page.theme-light .prose-blog :deep(a) {
  color: #2563eb;
}

.blog-page.theme-light .prose-blog :deep(a:hover) {
  color: #1d4ed8;
}

.blog-page.theme-light .prose-blog :deep(pre) {
  background: rgba(241, 245, 249, 0.9);
  border-color: rgba(148, 163, 184, 0.34);
  color: #0f172a;
}
</style>
