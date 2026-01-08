#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Populate initial data if database is empty
echo "Checking for initial data..."
python manage.py shell -c "
from apps.products.models import Product
from apps.home.models import SliderImage
from apps.about.models import AboutPage
if Product.objects.count() == 0:
    print('No products found, populating...')
    exit(1)
" || python manage.py populate_products <<EOF
y
EOF

python manage.py shell -c "
from apps.home.models import SliderImage
if SliderImage.objects.count() == 0:
    print('No sliders found, populating...')
    exit(1)
" || python manage.py populate_media

python manage.py shell -c "
from apps.about.models import AboutPage
if AboutPage.objects.count() == 0:
    print('No about page found, populating...')
    exit(1)
" || python manage.py populate_about

# Sync S3 files to database (if USE_S3 is enabled)
if [ "$USE_S3" = "True" ]; then
    echo "Syncing S3 files to database..."
    python manage.py sync_s3_to_db || echo "Sync skipped or failed"
fi

echo "Build complete - all data populated!"
