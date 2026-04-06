# ScreenGram — Digital Signage Platform

ScreenGram is the source tree for **PixelCast**, a self-hosted or SaaS digital signage system for managing screens, templates, schedules, and media on distributed displays. It pairs a Django REST API and real-time WebSockets (Django Channels) with a Vue 3 SPA and an in-browser web player for any modern screen.

---

## Architecture

```
                     ┌──────────────┐
   Browser / TV  ──▶ │  Nginx (SPA) │──▶ /api/, /iot/, /ws/ ──▶ Django (Gunicorn + Uvicorn)
                     └──────────────┘                            │         │         │
                                                           PostgreSQL   Redis    Celery*
```

\*Celery is configured in Django and uses Redis as broker; the default `docker-compose` files run **API + WebSockets in the backend container only**. For reliable async jobs (notifications, etc.) in production, run one or more Celery workers against the same broker (add a worker service or run `celery -A Screengram worker` alongside the app).

| Layer | Technology |
|-------|------------|
| Back-end | Python 3.12, Django 5.2.x, Django REST Framework, Django Channels (ASGI), Celery (optional worker) |
| Front-end | Vue 3, Vite 8, Pinia, Vue Router, Tailwind CSS, Chart.js |
| Database | PostgreSQL 15 (Docker default); SQLite optional for local dev (`USE_SQLITE=True`) |
| Cache / broker / channels | Redis 7 |
| Reverse proxy | Nginx (production frontend image) |
| Containers | Docker, Docker Compose |

---

## Repository layout

```
ScreenGram/
├── app/                          # Django project root
│   ├── Screengram/               # Settings, ASGI/WSGI, root URLconf
│   ├── accounts/                 # Users, JWT, 2FA/TOTP, SSO hooks, invitations, RBAC
│   ├── analytics/                # Aggregated metrics APIs
│   ├── api_docs/                 # Swagger / OpenAPI (drf-spectacular)
│   ├── blog/                     # Marketing blog (public + admin API)
│   ├── bulk_operations/          # Batch actions API
│   ├── commands/                 # Remote device commands
│   ├── content_validation/       # Upload validation utilities
│   ├── core/                     # Rate limiting, audit, backups, system email, middleware, TV catalog
│   ├── licensing/                # License enforcement and registry integration
│   ├── log/                      # Centralized error logging
│   ├── notifications/            # Multi-channel notifications (email, SMS via Twilio), Celery tasks
│   ├── saas_platform/            # Multi-tenant management, Stripe billing, impersonation
│   ├── setup/                    # First-run installation wizard
│   ├── signage/                  # Screens, IoT endpoints, pairing, heartbeat
│   ├── templates/                # Template authoring, QR actions, media
│   ├── tickets/                  # Helpdesk: queues, SLA, routing, threads, operator bridge
│   ├── tests/                    # Pytest suite
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── frontend/                     # Vue 3 SPA
│   ├── public/documentation/     # Static product docs served with the SPA build
│   ├── src/
│   │   ├── pages/                # Route-level views (dashboard, screens, templates, player, …)
│   │   ├── components/           # Reusable UI
│   │   ├── stores/               # Pinia stores
│   │   ├── composables/          # WebSocket, responsive scaling, …
│   │   ├── services/             # Axios API layer
│   │   ├── router/
│   │   ├── layouts/              # Admin / super-admin shells
│   │   └── config/               # Navigation, feature flags
│   ├── Dockerfile                # Production: Node build → Nginx
│   ├── Dockerfile.dev            # Vite dev server
│   ├── nginx.conf                # SPA routing + API / WebSocket proxy
│   └── package.json
├── documentation/                # Source HTML for product docs (mirrored under frontend/public)
├── docker-compose.yml            # Local dev: Vite + Django hot-reload
├── docker-compose.prod.yml       # Production: Nginx + Gunicorn/Uvicorn
├── .env.example                  # Environment reference — copy to `.env`
├── install.sh                    # Docker-based installer (wraps compose)
├── requirements.txt              # Python deps (mirrors app/requirements.txt)
└── README.md
```

---

## Features

### Screens and devices

- Register, group, and monitor screens
- IoT endpoints for pairing, heartbeat, and status
- Push templates to connected screens in real time over WebSocket

### Template editor

