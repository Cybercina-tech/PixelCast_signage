# Docker Stack Fixes - ScreenGram

## Problems Fixed

### 1. **Backend Crash Loop** ✅
**Root Cause:** `set -e` + `check_installation` returning 1 caused script to exit
- **Fix:** Added `|| true` to prevent exit when lock file missing
- **Fix:** Added `set -x` for detailed debugging output
- **Fix:** Volume mount changed from file to directory

### 2. **Volume Mount Issue** ✅
**Root Cause:** `installation_state:/app/installed.lock` mounted volume as directory, not file
- **Fix:** Changed to `installation_state:/app/installation_state` (directory)
- **Fix:** Lock file now at `/app/installation_state/installed.lock`
- **Fix:** Added permission checks and `mkdir -p` in entrypoint

### 3. **Nginx "host not found" Error** ✅
**Root Cause:** Nginx crashes if upstream `backend:8000` doesn't exist at startup
- **Fix:** Added Docker DNS resolver `127.0.0.11`
- **Fix:** Changed all proxy_pass to use variables (`$backend_upstream`)
- **Fix:** This allows Nginx to start even if backend is down/restarting

### 4. **Container Naming Mismatch** ✅
**Root Cause:** `container_name: screengram_backend` didn't match `upstream backend`
- **Fix:** Changed container names to match service names:
  - `backend` (was `screengram_backend`)
  - `frontend` (was `screengram_frontend`)
  - `db` (was `screengram_postgres`)
  - `redis` (was `screengram_redis`)

## Files Changed

1. **docker-compose.yml**
   - Volume: `installation_state:/app/installation_state`
   - Container names simplified
   - Added `INSTALLATION_STATE_DIR` env var
   - Frontend depends_on: `service_started` (not healthy)

2. **BackEnd/entrypoint.sh**
   - Added `set -x` for debugging
   - Added `ensure_installation_state_dir()` function
   - Fixed lock path: `${INSTALLATION_STATE_DIR}/installed.lock`
   - Added permission checks (chmod 777)
   - `check_installation || true` prevents exit

3. **BackEnd/Screengram/settings.py**
   - Added `INSTALLATION_STATE_DIR` setting

4. **BackEnd/setup/utils.py**
   - `get_installed_lock_path()` uses `INSTALLATION_STATE_DIR`
   - `is_installed()` uses `is_file()` not `exists()`
   - `mark_as_installed()` handles permissions properly

5. **FrontEnd/nginx.conf**
   - Added `resolver 127.0.0.11`
   - All `proxy_pass` use `$backend_upstream` variable
   - Upstream has `max_fails=3 fail_timeout=30s`

## How to Deploy

### Clean Start (Recommended)

```bash
# Stop everything
docker compose down

# Remove old installation state volume (forces fresh install)
docker volume rm screengram_installation_state 2>/dev/null || true

# Rebuild images (includes new entrypoint + nginx config)
docker compose build --no-cache

# Start stack
docker compose up -d

# Watch logs
docker compose logs -f
```

### Quick Restart (Keep Data)

```bash
# Restart with new configs
docker compose down
docker compose up -d --build

# Check status
docker compose ps
```

### Diagnostic Commands

```bash
# Run diagnostic script
./diagnose.sh

# Check backend logs
docker compose logs -f backend

# Check if backend can connect to DB
docker compose exec backend python manage.py check --database default

# Test database migration
docker compose run --rm backend python manage.py migrate --check

# Access backend shell
docker compose exec backend bash

# Check installation state directory
docker compose exec backend ls -la /app/installation_state/
```

## Expected Behavior

### ✅ Correct Startup Sequence

1. **Database** starts, health check passes
2. **Redis** starts, health check passes
3. **Backend** starts:
   - Waits for PostgreSQL (60 retries)
   - Creates `/app/installation_state/` with 777 perms
   - Runs migrations (if DB available)
   - Checks for lock file (logs warning if missing)
   - Collects static files
   - **Starts Gunicorn** (stays running)
4. **Frontend** starts:
   - Nginx starts even if backend unavailable
   - Returns 502 Bad Gateway if backend down
   - Works normally once backend is healthy

### ✅ Installation Flow

1. Open `http://localhost` → Shows installation wizard
2. Complete wizard → Creates `/app/installation_state/installed.lock`
3. Restart backend → Finds lock file, skips wizard
4. Normal operation

### ❌ What to Watch For

- **Backend exits immediately after "Installation lock file not found"**
  - Check: `docker compose logs backend | grep -A 10 "Installation lock"`
  - Should continue to "Starting Gunicorn server..."
  - If exits: Check `set -x` output for exact failing command

- **Nginx shows "host not found in upstream"**
  - Check: Container names match (`docker compose ps`)
  - Backend should be named `backend` not `screengram_backend`
  - Restart frontend after fixing names

- **Lock file not created after installation**
  - Check: `docker compose exec backend ls -la /app/installation_state/`
  - Should show `installed.lock` file
  - Check permissions: directory should be writable (777)

## Troubleshooting

### Backend Still Looping?

```bash
# Check exact exit point with set -x
docker compose logs backend | tail -100

# Run migration manually
docker compose run --rm backend python manage.py migrate

# Check Python syntax
docker compose run --rm backend python -m py_compile manage.py
```

### Frontend 502 Bad Gateway?

```bash
# Check if backend is responding
curl http://localhost/api/setup/status/

# Should return JSON, not connection refused
# If connection refused: backend not running or not on network
```

### Permission Denied on Lock File?

```bash
# Check volume permissions
docker compose exec backend ls -la /app/installation_state/

# Recreate volume with correct permissions
docker compose down
docker volume rm screengram_installation_state
docker compose up -d
```

## Testing Checklist

- [ ] `docker compose up -d` - All containers start
- [ ] `docker compose ps` - All show "Up" status
- [ ] `curl http://localhost/health` - Returns "healthy"
- [ ] `curl http://localhost/api/setup/status/` - Returns JSON
- [ ] Open browser to `http://localhost` - Shows app
- [ ] Complete installation wizard - No errors
- [ ] Restart: `docker compose restart backend` - Still works
- [ ] `docker compose exec backend ls /app/installation_state/installed.lock` - File exists

## Support

If issues persist after these fixes, run:

```bash
./diagnose.sh > diagnostic-output.txt
```

And share `diagnostic-output.txt` for further debugging.
