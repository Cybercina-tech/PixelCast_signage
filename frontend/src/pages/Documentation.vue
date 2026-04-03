<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
    <header class="sticky top-0 z-40 border-b border-white/10 bg-slate-950/85 backdrop-blur-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div class="min-w-0">
          <p class="text-cyan-300 text-xs font-semibold tracking-[0.16em] uppercase">PixelCast</p>
          <h1 class="text-xl sm:text-2xl font-bold text-white truncate">Documentation</h1>
        </div>
        <div class="flex flex-wrap items-center gap-2 shrink-0">
          <router-link
            to="/docs/changelog"
            class="btn-outline px-3 py-2 rounded-lg text-xs sm:text-sm border border-white/20 hover:border-cyan-400/40 hover:text-cyan-100 transition-colors"
          >
            Changelog
          </router-link>
          <router-link to="/" class="btn-outline px-4 py-2 rounded-lg text-sm border border-white/20 hover:border-white/40 transition-colors">
            Back to Landing
          </router-link>
        </div>
      </div>
    </header>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-10">
      <div class="flex flex-col lg:flex-row gap-8 lg:gap-10 lg:items-start">
        <!-- TOC: mobile collapsible -->
        <aside class="w-full lg:w-64 shrink-0 lg:max-w-[17rem]">
          <details class="lg:hidden rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm mb-2 group">
            <summary
              class="cursor-pointer list-none flex items-center justify-between gap-2 px-4 py-3 text-sm font-semibold text-cyan-200 [&::-webkit-details-marker]:hidden"
            >
              <span>On this page</span>
              <span class="text-white/40 group-open:rotate-180 transition-transform text-xs">▼</span>
            </summary>
            <nav class="px-4 pb-4 max-h-[min(60vh,24rem)] overflow-y-auto border-t border-white/5 pt-3" aria-label="Table of contents">
              <ol class="space-y-1.5 text-sm">
                <li v-for="item in toc" :key="`m-${item.id}`">
                  <a
                    :href="`#${item.id}`"
                    class="block py-1 rounded-md px-1 -mx-1 transition-colors"
                    :class="
                      activeId === item.id
                        ? 'text-cyan-300 bg-cyan-500/10 font-medium'
                        : 'text-white/70 hover:text-white'
                    "
                    @click="activeId = item.id"
                  >
                    {{ item.label }}
                  </a>
                </li>
              </ol>
            </nav>
          </details>

          <!-- TOC: desktop sticky -->
          <nav
            class="hidden lg:block rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm p-4 sticky top-[5.25rem] max-h-[calc(100vh-6rem)] overflow-y-auto"
            aria-label="Table of contents"
          >
            <p class="text-xs font-semibold uppercase tracking-wider text-cyan-300/90 mb-3">Contents</p>
            <ol class="space-y-1 text-sm border-l border-white/10 pl-3">
              <li v-for="item in toc" :key="item.id">
                <a
                  :href="`#${item.id}`"
                  class="block py-1.5 pl-2 -ml-px border-l-2 -ml-[13px] transition-colors rounded-r-md"
                  :class="
                    activeId === item.id
                      ? 'border-cyan-400 text-cyan-100 bg-cyan-500/10 font-medium'
                      : 'border-transparent text-white/65 hover:text-white hover:border-white/20'
                  "
                >
                  {{ item.label }}
                </a>
              </li>
            </ol>
          </nav>
        </aside>

        <main class="min-w-0 flex-1 space-y-6 sm:space-y-8 pb-16">
          <!-- Hero -->
          <section
            class="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900/90 to-slate-950/90 p-5 sm:p-8 shadow-xl shadow-black/20"
          >
            <p
              class="inline-flex items-center rounded-full border border-purple-400/30 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-200 mb-4"
            >
              Product guide
            </p>
            <h2 class="text-2xl sm:text-3xl font-bold text-white tracking-tight mb-3">PicxelCast — complete documentation</h2>
            <p class="text-white/75 text-sm sm:text-base leading-relaxed max-w-3xl mb-6">
              Installation, production configuration, SaaS isolation, day-to-day operations, and support policy — written
              for technical and non-technical teams with clear, step-by-step instructions.
            </p>
            <div class="space-y-3">
              <div class="rounded-xl border border-amber-400/25 bg-amber-950/30 px-4 py-3 text-sm text-amber-50/95">
                <strong class="text-amber-200">Important:</strong>
                Keep this documentation updated for every release. Reviewers expect structure, clarity, and changelog quality.
              </div>
              <div class="rounded-xl border border-emerald-400/25 bg-emerald-950/25 px-4 py-3 text-sm text-emerald-50/95">
                <strong class="text-emerald-200">Dockerized by default:</strong>
                Use <code class="docs-code">docker-compose.yml</code> (dev) and
                <code class="docs-code">docker-compose.prod.yml</code> (production) for the fastest path.
              </div>
              <div class="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80">
                <strong class="text-white">Quick navigation:</strong>
                Return to the
                <router-link to="/" class="text-cyan-300 hover:text-cyan-200 underline underline-offset-2">landing page</router-link>
                anytime.
              </div>
            </div>
          </section>

          <DocsSection id="introduction" title="1) Introduction">
            <p class="docs-p">
              PicxelCast is a digital signage platform for managing screens, scheduling content, and operating multi-tenant SaaS
              instances from a centralized admin panel.
            </p>
            <div class="docs-card">
              <h3 class="docs-h3">Documentation in the Vue app</h3>
              <pre class="docs-pre text-xs sm:text-sm"><code>frontend/src/pages/Documentation.vue   → /docs
