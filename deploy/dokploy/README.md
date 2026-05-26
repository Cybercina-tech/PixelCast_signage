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
| Do **not** attach `backend` to `dokploy-network` | Traefik may steal `pixelcast.uk` traffic → 404 on `/health` and `/` |

> Note: Docker Compose `--watch` hot-reload is for manual `docker compose` runs. Dokploy deploys from git/build jobs and does not run `up --watch` continuously.

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

### `/health` or the whole site returns **404** (Traefik hits Django instead of Nginx)

**Symptom:** Browser DevTools shows `GET /health` → **404**, or every page is 404.  
**Cause:** `backend` is on `dokploy-network` **and** Traefik auto-discovers it. Some requests go to **Gunicorn :8000** (no `/health`, no Vue SPA) instead of **frontend Nginx :80**.

**Fix (pick one):**

1. **Recommended:** Remove `dokploy-network` from service `backend` in compose (only `frontend` needs it). Redeploy.
2. Or add on `backend`: `traefik.enable=false`
3. Domain in Dokploy must stay on service **`frontend`**, container port **80**.

**Quick test:**

| URL | If routed to Nginx (correct) | If routed to Django (wrong) |
|-----|------------------------------|-----------------------------|
| `https://pixelcast.uk/health` | `200` + body `healthy` | **404** |
| `https://pixelcast.uk/api/health/live/` | `200` JSON | `200` JSON (misleading — API works but site broken) |

### Domain shows **404** but Dokploy domain settings look correct

Most often **`frontend` never started** because it waited for `backend` to become healthy (first deploy: migrations can take 5–10 minutes). Traefik then has no container to route to → **404**.

**On the server (SSH), run:**

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "frontend|backend|NAMES"
curl -sS http://127.0.0.1:8080/health || echo "8080 not reachable"
docker logs "$(docker ps -aq -f name=backend | head -1)" --tail 80
```

| What you see | Meaning |
|--------------|---------|
| No `frontend` container, or `Created` / `Exited` | Frontend blocked on backend; fix backend first, redeploy with latest `docker-compose.prod.yml` (frontend starts after `backend` is **started**, not only healthy). |
| `curl` → `healthy` but domain 404 | Traefik/network: confirm `docker network inspect dokploy-network` lists the **frontend** container; domain service = `frontend`, container port **80**. |
| `curl` fails | Stack not up or wrong compose file (`docker-compose.yml` = Vite dev). |
| Backend logs: `ImproperlyConfigured` / `SECRET_KEY` / `CHANNEL_LAYERS` | Set env in Dokploy from [`.env.production.example`](.env.production.example). |
| Backend logs: `password authentication failed` | `DB_PASSWORD` must match the **existing** Postgres volume from first deploy. |

After pulling the compose fix: **Redeploy → Rebuild** all services. Then open `https://pixelcast.uk/health` (should be `healthy`) and `https://pixelcast.uk/install` on first boot.

### API returns **502** — frontend logs: `connect() failed (111: Connection refused)` to `backend:8000`

**Symptom:** Nginx (frontend) is up (`[pixelcast] production: nginx on :80`) but every `/api/...` returns **502**. Frontend log shows:

`upstream: "http://172.x.x.x:8000/..."` and `Connection refused`.

**Cause:** Django/Gunicorn is **not listening** on port 8000 — usually the `backend` container is still migrating, crashed on boot, or stuck restarting.

**Fix:**

1. In Dokploy, open **backend** container logs (not frontend).
2. Look for:
   - `AttributeError: 'CookieMiddleware' object has no attribute 'callback'` → old ASGI routing bug; **pull latest code** and rebuild backend.
   - `ImproperlyConfigured` / `CHANNEL_LAYERS_BACKEND` → set `CHANNEL_LAYERS_BACKEND=redis` in env.
   - `password authentication failed` → `DB_PASSWORD` = `POSTGRES_PASSWORD` (match existing Postgres volume).
   - Still running migrations → wait 5–10 minutes on first deploy, then retry `https://pixelcast.uk/api/health/live/`.
3. SSH check:

```bash
docker ps -a | grep backend
docker logs "$(docker ps -aq -f name=backend | head -1)" --tail 120
curl -sS -H 'Host: localhost' http://127.0.0.1:8000/api/health/live/   # from inside backend network if needed
```

When backend is healthy, `https://pixelcast.uk/api/health/` should return JSON (not 502).

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
