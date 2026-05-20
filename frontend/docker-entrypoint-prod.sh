#!/bin/sh
set -e
echo "[pixelcast] production: nginx on :80 (Traefik HTTPS :443 terminates SSL)"
exec nginx -g 'daemon off;'