frontend/src/pages/DocsChangelog.vue    → /docs/changelog
(styled with Tailwind to match the marketing site)</code></pre>
            </div>
            <div class="flex flex-wrap items-center gap-2 sm:gap-3 text-xs sm:text-sm" aria-label="Platform architecture">
              <span class="docs-pill">Frontend (Nginx + Vue)</span>
              <span class="text-white/40">→</span>
              <span class="docs-pill">Backend (Django)</span>
              <span class="text-white/40">→</span>
              <span class="docs-pill">PostgreSQL</span>
              <span class="text-white/40">+</span>
              <span class="docs-pill">Redis</span>
            </div>
          </DocsSection>

          <DocsSection id="requirements" title="2) Requirements">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="docs-card">
                <h3 class="docs-h3">Server requirements</h3>
                <ul class="docs-ul">
                  <li>Python 3.10+</li>
                  <li>Django 4.x or 5.x</li>
                  <li>Node.js 18+ (frontend build)</li>
                  <li>PostgreSQL 13+ or MySQL 8+</li>
                  <li>Redis 6+</li>
                  <li>Docker Engine 24+ and Compose</li>
                  <li>Nginx or Apache</li>
                  <li>SSL for production SaaS</li>
                </ul>
              </div>
              <div class="docs-card">
                <h3 class="docs-h3">Runtime notes</h3>
                <ul class="docs-ul">
                  <li>Dependencies in <code class="docs-code">requirements.txt</code></li>
                  <li>Build UI with <code class="docs-code">npm run build</code></li>
                  <li>Use UTC on the server for scheduling</li>
                  <li>Non-root database user recommended</li>
                </ul>
              </div>
            </div>
            <div class="docs-card">
              <h3 class="docs-h3">Browser support</h3>
              <p class="docs-p">Chrome 90+, Firefox 88+, Safari 14+, Edge 90+</p>
            </div>
          </DocsSection>

          <DocsSection id="installation-guide" title="3) Installation Guide">
            <p class="docs-p">Recommended: Docker. Manual steps below for advanced setups.</p>
            <div class="docs-card space-y-4">
              <h3 class="docs-h3">Quick Docker install</h3>
              <div class="space-y-3">
                <div v-for="(step, i) in dockerSteps" :key="i" class="flex gap-3">
                  <span
                    class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-cyan-500/25 to-violet-500/25 text-xs font-bold text-cyan-100 border border-cyan-400/35"
                  >
                    {{ i + 1 }}
                  </span>
                  <div class="flex-1 rounded-xl border border-white/10 bg-slate-900/50 px-3 py-2.5 text-sm text-white/85">
                    <strong class="text-white">{{ step.label }}</strong>
                    <template v-if="step.codes">
                      <span class="text-white/80"> Set </span>
                      <template v-for="(c, j) in step.codes" :key="j">
                        <code class="docs-code">{{ c }}</code><span v-if="j < step.codes.length - 1" class="text-white/70"> and </span>
                      </template>
                    </template>
                    <template v-else-if="step.code">
                      <code class="docs-code ml-1">{{ step.code }}</code>
                    </template>
                    <span v-if="step.text" class="text-white/80">{{ step.text }}</span>
                  </div>
                </div>
              </div>
              <pre class="docs-pre text-xs sm:text-sm"><code>docker compose build --no-cache
