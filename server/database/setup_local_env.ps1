# Local PostgreSQL Environment Setup Script
# Run this script before using database commands: . .\server\database\setup_local_env.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Local PostgreSQL Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Database Configuration
$env:POSTGRES_DB = "university_recommender"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres123"  # CHANGE THIS TO YOUR POSTGRESQL PASSWORD!
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/university_recommender"

Write-Host "Environment variables set:" -ForegroundColor Green
Write-Host "  POSTGRES_DB: $env:POSTGRES_DB" -ForegroundColor Yellow
Write-Host "  POSTGRES_USER: $env:POSTGRES_USER" -ForegroundColor Yellow
Write-Host "  POSTGRES_HOST: $env:POSTGRES_HOST" -ForegroundColor Yellow
Write-Host "  POSTGRES_PORT: $env:POSTGRES_PORT" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  IMPORTANT: Update POSTGRES_PASSWORD in this script!" -ForegroundColor Red
Write-Host "   Current password: $env:POSTGRES_PASSWORD" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing PostgreSQL connection..." -ForegroundColor Cyan

# Test connection
try {
    $testConn = psql -U postgres -d postgres -c "SELECT version();" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL connection successful!" -ForegroundColor Green
    } else {
        Write-Host "✗ PostgreSQL connection failed!" -ForegroundColor Red
        Write-Host "  Make sure PostgreSQL service is running:" -ForegroundColor Yellow
        Write-Host "    Get-Service postgresql*" -ForegroundColor Gray
        Write-Host "    Start-Service postgresql-x64-15" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ psql command not found!" -ForegroundColor Red
    Write-Host "  Add PostgreSQL bin to PATH:" -ForegroundColor Yellow
    Write-Host "    C:\Program Files\PostgreSQL\15\bin" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Ready to use database commands!" -ForegroundColor Green
Write-Host "  Example: python init_db.py" -ForegroundColor Gray

