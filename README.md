# PixelCast — Digital Signage Platform

PixelCast is a self-hosted (or SaaS) digital signage system for managing screens, templates, schedules, and media content across distributed displays. It combines a Django REST back-end with real-time WebSocket communication, a Vue 3 single-page front-end, and an in-browser web player that renders content on any screen with a modern browser.

---

## Architecture

```
                     ┌──────────────┐
   Browser / TV  ──▶ │  Nginx (SPA) │──▶ /api/, /iot/, /ws/ ──▶ Django (Gunicorn + Uvicorn)
                     └──────────────┘                            │         │         │
                                                           PostgreSQL   Redis    Celery
```

| Layer | Technology |
|-------|-----------|
| Back-end | Django 5.2, Django REST Framework, Django Channels (ASGI), Celery |
| Front-end | Vue 3, Vite, Pinia, Tailwind CSS, Chart.js |
| Database | PostgreSQL 15 (SQLite supported for dev) |
| Cache / Broker | Redis 7 |
| Reverse proxy | Nginx (production container) |
| Containers | Docker, Docker Compose |

---

## Repository layout

```
PixelCast/
├── app/                          # Django project root
│   ├── Screengram/               #   Project settings, ASGI/WSGI, root URL conf
│   ├── accounts/                 #   Users, JWT auth, 2FA/TOTP, SSO, invitations, RBAC
│   ├── analytics/                #   Aggregated metrics APIs
│   ├── api_docs/                 #   Swagger / OpenAPI (drf-spectacular)
│   ├── bulk_operations/          #   Batch actions API
│   ├── commands/                 #   Remote device commands
│   ├── content_validation/       #   Upload validation utilities
│   ├── core/                     #   Rate limiting, audit logs, backups, system email, middleware
│   ├── licensing/                #   License enforcement middleware
│   ├── log/                      #   Centralized error logging
│   ├── notifications/            #   Multi-channel notifications (email, SMS via Twilio), Celery tasks
│   ├── saas_platform/            #   Multi-tenant management, Stripe billing, impersonation
│   ├── setup/                    #   Installation wizard
│   ├── signage/                  #   Screens, IoT endpoints, device pairing / heartbeat
│   ├── templates/                #   Template authoring, QR actions, media
│   ├── tickets/                  #   Helpdesk: queues, SLA, routing, threads, attachments
│   ├── tests/                    #   Centralised test suite (pytest)
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── requirements.txt
├── frontend/                     # Vue 3 SPA
│   ├── src/
│   │   ├── pages/                #   Route-level views (dashboard, screens, templates, player …)
│   │   ├── components/           #   Reusable UI (analytics charts, player widgets, layout …)
│   │   ├── stores/               #   Pinia state stores
│   │   ├── composables/          #   Vue composables (WebSocket, responsive scaling …)
│   │   ├── services/             #   Axios API layer
│   │   ├── router/               #   Vue Router config
│   │   ├── layouts/              #   Shell layouts (admin, super-admin)
│   │   └── config/               #   Navigation, feature flags
│   ├── Dockerfile                #   Multi-stage: Node build → Nginx
│   ├── Dockerfile.dev            #   Vite dev server
│   ├── nginx.conf                #   SPA routing + API / WebSocket proxy
│   └── package.json
├── docker-compose.yml            # Local development (Vite + Django hot-reload)
├── docker-compose.prod.yml       # Production (Nginx + Gunicorn/Uvicorn)
├── .env.example                  # Environment template — copy to .env
├── install.sh                    # Docker-based installer
├── requirements.txt              # Python dependencies (mirrors app/requirements.txt)
└── README.md
```

---

## Features

### Screen & device management
- Register, group, and monitor screens
- IoT endpoints for device pairing, heartbeat, and status
- Push templates to connected screens in real time via WebSocket

### Template editor
- Drag-and-drop template builder with layers and widgets
- Built-in widgets: clock, weather, chart, video, QR code, text, image, and more
- Live preview and push-to-screen

### Scheduling & commands
- Recurring and one-off content schedules
- Remote device commands (reboot, screenshot, refresh, etc.)

### Analytics
- Screen uptime, command success rates, template usage, content metrics
- Activity trend charts with date-range filtering

