# Hot Module Replacement (HMR) - Docker Development

Save-to-refresh is now enabled for the frontend when using Docker.

## Quick Start

```bash
# Option A: Dev override (excludes production frontend)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Option B: Explicit dev stack
docker compose up db redis backend frontend-dev

# Open in browser
# http://localhost:5173
```

Edit any `.vue` or `.css` file in `FrontEnd/` – changes appear instantly without restarting the container.

## Clean Slate (Fix Frozen / Stuck UI)

If the UI is stuck on an old version or changes aren't appearing:

```bash
# 1. Stop everything
docker compose down

# 2. Remove frontend-dev container and its volumes (clears cached node_modules)
docker compose rm -f frontend-dev 2>/dev/null
docker volume prune -f

# 3. Rebuild and start with dev frontend
docker compose build --no-cache frontend-dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or with explicit services:
docker compose up db redis backend frontend-dev
```

## How It Works

- **frontend-dev** runs Vite dev server (`npm run dev`) – NOT `npm run build` + nginx
- Your local `./FrontEnd` folder is mounted: `./FrontEnd:/app`
- Anonymous volume `node_modules` prevents local packages from overwriting container's
- `CHOKIDAR_USEPOLLING=true` – mandatory for Docker to detect file saves on Windows/WSL
- Vite config: `usePolling: true`, `host: true`, `strictPort: true`, `hmr.clientPort: 5173`

## Production vs Development

| Command | Frontend | Port | Use Case |
|---------|----------|------|----------|
| `docker compose up` | Nginx (built) | 80 | Production |
| `docker compose -f docker-compose.yml -f docker-compose.dev.yml up` | Vite dev | 5173 | Development with HMR |
| `docker compose up db redis backend frontend-dev` | Vite dev | 5173 | Development with HMR |

## Troubleshooting

**Changes not detected?**
- Use `frontend-dev`, not `frontend` (prod uses static build)
- Ensure `CHOKIDAR_USEPOLLING=true` (set in docker-compose)
- On Windows: add project to Docker Desktop → Settings → Resources → File sharing
- Run clean slate (see above)

**API calls failing?**
- Backend must be running: `docker compose up backend`
- Check network: `docker network inspect screengram-net`

**Port 5173 in use?**
- Change port in docker-compose: `"5174:5173"`
- Add `server.port: 5174` in `vite.config.js`
