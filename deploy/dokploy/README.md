# Deploy on Dokploy — pixelcast.uk

Single public origin: **`https://pixelcast.uk`** (optional `www` alias).  
Nginx in **`frontend`** serves the SPA and proxies `/api`, `/iot`, `/ws`, `/media` to Django.

## Dokploy setup (summary)

| Step | Value |
|------|--------|
| Compose file | **`compose.yaml`** or **`docker-compose.prod.yml`** — never default `docker-compose.yml` |
| Host network (once) | `docker network create dokploy-network` |
| Domain | `pixelcast.uk` → service **`frontend`** |
| Do **not** expose | `backend:8000`, `db`, `redis` |

### Domain panel (match these fields exactly)

Use this in **Domains → Add/Edit** for `pixelcast.uk`:

| Field | Value | Why |
|-------|--------|-----|
| **Service Name** | `frontend` | Nginx + SPA + `/api` proxy |
| **Host** | `pixelcast.uk` | Public hostname |
| **Path** | `/` | Whole site |
| **Internal Path** | `/` | App root |
| **Strip Path** | **Off** | Do not strip `/` |
| **Container Port** | **`80`** | Nginx listens on 80 *inside* the container — **not 443** |
| **HTTPS** | **On** | Traefik serves **public HTTPS on 443** and terminates SSL |
| **Certificate Provider** | `Let's Encrypt` | Auto SSL for `pixelcast.uk` |

**Important:** You do **not** set Container Port to `443` for full HTTPS. Port **443** is the public internet port handled by **Traefik** when **HTTPS** is enabled. Traffic flow:

```text
Browser https://pixelcast.uk:443  →  Traefik (SSL / Let's Encrypt)  →  frontend container :80 (HTTP)
```

If Container Port is `443` but Nginx only listens on `80`, the site will not load (connection refused / bad gateway).

Optional second domain: `www.pixelcast.uk` — same settings, Container Port **80**, HTTPS **On**.

Env template: [`.env.production.example`](.env.production.example) → copy to `.env` on the server.

## Environment (go-live)

| Variable | Value |
|----------|--------|
| `ALLOWED_HOSTS` | `pixelcast.uk,www.pixelcast.uk,frontend,backend,.traefik.me` |
| `CSRF_TRUSTED_ORIGINS` | `https://pixelcast.uk,https://www.pixelcast.uk` |
| `BASE_URL` | `https://pixelcast.uk` |
| `PUBLIC_WEB_APP_URL` | `https://pixelcast.uk` |
| `USE_BEHIND_PROXY` | `True` |
| `VITE_PUBLIC_SITE_ORIGIN` | `https://pixelcast.uk` (frontend **rebuild**) |
| `SECRET_KEY` | Strong random (required when `DEBUG=False`) |
| `DB_PASSWORD` | Same as `POSTGRES_PASSWORD` |
| `CHANNEL_LAYERS_BACKEND` | **`redis`** (required for WebSocket broadcasts with multiple Gunicorn workers) |
| `REDIS_HOST` | `redis` |

Rebuild frontend after `VITE_*` changes:

```bash
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d
```

## First boot

1. Wait for `backend` healthy (`/api/health/`).
2. Open **`https://pixelcast.uk/install`** and complete the wizard.
3. Production: keep `BOOTSTRAP_DEFAULT_ADMIN=false`.

## Stripe (if used)

Webhook URL:

`https://pixelcast.uk/api/platform/stripe/webhook/`

## Verify before announcing

- `https://pixelcast.uk/health` → `healthy`
- `https://pixelcast.uk/api/health/` → OK
- Login: `POST https://pixelcast.uk/api/auth/login/` (same host, not `backend:8000`)
- `https://pixelcast.uk/sitemap.xml` lists `https://pixelcast.uk/...`

### WebSocket (live dashboard updates)

1. Log in to the app, open DevTools → **Network** → filter **WS**.
2. Expect: `wss://pixelcast.uk/ws/dashboard/?token=...` with status **101 Switching Protocols**.
3. Messages should include `connection_confirmed` and periodic `pong` responses to client `ping`.
4. Backend env must include `CHANNEL_LAYERS_BACKEND=redis` (not `memory` in production).
5. Nginx proxies `/ws/` to `backend:8000` with long timeouts (see `frontend/nginx.conf`).

If WS fails with code **1006** in a loop: redeploy **frontend + backend**, sign out/in (fresh JWT), and confirm Traefik WebSocket support on the domain (HTTPS → container port **80**).