- Drag-and-drop builder with layers and widgets
- Widgets include clock, weather, charts, video, QR code, text, image, and more
- Live preview and push-to-screen

### Scheduling and commands

- Recurring and one-off schedules
- Remote device commands (reboot, screenshot, refresh, etc.)

### Analytics

- Uptime, command outcomes, template usage, content metrics
- Trend charts with date-range filters

### Users and security

- Role-based access (admin, manager, operator, viewer, visitor)
- JWT with refresh token blacklist
- Two-factor authentication (TOTP)
- SSO-oriented hooks
- Invitations, session management, audit logging
- Rate limiting and brute-force protection

### SaaS platform (optional)

- Multi-tenant super-admin UI
- Stripe: checkout, customer portal, webhooks; plan catalog in the database
- Tenant impersonation, capacity and cohort-style reporting
- Per-tenant API keys and webhooks

### Helpdesk (tickets)

- Queues with SLA policies
- Routing rules, canned responses, tags
- Threaded conversations with attachments
- Optional mirror of tickets to an operator gateway (`TICKET_OPERATOR_BRIDGE_ENABLED`)

### Marketing blog

- Public blog API and platform admin flows for content

### Notifications

- Email and SMS (Twilio)
- Encrypted stored channel configuration
- Intended for async delivery via Celery when workers are running

### Other

- System email (SMTP) configurable from the admin UI, with env fallbacks
- Data Center page and Android TV APK URL (`ANDROID_TV_APK_URL` or build-time `VITE_ANDROID_TV_APK_URL`)
- Content upload validation, backups, license enforcement with offline grace
- Installation wizard until `installed.lock` exists under `INSTALLATION_STATE_DIR`
- Product documentation at `/documentation/`; SPA routes `/docs` and `/docs/changelog` redirect to the static HTML docs
- OpenAPI UI at `/api/docs/`

---

## Quick start (development)

### Prerequisites

- Docker and Docker Compose v2+
- A **`.env` file at the repository root** — Compose loads **only** `.env` (not `.env.example`)

### Minimal configuration before `docker compose up`

Copy [`.env.example`](.env.example) to `.env`, then set at least your **domain-related** values: `ALLOWED_HOSTS`, `BASE_URL`, and `CSRF_TRUSTED_ORIGINS` (and a strong `SECRET_KEY` for production). **`DB_PASSWORD` and `POSTGRES_PASSWORD` are optional:** Compose and the setup wizard use the same built-in default (`PCgMain_Sc7Qk9Nm2pW4vL8xH3jF6yT1sA5eB0dR`) unless you override them in `.env` (recommended for internet-facing deployments). Keep `DB_PASSWORD` and `POSTGRES_PASSWORD` identical. If you change the password after Postgres has already initialized its data volume, you may need to align credentials or reset the volume.

The **Pixelcast client** subtree ([`Pixelcast_client/`](Pixelcast_client/)) uses a **different** default database password; see [`Pixelcast_client/.env.example`](Pixelcast_client/.env.example) and its `docker-compose` files.

### Steps

```bash
git clone <repository-url> ScreenGram
cd ScreenGram

cp .env.example .env
# Edit .env: at minimum set domain/URL settings; DB password can stay at the documented default locally

docker compose up --build
```

Then open the **Vite dev app** (the browser talks to the API on the **same origin** via proxy):