### User management & security
- Role-based access control (admin, manager, operator, viewer, visitor)
- JWT authentication with token blacklist
- Two-factor authentication (TOTP)
- SSO-ready architecture
- User invitations
- Session management and audit logging
- Rate limiting and brute-force protection

### SaaS platform (optional)
- Multi-tenant management with super-admin UI
- Stripe billing: checkout, customer portal, webhooks
- Tenant impersonation, capacity dashboard, cohort analytics
- Per-tenant API keys and webhook integrations

### Helpdesk / tickets
- Support ticket queues with SLA policies
- Automatic routing rules, canned responses, tags
- Threaded conversations with attachments
- Separate requester and platform-admin APIs

### Notifications
- Email and SMS (Twilio) delivery
- Encrypted channel configuration
- Async dispatch via Celery

### Additional
- System email settings (SMTP configuration from admin UI)
- Data Center page with Android TV APK download link
- Content upload with validation
- Backup management
- License enforcement with offline grace period
- Installation wizard for first-run setup
- In-app product documentation at `/docs`
- OpenAPI / Swagger documentation at `/api/docs/`

---

## Quick start (development)

### Prerequisites

- Docker and Docker Compose v2+

### Steps

```bash
# 1. Clone the repository
git clone <repo-url> && cd PixelCast

# 2. Create your environment file
cp .env.example .env
# Edit .env — at minimum review SECRET_KEY and DB_PASSWORD

# 3. Start all services
docker compose up --build

# 4. Open the app
#    Frontend:  http://localhost:5173
#    Backend:   http://localhost:8000/api/
```

The development compose file (`docker-compose.yml`) starts:

| Service | Description |
|---------|-------------|
| **db** | PostgreSQL 15 |
| **redis** | Redis 7 |
| **backend** | Django with Uvicorn hot-reload |
| **frontend** | Vite dev server on port 5173 |

Or use the installer script:

```bash
chmod +x install.sh && ./install.sh
```

---

## Production deployment

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

This starts Nginx on **port 8080** (configurable), proxying to Gunicorn/Uvicorn for Django. Set these `.env` variables for production:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret — generate a strong random value |
| `ALLOWED_HOSTS` | Comma-separated hostnames |
| `CSRF_TRUSTED_ORIGINS` | Full origin URLs (`https://…`) |
| `BASE_URL` | Public URL of the deployment |
| `DB_PASSWORD` / `POSTGRES_PASSWORD` | Database credentials (must match) |

### Behind a reverse proxy (Traefik / Dokploy)

The production compose file attaches to the external `dokploy-network`. Create it once on the host if it doesn't exist:

```bash
docker network create dokploy-network
```

Set `VITE_BEHIND_HTTPS_PROXY=1` and configure `CSRF_TRUSTED_ORIGINS` to your domain.

---

## Environment reference

See `.env.example` for the full list. Key sections:

| Section | Variables |
|---------|-----------|
| Django | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` |
| Database | `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `USE_SQLITE` |
| Redis / Celery | `REDIS_HOST`, `REDIS_PORT`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` |
| Deployment mode | `DEPLOYMENT_MODE` (`saas`, `self_hosted`, `hybrid`) |
| SaaS / Stripe | `PLATFORM_SAAS_ENABLED`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID` |
| Weather widget | `OPENWEATHER_API_KEY` |
| License | `LICENSE_SERVER_URL`, `LICENSE_ENFORCEMENT_ENABLED` |
| Email (fallback) | `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` |
| Ports | `BACKEND_PORT`, `FRONTEND_HOST_PORT`, `HTTP_PORT` |

---

## Running tests

```bash
# Back-end (pytest inside the backend container)
docker compose exec backend pytest --cov

# Front-end (Playwright e2e)
cd frontend && npx playwright test
```

---

## Tech stack summary

**Back-end:** Python 3.12 · Django 5.2 · DRF · Django Channels · Celery · Redis · PostgreSQL · drf-spectacular · SimpleJWT · pyotp · Stripe SDK · cryptography · boto3 / django-storages

**Front-end:** Vue 3 · Vite · Pinia · Vue Router · Tailwind CSS · Chart.js · Axios · Playwright · html2canvas · vue3-moveable · @vueuse/motion

**Infrastructure:** Docker · Docker Compose · Nginx · Gunicorn + Uvicorn · Redis (cache + broker + channel layer)
