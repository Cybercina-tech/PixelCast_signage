#!/bin/sh
# Sync container node_modules with package-lock.json. The compose file uses a
# named volume for /app/node_modules so it survives rebuilds; without this,
# adding packages on the host leaves the volume stale and Vite cannot resolve
# new imports (e.g. @fontsource/*).
set -e
cd /app

LOCK_FILE=package-lock.json
STAMP_FILE=node_modules/.install-stamp

if [ ! -f "$LOCK_FILE" ]; then
  echo "docker-entrypoint-dev: $LOCK_FILE not found" >&2
  exit 1
fi

# Busybox (Alpine) provides sha256sum
LOCK_HASH=$(sha256sum "$LOCK_FILE" | awk '{print $1}')

if [ ! -f "$STAMP_FILE" ] || [ "$(cat "$STAMP_FILE" 2>/dev/null)" != "$LOCK_HASH" ]; then
  echo "docker-entrypoint-dev: installing dependencies (lockfile new or changed)..."
  npm ci
  mkdir -p node_modules
  printf '%s\n' "$LOCK_HASH" > "$STAMP_FILE"
fi

exec "$@"