docker compose up -d
docker compose ps</code></pre>
            </div>
            <div class="rounded-xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white/80">
              <strong class="text-white">Docker stack:</strong>
              <code class="docs-code">frontend</code>, <code class="docs-code">backend</code>, <code class="docs-code">db</code>,
              <code class="docs-code">redis</code>.
            </div>
            <p class="docs-p">Manual installation (non-Docker):</p>
            <ol class="list-decimal pl-5 sm:pl-6 space-y-4 text-white/85 text-sm sm:text-base marker:text-cyan-400/80">
              <li class="pl-1">
                <span class="font-semibold text-white">Upload</span> — cPanel, FTP, or SSH.
              </li>
              <li class="pl-1">
                <span class="font-semibold text-white">Database</span> — create DB and user with least privilege.
              </li>
              <li class="pl-1">
                <span class="font-semibold text-white">Configure</span>
                <code class="docs-code">.env</code>.
              </li>
              <li class="pl-1">
                <span class="font-semibold text-white">Migrate</span>
                <pre class="docs-pre mt-2 text-xs"><code>python manage.py migrate</code></pre>
              </li>
              <li class="pl-1">
                <span class="font-semibold text-white">Build frontend</span>
                <pre class="docs-pre mt-2 text-xs"><code>npm install
npm run build</code></pre>
              </li>
              <li class="pl-1"><span class="font-semibold text-white">Web server</span> — Nginx/Apache with HTTPS.</li>
              <li class="pl-1">
                <span class="font-semibold text-white">Wizard</span>
                <pre class="docs-pre mt-2 text-xs"><code>https://yourdomain.com/install</code></pre>
              </li>
              <li class="pl-1"><span class="font-semibold text-white">Admin user</span> — create and sign in.</li>
            </ol>
            <div class="rounded-xl border border-emerald-400/20 bg-emerald-950/20 px-4 py-3 text-sm text-emerald-50/95">
              <strong class="text-emerald-200">Done:</strong> verify dashboard, <code class="docs-code">/api/health</code>, and
              scheduler.
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div v-for="svc in serviceCards" :key="svc.name" class="docs-mini-card">
                <strong class="text-white block text-sm">{{ svc.name }}</strong>
                <span class="text-xs text-white/55 mt-1 block">{{ svc.desc }}</span>
              </div>
            </div>
          </DocsSection>

          <DocsSection id="env-configuration" title="4) Configuration (.env)">
            <p class="docs-p">Review every variable before production.</p>
            <pre class="docs-pre text-[11px] sm:text-xs overflow-x-auto"><code># Database
DB_HOST=db
DB_NAME=pixelcast_signage_db
DB_USER=pixelcast_signage_user
DB_PASSWORD=...
DB_PORT=5432

