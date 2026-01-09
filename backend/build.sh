#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Clean up old media (delete all sliders, videos, product images)
echo "Cleaning up media files..."
python manage.py shell << 'CLEANUP_EOF'
from apps.home.models import SliderImage, HomeVideo
from apps.products.models import Product
SliderImage.objects.all().delete()
HomeVideo.objects.all().delete()
Product.objects.all().update(main_image='')
print("✓ All media records deleted")
CLEANUP_EOF

# Sync S3 files to database (if USE_S3 is enabled)
if [ "$USE_S3" = "True" ]; then
    echo "Syncing S3 files to database..."
    python manage.py sync_s3_to_db || echo "Sync skipped or failed"
fi

echo "Build complete - all data cleaned!"
