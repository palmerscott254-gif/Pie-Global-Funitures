#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Initialize default about page (safe to run multiple times)
python manage.py init_about_page

# Import media records from JSON (if present)
# Always use --skip-duplicates to prevent re-importing on every build
if [ -f "media_records.json" ]; then
    echo "Importing media records from media_records.json..."
    python manage.py import_media --input media_records.json --skip-duplicates
else
    echo "No media_records.json found (skipping import)"
fi

# Populate real products (safe - uses get_or_create, won't overwrite existing)
echo "Ensuring real products exist..."
python manage.py ensure_products || echo "Product creation skipped or failed"

# Sync S3 files to database (only if enabled AND creds exist)
# Note: This only updates empty product records, doesn't create new ones
if [ "$USE_S3" = "True" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Syncing S3 files to database..."
    python manage.py sync_s3_to_db || echo "Sync skipped or failed"
else
    echo "Skipping S3 sync (USE_S3 disabled or AWS creds missing)"
fi

echo "Build complete!"
