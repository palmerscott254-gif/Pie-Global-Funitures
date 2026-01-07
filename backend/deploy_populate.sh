#!/bin/bash

# Deployment script for Render - Populates all data
echo "🚀 Starting Render deployment data population..."

# Run migrations first
echo "📦 Running migrations..."
python manage.py migrate

# Populate About page
echo "📝 Populating About page..."
python manage.py populate_about

# Populate media (sliders and videos)
echo "🖼️ Populating media..."
python manage.py populate_media

# Populate products
echo "🛋️ Populating products..."
python manage.py populate_products <<EOF
y
EOF

# Sync S3 records to database (if S3 is configured)
if [ "$USE_S3" = "True" ]; then
    echo "☁️ Syncing S3 media to database..."
    python manage.py sync_s3_to_db
fi

# Collect static files
echo "📂 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Deployment data population complete!"