| What | URL |
|------|-----|
| SPA (dev) | [http://localhost:5173](http://localhost:5173) (or the host port from `FRONTEND_HOST_PORT`) |
| API (via Vite proxy) | Same origin, e.g. `http://localhost:5173/api/…` |

The dev stack runs **PostgreSQL**, **Redis**, **Django** (Uvicorn with `--reload` when `ENABLE_HOT_RELOAD=true`), and **Vite**. The backend container **does not publish port 8000** by default; use the SPA origin so `/api`, `/iot`, and `/ws` are proxied correctly.

### Default developer account (local Compose)

When `BOOTSTRAP_DEFAULT_ADMIN=true` (default in `docker-compose.yml`), first boot can create:

- **Email:** `admin@pixelcast.com`
- **Password:** `adminadmin`

Production compose sets `BOOTSTRAP_DEFAULT_ADMIN=false`. To reset or recreate the developer user: `python manage.py ensure_default_developer --update` inside the backend environment.

### Installer script

```bash
chmod +x install.sh && ./install.sh
```

The script expects a populated `.env`; on first run it may copy from `.env.example` or generate a minimal `.env` and exit so you can review it.

---

## Production deployment

```bash
docker network create dokploy-network   # once per host, if using Traefik/Dokploy attachment
docker compose -f docker-compose.prod.yml up -d --build
```

The production bundle exposes the **Nginx** frontend on host **port 8080** (mapped `8080:80` in `docker-compose.prod.yml`). Nginx serves the built SPA and proxies `/api`, `/iot`, and `/ws` to the backend.

Set at least:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Strong random Django secret |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Full origins (`https://…`) |
| `BASE_URL` | Public site URL (affects TLS redirects and links) |
| `DB_PASSWORD` | Must stay in sync with `POSTGRES_PASSWORD` / `db` service |

`frontend` and `backend` join the external network **`dokploy-network`** so an edge proxy can reach them without binding host port 80 on the stack.

---

## Environment configuration

- **`.env`** is required for Compose and holds real values.
- **`.env.example`** documents variables; it is **not** loaded automatically.

High-level groups (see `.env.example` for the full list and comments):

| Area | Examples |
|------|----------|
| Django | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `BASE_URL` |
| Database | `DB_*`, `USE_SQLITE`, `POSTGRES_*` |
| Redis / Celery / Channels | `REDIS_*`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CHANNEL_LAYERS_BACKEND` |
| Deployment mode | `DEPLOYMENT_MODE`, `PLATFORM_SAAS_ENABLED`, `TICKET_OPERATOR_BRIDGE_ENABLED` |
| Stripe | `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`, … |
| Weather widget | `OPENWEATHER_API_KEY`, related `WEATHER_*` tuning |
| License | `LICENSE_GATEWAY_BASE_URL`, `LICENSE_SERVER_URL`, `LICENSE_ENFORCEMENT_ENABLED`, `CODECANYON_*`, `SCREENGRAM_APP_VERSION` |
| Email fallbacks | `EMAIL_*`, `DEFAULT_FROM_EMAIL` |
| Ports / dev UX | `FRONTEND_HOST_PORT`, `HTTP_PORT`, `VITE_BEHIND_HTTPS_PROXY`, optional `VITE_HMR_*` |
| SEO / marketing build | `VITE_PUBLIC_SITE_ORIGIN`, `VITE_GTM_CONTAINER_ID`, `VITE_CODECANYON_ITEM_URL`, … |
| Storage | `USE_S3_STORAGE`, `AWS_*` |

### Vite / API base URL

The SPA must use a **browser-reachable** API base. In Docker dev and prod builds this is **`/api`** (same origin; Nginx or Vite proxies to Django). Do **not** set `VITE_API_BASE_URL=https://backend:8000/...` — `backend` resolves only inside the Docker network.

---

## Troubleshooting (login / `ERR_NAME_NOT_RESOLVED`)

If the browser requests **`https://backend:8000`** (or similar), the bundle is using a Docker-only hostname. Fix:

1. Ensure `VITE_API_BASE_URL=/api` for the frontend service (as in `docker-compose.yml` / production build args).
2. After changing any `VITE_*` variable, rebuild or restart the frontend container and hard-refresh (or clear site data).
3. In DevTools, login should **`POST`** to **`/api/auth/login/`** on the **same host** as the page (e.g. `http://localhost:5173` in dev).

---

## Running tests

```bash
# Backend (pytest in the backend container)
docker compose exec backend pytest --cov

# Frontend unit tests
cd frontend && npm run test

# Frontend E2E (Playwright)
cd frontend && npm run e2e
```

---

## Tech stack summary

**Back-end:** Python 3.12 · Django 5.2 · DRF · Django Channels · Celery · Redis · PostgreSQL · drf-spectacular · SimpleJWT · pyotp · Stripe SDK · cryptography · boto3 / django-storages · Twilio (optional)

**Front-end:** Vue 3 · Vite 8 · Pinia · Vue Router · Tailwind CSS · Chart.js · Axios · Vitest · Playwright · html2canvas · vue3-moveable · @vueuse/motion · DOMPurify · marked

**Infrastructure:** Docker · Docker Compose · Nginx · Gunicorn + UvicornWorker · Redis

