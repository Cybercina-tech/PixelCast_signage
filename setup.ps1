# ScreenGram - Fix & Setup Script (Windows PowerShell)
# Run from project root: .\setup.ps1

$ErrorActionPreference = "Stop"

Write-Host "Starting ScreenGram Fix & Setup..." -ForegroundColor Cyan

# 1. Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Write-Host "Creating .env from env.example..." -ForegroundColor Yellow
        Copy-Item "env.example" ".env"
        Write-Host "Please edit .env and set DB_PASSWORD and SECRET_KEY before running again." -ForegroundColor Yellow
        exit 1
    } else {
        Write-Host "Creating minimal .env..." -ForegroundColor Yellow
        $secretKey = -join ((1..32) | ForEach-Object { "{0:x2}" -f (Get-Random -Maximum 256) })
        @"
DB_PASSWORD=change-me-please
SECRET_KEY=$secretKey
DB_NAME=screengram_db
DB_USER=screengram_user
"@ | Out-File -FilePath ".env" -Encoding utf8
        Write-Host "Please edit .env and set a secure DB_PASSWORD before running again." -ForegroundColor Yellow
        exit 1
    }
}

# 2. Add SECRET_KEY if missing
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "SECRET_KEY=.+") {
    $secretKey = -join ((1..32) | ForEach-Object { "{0:x2}" -f (Get-Random -Maximum 256) })
    Add-Content ".env" "SECRET_KEY=$secretKey"
    Write-Host "Added SECRET_KEY to .env" -ForegroundColor Green
}

# 3. Verify LogsReports.vue exists
$filePath = "FrontEnd\src\pages\logs\LogsReports.vue"
if (-not (Test-Path $filePath)) {
    Write-Host "Error: $filePath not found!" -ForegroundColor Red
    Get-ChildItem -Path "FrontEnd" -Recurse -Filter "*.vue" | Select-Object -First 20 | ForEach-Object { $_.FullName }
    exit 1
}
Write-Host "LogsReports.vue found" -ForegroundColor Green

# 4. Clean Docker
Write-Host "Cleaning up old Docker images and cache..." -ForegroundColor Yellow
docker compose down 2>$null
docker system prune -f 2>$null

# 5. Build
Write-Host "Building containers..." -ForegroundColor Yellow
docker compose build --no-cache

# 6. Start
Write-Host "Starting ScreenGram..." -ForegroundColor Yellow
docker compose up -d

Write-Host "Done! Use 'docker compose logs -f' to see the logs." -ForegroundColor Green
Write-Host "Frontend: http://localhost (or FRONTEND_PORT from .env)" -ForegroundColor Cyan
