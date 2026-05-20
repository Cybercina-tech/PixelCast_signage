# Deploy on Dokploy — pixelcast.uk

Single public origin: **`https://pixelcast.uk`** (optional `www` alias).  
Nginx in **`frontend`** serves the SPA and proxies `/api`, `/iot`, `/ws`, `/media` to Django.

## Dokploy setup (summary)

| Step | Value |
|------|--------|
| Compose file | `docker-compose.prod.yml` |
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

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 400 DisallowedHost | Add host to `ALLOWED_HOSTS` |
| CSRF / cookie on HTTPS | `CSRF_TRUSTED_ORIGINS` + `USE_BEHIND_PROXY=True` |
| API 503 | Finish `/install` or set `PIXELCAST_SIGNAGE_INSTALLED=true` after lock file exists |
| `backend:8000` in browser | Rebuild frontend (`VITE_API_BASE_URL=/api` in compose) |

See [`../../README.md`](../../README.md) → Production deployment.