# Security
SECRET_KEY=replace-me
DEBUG=False
ALLOWED_HOSTS=domain.com,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://domain.com

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USER=example@domain.com
MAIL_PASS=app-password
MAIL_USE_TLS=True</code></pre>
            <div class="flex flex-wrap gap-2">
              <span v-for="p in envPills" :key="p" class="docs-tag">{{ p }}</span>
            </div>
            <div class="rounded-xl border border-amber-400/20 bg-amber-950/20 px-4 py-3 text-sm text-amber-50/90">
              <strong class="text-amber-200">Security:</strong> never commit <code class="docs-code">.env</code>. Rotate credentials if
              exposed.
            </div>
          </DocsSection>

          <DocsSection id="saas-setup" title="5) Multi-Tenant / SaaS Setup">
            <ul class="docs-ul">
              <li>Create tenants from the SaaS admin panel.</li>
              <li>Assign plans, seats, and billing.</li>
              <li>Keep data isolated per tenant.</li>
              <li>Optional custom domains per tenant.</li>
              <li>Validate permissions with test users.</li>
            </ul>
            <div class="docs-card">
              <h3 class="docs-h3">Architecture summary</h3>
              <pre class="docs-pre text-xs sm:text-sm"><code>Client → Nginx → Django → Tenant resolver
                      → PostgreSQL
                      → Redis
                      → Workers / scheduler</code></pre>
            </div>
            <figure class="docs-figure">
              <img :src="screenshot('saas-admin.png')" alt="SaaS admin" class="docs-img" @error="hideBroken" />
              <figcaption class="docs-caption">SaaS administration (tenants &amp; plans)</figcaption>
            </figure>
          </DocsSection>

          <DocsSection id="admin-dashboard" title="6) Admin Dashboard">
            <p class="docs-p">Tenant overview, screens, failed jobs, and alerts.</p>
            <figure class="docs-figure">
              <img :src="screenshot('dashboard.png')" alt="Dashboard" class="docs-img" @error="hideBroken" />
              <figcaption class="docs-caption">Main dashboard</figcaption>
            </figure>
          </DocsSection>

          <DocsSection id="screen-management" title="7) Screen Management">
            <ul class="docs-ul">
              <li>Pair devices with codes or tokens.</li>
              <li>Group by location, tenant, tags.</li>
              <li>Fallback content for reliability.</li>
              <li>Live online/offline status.</li>
            </ul>
            <figure class="docs-figure">
              <img :src="screenshot('screen-manager.png')" alt="Screens" class="docs-img" @error="hideBroken" />
              <figcaption class="docs-caption">Screen manager</figcaption>
            </figure>
          </DocsSection>

          <DocsSection id="content-scheduler" title="8) Content Scheduler">
            <ul class="docs-ul">
              <li>One-off and recurring schedules.</li>
              <li>Timezone-aware campaign windows.</li>
              <li>Priority when slots overlap.</li>
              <li>Preview before go-live.</li>
            </ul>
            <figure class="docs-figure">
              <img :src="screenshot('scheduler.png')" alt="Scheduler" class="docs-img" @error="hideBroken" />
              <figcaption class="docs-caption">Scheduler timeline</figcaption>
            </figure>
          </DocsSection>

          <DocsSection id="template-builder" title="9) Template Builder">
            <ul class="docs-ul">
              <li>Canvas profiles (1080p, 4K, portrait).</li>
              <li>Widgets: text, image, video, clock, web, ticker.</li>
              <li>Reusable blocks.</li>
              <li>Publish to one or many screens.</li>
            </ul>
            <figure class="docs-figure">
              <img :src="screenshot('template-builder.png')" alt="Template builder" class="docs-img" @error="hideBroken" />
              <figcaption class="docs-caption">Template editor</figcaption>
            </figure>
          </DocsSection>

          <DocsSection id="error-handling" title="10) Error Handling & Logs">
            <h3 class="docs-h3 text-base">Where to check</h3>
            <ul class="docs-ul">
              <li>Application: Django and workers</li>
              <li>Web: Nginx/Apache logs</li>
              <li>Scheduler: job queue state</li>
            </ul>
            <h3 class="docs-h3 text-base mt-4">Common fixes</h3>
            <ul class="docs-ul">
              <li><strong class="text-white">500:</strong> env values and <code class="docs-code">DEBUG=False</code></li>
              <li><strong class="text-white">Assets:</strong> rebuild frontend and collect static</li>
              <li><strong class="text-white">WebSocket:</strong> Redis and firewall</li>
            </ul>
          </DocsSection>

          <DocsSection id="api-reference" title="11) API Reference">
            <p class="docs-p">Core routes:</p>
            <pre class="docs-pre text-xs sm:text-sm"><code>/api/setup/status