### Upload works but preview shows "Failed to load media"

1. Rebuild **frontend + backend** (nginx `/media/` uses `root /app`; API returns public `https://pixelcast.uk/media/...` URLs).
2. Open a file URL directly: `https://pixelcast.uk/media/...` — should return the image (not 404).
3. Ensure `BASE_URL` and `PUBLIC_WEB_APP_URL` are `https://pixelcast.uk` (not `http://backend:8000`).
4. Both services must mount the same volume `backend_media` at `/app/media`.

## Troubleshooting

### API returns **400** on `pixelcast.uk` (`/api/setup/status/`, `/api/public/...`)

**Cause:** Django `USE_X_FORWARDED_HOST=True` with an **empty** `X-Forwarded-Host` from Nginx → `DisallowedHost` (shows as 400).

**Fix:** Rebuild **frontend** image (nginx passes `X-Forwarded-Host` from client `Host` when upstream header is empty). Ensure Environment has:

```env
ALLOWED_HOSTS=pixelcast.uk,www.pixelcast.uk,backend,frontend,.traefik.me
BASE_URL=https://pixelcast.uk
USE_BEHIND_PROXY=True
```

### `backend` unhealthy / `dependency failed to start`

Your deploy log may end with:

```text
container ...-backend-1 is unhealthy
dependency failed to start
```

That means **Gunicorn did not pass the health probe in time** (or crashed on boot). Celery/frontend then fail because they wait on `backend`.

**Checklist (in order):**

1. **Backend logs** (Dokploy → `backend` → Logs). Look for:
   - `ImproperlyConfigured: CHANNEL_LAYERS_BACKEND must be 'redis'` → set `CHANNEL_LAYERS_BACKEND=redis` in Environment (prod compose now defaults this).
   - `ImproperlyConfigured: SECRET_KEY` → set a strong `SECRET_KEY`.
   - `password authentication failed` → `DB_PASSWORD` must match the existing Postgres volume (`POSTGRES_PASSWORD`).
   - `FATAL: database "pixelcast_signage_db" does not exist` → wait for entrypoint `ensure_postgres_db` or fix `DB_NAME`.
2. **Env (required for production):**
   ```env
   CHANNEL_LAYERS_BACKEND=redis
   SECURE_SSL_REDIRECT=false
   USE_BEHIND_PROXY=True
   ```
3. **First deploy is slow** — migrations + `collectstatic` run before Gunicorn. Prod compose allows **420s** `start_period` on `backend`. Dokploy must not use a deploy wait timeout shorter than ~7 minutes on first boot.
4. **Health probe** — Docker calls `GET http://127.0.0.1:8000/api/health/live/` (no install lock required).
5. **Disk space** — full disk during image build can leave containers half-started; run `df -h` on the host.

**After deploy succeeds:** open `https://pixelcast.uk/install` if this is a fresh server.

**Manual check on the server:**

```bash
docker logs pixelcast-saas-eqm4aq-backend-1 --tail 120
docker inspect pixelcast-saas-eqm4aq-backend-1 --format '{{json .State.Health}}'
curl -sS http://127.0.0.1:8080/api/health/live/   # via published frontend port if mapped
```

### Frontend logs show `vite --port 5173` or `npm run dev`

**Cause:** Dokploy is using **`docker-compose.yml`** (local dev), not production.

**Fix:**

1. Dokploy → Application → **Compose file** → set to **`compose.yaml`** or **`docker-compose.prod.yml`**
2. Remove any custom **Start command** on `frontend` (must not run `npm run dev`)
3. **Redeploy** with **Rebuild** enabled
4. Logs should show: `[pixelcast] production: nginx on :80` — not Vite `5173`
5. Domain **Container Port** = **80** (HTTPS stays **On** for public 443)

| Issue | Fix |
|-------|-----|
| 400 DisallowedHost | Add host to `ALLOWED_HOSTS` |
| CSRF / cookie on HTTPS | `CSRF_TRUSTED_ORIGINS` + `USE_BEHIND_PROXY=True` |
| API 503 | Finish `/install` or set `PIXELCAST_SIGNAGE_INSTALLED=true` after lock file exists |
| `backend:8000` in browser | Rebuild frontend (`VITE_API_BASE_URL=/api` in compose) |

See [`../../README.md`](../../README.md) → Production deployment.
