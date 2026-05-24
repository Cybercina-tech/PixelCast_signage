<template>
  <div
    class="blog-page min-h-screen min-h-[100dvh] bg-gradient-to-br from-slate-800 via-slate-700 to-slate-800 text-white"
    :class="{ 'theme-light': !themeStore.isDarkMode }"
  >
    <header class="blog-header sticky top-0 z-40 backdrop-blur-md">
      <div
        class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3"
      >
        <div>
          <p class="blog-kicker text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <p class="blog-title text-xl sm:text-2xl font-bold">Blog</p>
        </div>
        <div class="flex flex-wrap gap-2">
          <router-link
            to="/docs"
            class="blog-nav-btn blog-nav-btn-primary px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Documentation
          </router-link>
          <router-link
            to="/"
            class="blog-nav-btn px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Home
          </router-link>
        </div>
      </div>
    </header>

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 pb-20">
      <section class="blog-hero mb-8 sm:mb-10">
        <img
          src="/blog/turn-any-tv-browser-signage.png"
          alt="Turn Any TV with a Browser into Digital Signage. No Media Players Required."
          class="blog-hero-image"
          loading="eager"
          fetchpriority="high"
        />
        <div class="blog-hero-overlay">
          <p class="blog-hero-kicker">PixelCast Blog</p>
          <h1 class="blog-hero-title">
            Turn Any TV with a Browser into Digital Signage.
            <br />
            No Media Players Required.
          </h1>
        </div>
      </section>

      <p class="blog-section-kicker text-xs font-semibold uppercase tracking-wider mb-2">Insights</p>
      <p class="blog-lead text-sm sm:text-base max-w-2xl mb-8">
        Product updates, digital signage best practices, and how to run your screen network with confidence.
      </p>
      <div class="blog-guides-panel mb-8 rounded-xl border p-4 sm:p-5">
        <p class="blog-guides-kicker text-xs uppercase tracking-wider font-semibold mb-2">Start with intent guides</p>
        <div class="flex flex-wrap gap-x-5 gap-y-2 text-sm">
          <router-link to="/solutions/browser-based-digital-signage-software" class="blog-guide-link">
            Browser-based digital signage software
          </router-link>
          <router-link to="/guides/turn-smart-tv-into-digital-signboard" class="blog-guide-link">
            Turn a smart TV into a digital signboard
          </router-link>
          <router-link to="/solutions/free-digital-signage-menu-boards" class="blog-guide-link">
            Free digital signage for menu boards
          </router-link>
          <router-link to="/solutions/cloud-digital-signage-tv-browser" class="blog-guide-link">
            Cloud signage for TV browser
          </router-link>
        </div>
      </div>

      <div v-if="loading" class="blog-loading text-center py-16">Loading articles…</div>
      <div v-else-if="error" class="blog-error rounded-xl border px-4 py-3 text-sm">
        {{ error }}
      </div>
      <div v-else-if="!posts.length" class="blog-empty text-center py-16 rounded-2xl border">
        <p class="blog-empty-title font-medium">No articles yet</p>
        <p class="blog-empty-copy text-sm mt-2">Check back soon for guides and updates.</p>
      </div>
      <div v-else class="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        <article
          v-for="post in posts"
          :key="post.id"
          class="blog-card group rounded-2xl border transition-colors overflow-hidden flex flex-col"
        >
          <router-link :to="{ name: 'blog-post', params: { slug: post.slug } }" class="flex flex-col flex-1 min-h-0">
            <div
              v-if="post.featured_image_url"
              class="blog-card-media aspect-[21/9] w-full overflow-hidden"
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
                class="blog-card-date text-[11px] uppercase tracking-wider mb-2"
                :datetime="post.published_at"
              >
                {{ formatDate(post.published_at) }}
              </time>
              <h2 class="blog-card-title text-lg font-semibold transition-colors leading-snug">
                {{ post.title }}
              </h2>
              <p v-if="post.excerpt" class="blog-card-excerpt mt-2 text-sm line-clamp-3 flex-1">{{ post.excerpt }}</p>
              <p v-if="post.author_name" class="blog-card-author mt-4 text-xs">By {{ post.author_name }}</p>
              <span class="blog-card-cta mt-4 inline-flex items-center text-sm font-medium">
                Read article →
              </span>
            </div>
          </router-link>
        </article>
      </div>

      <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-10 flex-wrap">
        <button
          type="button"
          class="blog-page-btn px-4 py-2 rounded-lg text-sm border disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="page <= 1"
          @click="goPage(page - 1)"
        >
          Previous
        </button>
        <span class="blog-page-indicator px-3 py-2 text-sm"> Page {{ page }} of {{ totalPages }} </span>
        <button
          type="button"
          class="blog-page-btn px-4 py-2 rounded-lg text-sm border disabled:opacity-40 disabled:cursor-not-allowed"
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
import { useThemeStore } from '@/stores/theme'

