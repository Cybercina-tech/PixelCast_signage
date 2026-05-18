# Run backend pytest inside Docker (matches CI / Linux Python 3.12).
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")
docker compose exec -T -e PIXELCAST_SIGNAGE_INSTALLED=true backend python -m pytest tests/ @args
