# cPanel Installation Guide

PixelCast Signage is built to run behind a reverse proxy (nginx in Docker). On shared cPanel hosting, you typically won’t be able to run Docker the same way, so this guide focuses on a common hosting approach:

1. Run the **backend** as a long-running Python process (or via cPanel “Setup Python App”)
2. Host the **frontend** as static files
3. Configure your web server to proxy:
   - `/api` and `/admin` to the backend
   - `/iot` (screen/player endpoints) to the backend
   - `/media` (uploads) to the backend
   - `/ws` to the backend if WebSockets are supported

Because cPanel setups vary a lot, choose the option that matches your host.

## Assumptions (read first)

This guide assumes:

- You have **SSH access** to your cPanel account.
- Your host either:
  - provides a way to run a long-running process (Gunicorn/uvicorn) reliably, or
  - provides cPanel “Setup Python App”.
- You can configure reverse proxying for the paths listed above (via Apache modules, if allowed by your host).

If any of those are not available, the “deploy” part will need adjustment for your specific cPanel environment.

## Option A (recommended on shared cPanel): SQLite + same-domain reverse proxy

SQLite avoids PostgreSQL setup, which is often the biggest blocker on shared cPanel.

### 1. Prepare your hosting directories

From your SSH session, create a folder (example):
```bash
mkdir -p ~/screengram
cd ~/screengram
```

Upload or clone the project into `~/screengram/ScreenGram` (or move files there).

### 2. Configure `.env`

From the repo root:
```bash
cp env.example .env
```
Edit `.env`:

- Set:
  - `SECRET_KEY` to a strong value
  - `DEBUG=False`
  - `ALLOWED_HOSTS` to your domain (example: `ALLOWED_HOSTS=example.com,www.example.com`)
  - `BASE_URL` to your public URL (example: `https://example.com`)
- Enable SQLite:
  - `USE_SQLITE=True`
- After you successfully migrate/create admin, you can skip the `/install` wizard by setting:
  - `PIXELCAST_SIGNAGE_INSTALLED=true`

### 3. Install Python dependencies in a virtualenv

From the repo root:
```bash
python3.12 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r BackEnd/requirements.txt
```

### 4. Migrate the database and collect static files

```bash
cd BackEnd
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
```

### 5. Create an admin user

```bash
python manage.py createsuperuser
```

Then set `PIXELCAST_SIGNAGE_INSTALLED=true` in your repo-root `.env`.

### 6. Build the frontend (Vue)

From the repo root:
```bash
cd FrontEnd
npm ci

# Build so the dashboard calls same-origin /api
VITE_API_BASE_URL=/api npm run build
```

Deploy `FrontEnd/dist/` to your web root (commonly `~/public_html/`).

SPA routing:
- Ensure unknown routes (like `/install`) return `index.html`.
- Many hosts support this via a custom rule or `.htaccess`.

### 7. Start the backend (Gunicorn)

Run backend on a private port (example `8000`) bound to localhost:
```bash
cd ~/screengram/ScreenGram/BackEnd
source ../venv/bin/activate

gunicorn Screengram.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 120
```

If you want WebSockets, use ASGI (and ensure your hosting supports it):
```bash
gunicorn Screengram.asgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120
```

### 8. Configure reverse proxy routes

You must proxy these paths to the backend at `http://127.0.0.1:8000`:

- `/api/` -> backend
- `/admin/` -> backend
- `/iot/` -> backend (screen/player endpoints)
- `/public-iot/` -> backend
- `/media/` -> backend (uploads)
- `/ws/` -> backend (WebSocket endpoints; optional)

How you implement this depends on your cPanel. Common patterns:

- If your host allows editing Apache config / includes, configure proxy at the vhost level.
- If your host blocks proxy in Apache, you may need an alternate deployment (for example, running nginx or using a VPS instead of shared cPanel).

### 9. Permissions for uploads

Ensure uploads can be written:

- `BackEnd/media/` must be writable by the user running Gunicorn.

If you see upload errors, fix permissions:
```bash
chmod -R 775 BackEnd/media
```

## Option B: PostgreSQL (if your cPanel provides it)

If your cPanel supports PostgreSQL (or you have your own PostgreSQL server):

1. Set in `.env`:
   - `USE_SQLITE=False`
   - `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
2. Run:
```bash
cd BackEnd
python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear
python manage.py createsuperuser
```
3. Either:
   - set `PIXELCAST_SIGNAGE_INSTALLED=true`, or
   - use the `/install` wizard in the browser to finalize.

## `/install` wizard (works if backend is reachable)

If you did not set `PIXELCAST_SIGNAGE_INSTALLED=true`, open:

- `https://yourdomain.com/install`

Then complete the steps. The frontend calls these endpoints:
- `GET /api/setup/status/`
- `POST /api/setup/db-check/`
- `POST /api/setup/run-migrations/`
- `POST /api/setup/create-admin/`
- `POST /api/setup/finalize/`

## WebSockets warning (important)

Many shared cPanel setups cannot properly proxy WebSockets.

- If WebSockets fail, the system can still function through HTTP endpoints + polling (template polling and command pull).
- If you need full real-time WebSocket reliability, consider moving to a VPS where you can configure nginx and run ASGI correctly.

