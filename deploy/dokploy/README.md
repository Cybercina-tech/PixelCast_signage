# Deploy PixelCast Signage on Dokploy

Production domains:

| Host | Role |
|------|------|
| `https://pixelcast.uk` | Public marketing / SEO canonical (`VITE_PUBLIC_SITE_ORIGIN`) |
| `https://www.pixelcast.uk` | Optional alias → same app |
| `https://app.pixelcast.uk` | Web app, API (`/api`), IoT (`/iot`), WebSockets (`/ws`) |

One Compose stack serves the Vue SPA (Nginx) and proxies API traffic to Django. Point **both** hostnames at the **`frontend`** service (container port **80**).

## 1. Host preparation

On the Dokploy server (once):

```bash
docker network create dokploy-network
```

## 2. Dokploy application

1. **Source**: Git repository for this project.
2. **Compose file**: `docker-compose.prod.yml`
3. **Environment**: copy [`deploy/dokploy/.env.production.example`](.env.production.example) to `.env` on the server, or paste variables into Dokploy → **Environment**.
4. Set a strong `SECRET_KEY` and `DB_PASSWORD` / `POSTGRES_PASSWORD` (must match).
5. **Build**: enable build on deploy; first deploy runs `docker compose -f docker-compose.prod.yml up -d --build`.

Services `frontend` and `backend` join **`dokploy-network`** so Traefik can reach them without binding host port 80.

## 3. Domains in Dokploy (Traefik)

Add two domains (or three with `www`) on the **`frontend`** service:

| Domain | Container port | HTTPS |
|--------|----------------|-------|
| `pixelcast.uk` | 80 | Let's Encrypt |
| `www.pixelcast.uk` | 80 | redirect to apex or same service |
| `app.pixelcast.uk` | 80 | Let's Encrypt |

Do **not** expose `backend:8000` publicly. The browser must call **`/api`** on the same origin as the SPA (Nginx proxy).

Optional: stop publishing host port `8080` in production if you only use `dokploy-network` (remove the `ports:` block from `frontend` in a Dokploy-specific override, or firewall 8080).

## 4. Environment checklist (go-live)

| Variable | Production value |
|----------|------------------|
| `ALLOWED_HOSTS` | `pixelcast.uk,www.pixelcast.uk,app.pixelcast.uk,frontend,backend,.traefik.me` |
| `CSRF_TRUSTED_ORIGINS` | `https://pixelcast.uk,https://www.pixelcast.uk,https://app.pixelcast.uk` |
| `BASE_URL` | `https://app.pixelcast.uk` |
| `PUBLIC_WEB_APP_URL` | `https://app.pixelcast.uk` |
| `USE_BEHIND_PROXY` | `True` |
| `DEBUG` | `False` |
| `BOOTSTRAP_DEFAULT_ADMIN` | `false` |
| `VITE_PUBLIC_SITE_ORIGIN` | `https://pixelcast.uk` (requires **frontend rebuild**) |
| `VITE_PUBLIC_REGION` | `UK` (optional, rebuild) |

After changing any `VITE_*` variable:

```bash
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d frontend
```

## 5. First boot

1. Wait until `backend` healthcheck passes (`/api/health/`).
2. Open `https://app.pixelcast.uk/install` and finish the setup wizard (or set `PIXELCAST_SIGNAGE_INSTALLED=true` only after `installed.lock` exists).
3. Create admin via wizard; do not rely on `BOOTSTRAP_DEFAULT_ADMIN` in production.

## 6. Stripe webhooks (if SaaS billing)

Register webhook endpoint on Stripe Dashboard:

`https://app.pixelcast.uk/api/platform/stripe/webhook/`

Set `STRIPE_WEBHOOK_SECRET` in `.env`.

## 7. Verify

- `https://app.pixelcast.uk/health` → `healthy`
- `https://app.pixelcast.uk/api/health/` → JSON OK
- Login: DevTools → `POST https://app.pixelcast.uk/api/auth/login/` (not `backend:8000`)
- `https://pixelcast.uk/` → landing; sitemap at `https://pixelcast.uk/sitemap.xml` uses `VITE_PUBLIC_SITE_ORIGIN`

## 8. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ERR_NAME_NOT_RESOLVED` for `backend:8000` | Rebuild frontend; ensure `VITE_API_BASE_URL=/api` at build (see `docker-compose.prod.yml`). |
| 400 DisallowedHost | Add hostname to `ALLOWED_HOSTS`. |
| CSRF / login fails on HTTPS | Set `CSRF_TRUSTED_ORIGINS` and `USE_BEHIND_PROXY=True`. |
| Mixed Content / WebSocket | Same-origin `/ws` via Nginx; avoid absolute `http://` API URLs. |
| 503 on `/api` | Complete `/install` or set `PIXELCAST_SIGNAGE_INSTALLED=true` after install. |

See also root [`README.md`](../../README.md) → Production deployment.
