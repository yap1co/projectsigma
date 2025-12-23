# Clean Next.js cache and restart
Write-Host "Cleaning Next.js cache..." -ForegroundColor Cyan

# Remove .next directory
if (Test-Path .next) {
    Remove-Item -Recurse -Force .next
    Write-Host "✓ Removed .next directory" -ForegroundColor Green
}

# Remove node_modules cache
if (Test-Path node_modules\.cache) {
    Remove-Item -Recurse -Force node_modules\.cache
    Write-Host "✓ Removed node_modules cache" -ForegroundColor Green
}

Write-Host "`nStarting Next.js dev server..." -ForegroundColor Cyan
npm run dev