const posts = ref([])
const loading = ref(true)
const error = ref('')
const page = ref(1)
const totalPages = ref(1)
const themeStore = useThemeStore()

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

.blog-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(30, 41, 59, 0.9);
}

.blog-kicker {
  color: #67e8f9;
}

.blog-title {
  color: #ffffff;
}

.blog-nav-btn {
  border: 1px solid rgba(255, 255, 255, 0.24);
  background: rgba(15, 23, 42, 0.42);
  color: rgba(226, 232, 240, 0.92);
}

.blog-nav-btn:hover {
  border-color: rgba(255, 255, 255, 0.42);
  color: #ffffff;
}

.blog-nav-btn-primary:hover {
  border-color: rgba(103, 232, 249, 0.44);
  color: #dbeafe;
}

.blog-nav-btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(103, 232, 249, 0.26);
}

.blog-page.theme-light {
  background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #e2e8f0 100%);
  color: #0f172a;
}

.blog-page.theme-light .blog-header {
  border-bottom-color: rgba(148, 163, 184, 0.36);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(248, 250, 252, 0.86) 100%);
}

.blog-page.theme-light .blog-kicker {
  color: #0284c7;
}

.blog-page.theme-light .blog-title {
  color: #0f172a;
}

.blog-page.theme-light .blog-nav-btn {
  border-color: rgba(148, 163, 184, 0.52);
  background: rgba(255, 255, 255, 0.92);
  color: #334155;
  box-shadow: 0 3px 12px rgba(15, 23, 42, 0.08);
}

.blog-page.theme-light .blog-nav-btn:hover {
  border-color: rgba(51, 65, 85, 0.45);
  background: #ffffff;
  color: #0f172a;
}

.blog-page.theme-light .blog-nav-btn-primary:hover {
  border-color: rgba(37, 99, 235, 0.38);
  color: #1d4ed8;
}

.blog-page.theme-light .blog-nav-btn:focus-visible {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.22);
}

/* Explicit light text: some browsers/themes ignore Tailwind `text-white/75` on this route; avoid body --text-body winning. */
.blog-page .blog-lead {
  color: rgba(255, 255, 255, 0.82);
  -webkit-text-fill-color: rgba(255, 255, 255, 0.82);
}

.blog-hero {
  position: relative;
  overflow: hidden;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.35);
}

.blog-hero-image {
  display: block;
  width: 100%;
  aspect-ratio: 16 / 8;
  object-fit: cover;
}

.blog-hero-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding: 1rem;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.05) 18%, rgba(15, 23, 42, 0.72) 100%);
}

.blog-hero-kicker {
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(186, 230, 253, 0.92);
  font-weight: 700;
  margin-bottom: 0.35rem;
}

.blog-hero-title {
  color: #ffffff;
  font-size: clamp(1rem, 2vw, 1.7rem);
  line-height: 1.25;
  font-weight: 800;
  max-width: 45rem;
  text-wrap: balance;
}

.blog-page.theme-light .blog-lead {
  color: rgba(51, 65, 85, 0.9);
  -webkit-text-fill-color: rgba(51, 65, 85, 0.9);
}

.blog-page.theme-light .blog-hero {
  border-color: rgba(148, 163, 184, 0.35);
  box-shadow: 0 16px 36px rgba(30, 41, 59, 0.12);
}

.blog-page.theme-light .blog-hero-overlay {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 20%, rgba(15, 23, 42, 0.6) 100%);
}

/* Section + guides (dark base) */
.blog-section-kicker {
  color: rgba(216, 180, 254, 0.9);
}

.blog-guides-panel {
  border-color: rgba(34, 211, 238, 0.2);
  background: rgba(8, 47, 73, 0.35);
}

.blog-guides-kicker {
  color: rgba(103, 232, 249, 0.95);
}

.blog-guide-link {
  color: rgba(165, 243, 252, 0.95);
  text-decoration: none;
  transition: color 0.15s ease;
}

.blog-guide-link:hover {
  color: #ecfeff;
}

.blog-loading {
  color: rgba(226, 232, 240, 0.65);
}

.blog-error {
  border-color: rgba(251, 191, 36, 0.35);
  background: rgba(69, 26, 3, 0.45);
  color: #fde68a;
}

