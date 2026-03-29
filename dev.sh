#!/bin/bash
# Start PixelCast Signage with hot-reloading frontend (Vite dev server)
# Edit Vue files - changes appear instantly at http://localhost:5173

set -e

echo "Starting PixelCast Signage (dev mode with HMR)..."
echo "Frontend: http://localhost:5173"
echo ""

# Use dev override: excludes production frontend, uses frontend-dev
docker compose -f docker-compose.yml -f docker-compose.dev.yml up "$@"
