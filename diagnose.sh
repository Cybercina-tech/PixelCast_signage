#!/bin/bash

# Diagnostic script to check Docker stack health
# Run: ./diagnose.sh

set -e

echo "=================================="
echo "ScreenGram Docker Stack Diagnostics"
echo "=================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi
echo "✅ Docker is running"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.example"
    exit 1
fi
echo "✅ .env file exists"

# Check for required env vars
if ! grep -q "^DB_PASSWORD=.\+" .env 2>/dev/null; then
    echo "⚠️  DB_PASSWORD not set in .env"
fi

if ! grep -q "^SECRET_KEY=.\+" .env 2>/dev/null; then
    echo "⚠️  SECRET_KEY not set in .env"
fi

echo ""
echo "--- Container Status ---"
docker compose ps

echo ""
echo "--- Network Status ---"
docker network inspect screengram-net --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' 2>/dev/null || echo "Network not found"

echo ""
echo "--- Volume Status ---"
docker volume ls | grep screengram

echo ""
echo "--- Backend Logs (last 50 lines) ---"
docker compose logs --tail=50 backend 2>/dev/null || echo "Backend not running"

echo ""
echo "--- Frontend Logs (last 30 lines) ---"
docker compose logs --tail=30 frontend 2>/dev/null || echo "Frontend not running"

echo ""
echo "--- Database Health ---"
docker compose exec -T db pg_isready -U screengram_user 2>/dev/null && echo "✅ Database is ready" || echo "❌ Database not ready"

echo ""
echo "--- Installation Lock Status ---"
docker compose exec -T backend ls -la /app/installation_state/ 2>/dev/null || echo "Installation state directory not found"

echo ""
echo "=================================="
echo "Manual Commands to Try:"
echo "=================================="
echo ""
echo "1. Test backend database connection:"
echo "   docker compose run --rm backend python manage.py migrate --check"
echo ""
echo "2. View live backend logs:"
echo "   docker compose logs -f backend"
echo ""
echo "3. Access backend shell:"
echo "   docker compose exec backend bash"
echo ""
echo "4. Test backend API:"
echo "   curl http://localhost/api/setup/status/"
echo ""
echo "5. Restart everything cleanly:"
echo "   docker compose down && docker compose up -d"
echo ""
echo "6. Remove volumes and start fresh:"
echo "   docker compose down -v && docker compose up -d"
echo ""
