# Installation Guide (Project Root)

This guide explains how to install and run PixelCast Signage.

## What you’re installing

1. **Backend**: Django app (`BackEnd/`) with REST API + optional WebSockets (Django Channels)
2. **Frontend**: Vue 3 app (`FrontEnd/`) built to static files and served by nginx (or your web server)
3. **Database**: PostgreSQL (recommended for production) or SQLite (for simple deployments)
4. **Redis (optional)**: used for caching/channel layers/Celery when configured

## Quick start (Docker)

If your host can run Docker, this is the simplest path (it also runs the migrations automatically on container start).

1. Copy configuration:
   - Create `.env` in the repo root from `env.example` and set:
     - `SECRET_KEY`
     - `DB_PASSWORD`
     - `LICENSE_SERVER_URL` (for license checks)
     - `CODECANYON_TOKEN` (optional auth for your license server)
2. Start the stack:
```bash
docker compose up -d
```
3. Open the app in a browser:
   - Frontend is served by the `frontend` container (configured by `FRONTEND_PORT` in `.env`, default `80`).

Notes:
- The backend uses an installation wizard. On first run you may see the `/install` page in the frontend to finalize setup.

## Non-Docker install (recommended for servers/VPS)

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+ (optional if you use SQLite)
- Redis (optional; only needed if you want Redis-based caching/channels)

### 1. Create a virtualenv and install Python dependencies

From the repo root:
```bash
python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r BackEnd/requirements.txt
```

### 2. Configure environment variables

1. Create `.env` in the repo root:
```bash
cp env.example .env
```
2. Edit `.env`:
   - Set a strong `SECRET_KEY`
   - Set `DB_PASSWORD`
   - Set `DB_HOST` (for example `localhost` if PostgreSQL runs on the same server)
   - Set `BASE_URL` to your public URL (example: `https://example.com`)
   - Update `ALLOWED_HOSTS` to include your domain
   - Configure licensing:
     - `LICENSE_SERVER_URL` (required for enforced validation)
     - `CODECANYON_PRODUCT_ID` (can remain empty before marketplace publish)
     - `LICENSE_ENFORCEMENT_ENABLED=True`
     - `LICENSE_OFFLINE_GRACE_HOURS=72`
3. If you want **SQLite** instead of PostgreSQL:
   - set `USE_SQLITE=True`
   - you can still keep `DB_*` values, but the Django DB engine will use `db.sqlite3`

### 3. Run database migrations

```bash
cd BackEnd
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
```

### 4. Create an admin user

```bash
python manage.py createsuperuser
```

If you prefer passing flags, Django will still prompt for any missing fields.

### 5. Start the backend

Backend can run in HTTP mode (WSGI) or full ASGI mode (required for WebSockets).

HTTP-only (simple deployments):
```bash
gunicorn Screengram.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3
```

ASGI (recommended; WebSockets capable):
```bash
gunicorn Screengram.asgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120
```

### 6. Build and deploy the frontend

From the repo root:
```bash
cd FrontEnd
npm ci

# IMPORTANT:
# - If your backend is available on the same domain under /api, build with /api.
# - This is required because the dashboard uses VITE_API_BASE_URL at build time.
VITE_API_BASE_URL=/api npm run build
```

Deploy the generated `FrontEnd/dist/` to your web server document root.

Routing note (SPA):
- Vue uses history mode. Your web server must route unknown paths to `index.html` (so `/install`, `/dashboard`, etc. work).

## Installation wizard (/install)

The backend includes an installation wizard UI at frontend route `/install`.

Setup endpoints are under:
- `GET /api/setup/status/`
- `POST /api/setup/db-check/`
- `POST /api/setup/run-migrations/`
- `POST /api/setup/seed-assets/`
- `POST /api/setup/create-admin/`
- `POST /api/setup/finalize/`

If you run migrations/admin manually (sections above), you can also skip the wizard by setting one of:
- `PIXELCAST_SIGNAGE_INSTALLED=true` in `.env`, or
- ensuring `installed.lock` exists under `INSTALLATION_STATE_DIR` (in Docker it’s mounted to `/app/installation_state`).

## License activation (MVP)

After first admin login, open `/settings/license` in the dashboard:

- `GET /api/license/status/` shows current state, product-id source (`env`/`db`/`temporary`), and grace window.
- `POST /api/license/activate/` saves purchase code and performs immediate validation.
- `POST /api/license/revalidate/` forces a fresh validation call.

Notes:
- If `CODECANYON_PRODUCT_ID` is empty, the backend uses temporary mode payloads so you can launch before CodeCanyon item publish.
- Once published, set `CODECANYON_PRODUCT_ID` in `.env` and restart; no source changes are required.

## Updating

On update:
1. Pull the new code
2. Rebuild frontend (`npm ci` + `npm run build`)
3. Run backend migrations (`python manage.py migrate --noinput`)
4. Restart backend

## Troubleshooting checklist

- Backend not serving API:
  - Verify the server is running on `8000`
  - Verify reverse proxy rules (if you use nginx/Apache) forward `/api` to the backend
- Media uploads fail:
  - Ensure `BackEnd/media/` is writable by the backend user
- Frontend shows incorrect API URLs:
  - Rebuild frontend with the correct `VITE_API_BASE_URL`