/api/setup/db-check
/api/health
/api/docs
/api/schema
/api/logs/...
/api/core/...
/iot/...</code></pre>
            <div class="flex flex-wrap gap-2">
              <span class="docs-tag">/install + /api/setup/*</span>
              <span class="docs-tag">/api/health</span>
              <span class="docs-tag">/api/docs</span>
              <span class="docs-tag">/iot/*</span>
            </div>
            <p class="docs-p text-sm">Authentication is enforced on the server; UI route guards are not a security boundary.</p>
          </DocsSection>

          <DocsSection id="update-guide" title="12) Update Guide">
            <ol class="list-decimal pl-5 space-y-2 text-white/85 text-sm sm:text-base">
              <li>Full backup: database, media, env.</li>
              <li>Deploy new application files or images.</li>
              <li>Install dependencies / rebuild images.</li>
              <li>Run migrations.</li>
              <li>Rebuild frontend if needed.</li>
              <li>Restart services.</li>
              <li>
                Read the
                <router-link to="/docs/changelog" class="text-cyan-300 hover:underline">changelog</router-link>
                for breaking changes.
              </li>
            </ol>
          </DocsSection>

          <DocsSection id="faq" title="13) FAQ">
            <div class="space-y-4">
              <div class="docs-card">
                <h3 class="docs-h3">One license, multiple production domains?</h3>
                <p class="docs-p">No — follow marketplace licensing per domain/project.</p>
              </div>
              <div class="docs-card">
                <h3 class="docs-h3">Multi-tenant SaaS?</h3>
                <p class="docs-p">Yes — isolation, plans, and tenant administration are supported.</p>
              </div>
              <div class="docs-card">
                <h3 class="docs-h3">Custom features?</h3>
                <p class="docs-p">Possible as separate paid work; not included in standard item support.</p>
              </div>
            </div>
          </DocsSection>

          <DocsSection id="support" title="14) Support">
            <ul class="docs-ul">
              <li>
                Email:
                <a href="mailto:support@picxelcast.app" class="text-cyan-300 hover:text-cyan-200 underline">support@picxelcast.app</a>
              </li>
              <li>
                Envato:
                <a href="https://codecanyon.net/" target="_blank" rel="noreferrer" class="text-cyan-300 hover:underline">Item comments</a>
              </li>
              <li>Response: typically 24–48 business hours</li>
              <li>Included: bugs, setup help, documented behavior</li>
              <li>Not included: custom dev, third-party integrations, managed hosting</li>
            </ul>
          </DocsSection>

          <DocsSection id="changelog" title="15) Changelog">
            <div class="docs-card">
              <h3 class="docs-h3">Version 1.0.0 — March 2026</h3>
              <ul class="docs-ul">
                <li>Initial release</li>
                <li>Multi-screen management</li>
                <li>Scheduler</li>
                <li>SaaS / multi-tenant</li>
                <li>Template builder</li>
                <li>Error handling</li>
              </ul>
              <p class="docs-p mt-3">
                <router-link to="/docs/changelog" class="text-cyan-300 font-medium hover:underline">Full changelog →</router-link>
              </p>
            </div>
          </DocsSection>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import DocsSection from '@/components/docs/DocsSection.vue'

const toc = [
  { id: 'introduction', label: 'Introduction' },
  { id: 'requirements', label: 'Requirements' },
  { id: 'installation-guide', label: 'Installation Guide' },
  { id: 'env-configuration', label: 'Configuration (.env)' },
  { id: 'saas-setup', label: 'Multi-Tenant / SaaS' },
  { id: 'admin-dashboard', label: 'Admin Dashboard' },
  { id: 'screen-management', label: 'Screen Management' },
  { id: 'content-scheduler', label: 'Content Scheduler' },
  { id: 'template-builder', label: 'Template Builder' },
  { id: 'error-handling', label: 'Errors & Logs' },
  { id: 'api-reference', label: 'API Reference' },
  { id: 'update-guide', label: 'Update Guide' },
  { id: 'faq', label: 'FAQ' },
  { id: 'support', label: 'Support' },
  { id: 'changelog', label: 'Changelog' },
]

const dockerSteps = [
  { label: 'Prepare env:', code: 'cp .env.example .env' },
  { label: 'Configure secrets:', codes: ['DB_PASSWORD', 'SECRET_KEY'] },
  { label: 'Run installer:', code: 'chmod +x install.sh && ./install.sh' },
  { label: 'Finish setup:', text: ' Open your site and complete the /install wizard.' },
]

const serviceCards = [
  { name: 'frontend', desc: 'UI on port 80 (default)' },
  { name: 'backend', desc: 'API & migrations' },
  { name: 'db', desc: 'PostgreSQL volume' },
  { name: 'redis', desc: 'Queue & realtime' },
]

const envPills = [
  'DB_HOST=db',
  'USE_REDIS_CACHE=True',
  'DEBUG=False in production',
  'FRONTEND_HOST_PORT for local dev',
]

const activeId = ref(toc[0]?.id || '')
let observer = null

function screenshot(name) {
  return `/documentation/assets/screenshots/${name}`
}

function hideBroken(e) {
  const fig = e.target?.closest?.('figure')
  if (fig) fig.classList.add('hidden')
}

onMounted(() => {
  document.title = 'PicxelCast Documentation'
  const opts = { rootMargin: '-12% 0px -55% 0px', threshold: [0, 0.1, 0.25] }
  observer = new IntersectionObserver((entries) => {
    const visible = entries
      .filter((e) => e.isIntersecting)
      .sort((a, b) => (b.intersectionRatio || 0) - (a.intersectionRatio || 0))
    if (visible[0]?.target?.id) activeId.value = visible[0].target.id
  }, opts)
  toc.forEach(({ id }) => {
    const el = document.getElementById(id)
    if (el) observer.observe(el)
  })
})

onUnmounted(() => {
  observer?.disconnect()
})
</script>

<style scoped>
.docs-p {
  @apply text-white/80 text-sm sm:text-base leading-relaxed;
}
.docs-h3 {
  @apply text-sm sm:text-base font-semibold text-white mb-2;
}
.docs-ul {
  @apply list-disc pl-5 space-y-2 text-white/80 text-sm sm:text-base;
}
.docs-card {
  @apply rounded-xl border border-white/10 bg-slate-900/40 p-4 sm:p-5;
}
.docs-mini-card {
  @apply rounded-xl border border-white/10 bg-slate-900/30 px-3 py-3;
}
.docs-pre {
  @apply rounded-xl bg-slate-950 border border-white/10 p-4 overflow-x-auto font-mono text-emerald-200/90;
}
.docs-code {
  @apply rounded bg-slate-900/90 border border-white/10 px-1.5 py-0.5 text-cyan-200/95 text-xs sm:text-sm font-mono align-middle;
}
.docs-pill {
  @apply inline-flex items-center rounded-full border border-white/15 bg-slate-900/50 px-3 py-1.5 text-white/85;
}
.docs-tag {
  @apply inline-flex rounded-full border border-violet-400/25 bg-violet-950/30 px-2.5 py-1 text-xs text-violet-100/90;
}
.docs-figure {
  @apply mt-2 rounded-xl overflow-hidden border border-white/10 bg-black/20;
}
.docs-img {
  @apply w-full h-auto max-w-full block;
}
.docs-caption {
  @apply px-3 py-2 text-xs text-white/50 border-t border-white/5;
}
</style>