.blog-empty {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
}

.blog-empty-title {
  color: rgba(248, 250, 252, 0.88);
}

.blog-empty-copy {
  color: rgba(226, 232, 240, 0.55);
}

.blog-card {
  border-color: rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
}

.blog-card:hover {
  border-color: rgba(34, 211, 238, 0.28);
  background: rgba(255, 255, 255, 0.09);
}

.blog-card-media {
  background: rgba(15, 23, 42, 0.5);
}

.blog-card-date {
  color: rgba(103, 232, 249, 0.8);
}

.blog-card-title {
  color: #ffffff;
}

.blog-card:hover .blog-card-title {
  color: #ecfeff;
}

.blog-card-excerpt {
  color: rgba(248, 250, 252, 0.72);
}

.blog-card-author {
  color: rgba(226, 232, 240, 0.45);
}

.blog-card-cta {
  color: rgba(103, 232, 249, 0.95);
}

.blog-card:hover .blog-card-cta {
  color: #a5f3fc;
}

.blog-page-btn {
  border-color: rgba(255, 255, 255, 0.22);
  background: rgba(15, 23, 42, 0.35);
  color: rgba(226, 232, 240, 0.92);
  transition: border-color 0.15s ease, color 0.15s ease;
}

.blog-page-btn:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.4);
  color: #ffffff;
}

.blog-page-indicator {
  color: rgba(226, 232, 240, 0.62);
}

/* Light theme: guides, cards, pagination */
.blog-page.theme-light .blog-section-kicker {
  color: rgba(124, 58, 237, 0.88);
}

.blog-page.theme-light .blog-guides-panel {
  border-color: rgba(37, 99, 235, 0.22);
  background: linear-gradient(135deg, rgba(219, 234, 254, 0.9) 0%, rgba(224, 231, 255, 0.75) 100%);
  box-shadow: 0 8px 24px rgba(37, 99, 235, 0.08);
}

.blog-page.theme-light .blog-guides-kicker {
  color: #1e40af;
}

.blog-page.theme-light .blog-guide-link {
  color: #2563eb;
}

.blog-page.theme-light .blog-guide-link:hover {
  color: #1d4ed8;
}

.blog-page.theme-light .blog-loading {
  color: #64748b;
}

.blog-page.theme-light .blog-error {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(254, 243, 199, 0.9);
  color: #92400e;
}

.blog-page.theme-light .blog-empty {
  border-color: rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.85);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.blog-page.theme-light .blog-empty-title {
  color: #0f172a;
}

.blog-page.theme-light .blog-empty-copy {
  color: #64748b;
}

.blog-page.theme-light .blog-card {
  border-color: rgba(148, 163, 184, 0.38);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

.blog-page.theme-light .blog-card:hover {
  border-color: rgba(37, 99, 235, 0.35);
  background: #ffffff;
  box-shadow: 0 14px 32px rgba(37, 99, 235, 0.12);
}

.blog-page.theme-light .blog-card-media {
  background: rgba(226, 232, 240, 0.85);
}

.blog-page.theme-light .blog-card-date {
  color: #0284c7;
}

.blog-page.theme-light .blog-card-title {
  color: #0f172a;
}

.blog-page.theme-light .blog-card:hover .blog-card-title {
  color: #1d4ed8;
}

.blog-page.theme-light .blog-card-excerpt {
  color: #475569;
}

.blog-page.theme-light .blog-card-author {
  color: #94a3b8;
}

.blog-page.theme-light .blog-card-cta {
  color: #2563eb;
}

.blog-page.theme-light .blog-card:hover .blog-card-cta {
  color: #1d4ed8;
}

.blog-page.theme-light .blog-page-btn {
  border-color: rgba(148, 163, 184, 0.5);
  background: rgba(255, 255, 255, 0.92);
  color: #334155;
  box-shadow: 0 3px 12px rgba(15, 23, 42, 0.06);
}

.blog-page.theme-light .blog-page-btn:hover:not(:disabled) {
  border-color: rgba(51, 65, 85, 0.4);
  color: #0f172a;
}

.blog-page.theme-light .blog-page-indicator {
  color: #64748b;
}

@media (max-width: 640px) {
  .blog-hero-image {
    aspect-ratio: 4 / 3;
  }

  .blog-hero-overlay {
    padding: 0.85rem;
  }

  .blog-hero-title {
    font-size: clamp(0.92rem, 4.2vw, 1.2rem);
    line-height: 1.3;
  }
}
</style>
