# Deployment Data Population Script for Render
# Run this in the Render Shell to populate all initial data

Write-Host "🚀 Starting Render deployment data population..." -ForegroundColor Cyan

# Run migrations first
Write-Host "📦 Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Populate About page
Write-Host "📝 Populating About page..." -ForegroundColor Yellow
python manage.py populate_about

# Populate media (sliders and videos)
Write-Host "🖼️ Populating media..." -ForegroundColor Yellow
python manage.py populate_media

# Populate products (auto-confirm with 'y')
Write-Host "🛋️ Populating products..." -ForegroundColor Yellow
echo "y" | python manage.py populate_products

# Sync S3 records to database (if S3 is configured)
if ($env:USE_S3 -eq "True") {
    Write-Host "☁️ Syncing S3 media to database..." -ForegroundColor Yellow
    python manage.py sync_s3_to_db
}

# Collect static files
Write-Host "📂 Collecting static files..." -ForegroundColor Yellow
python manage.py collectstatic --noinput

Write-Host "✅ Deployment data population complete!" -ForegroundColor Green
