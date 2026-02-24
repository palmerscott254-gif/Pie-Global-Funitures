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

# ============================================================================
# CRITICAL: Sync S3 and Make ALL Products Visible
# This ensures the website displays all 30 products, not just 8
# ============================================================================
if [ "$USE_S3" = "True" ] && [ -n "$AWS_ACCESS_KEY_ID" ] && [ -n "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "=========================================="
    echo "SYNCING S3 FILES TO DATABASE..."
    echo "=========================================="
    python manage.py sync_s3_to_db || echo "⚠️  S3 Sync failed"
    
    echo ""
    echo "=========================================="
    echo "IMPORTING REAL PRODUCT DATA..."
    echo "=========================================="
    python << 'EOF'
import os
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
import django
django.setup()

from apps.products.models import Product

imported = 0
try:
    if os.path.exists('products_full_export.json'):
        with open('products_full_export.json', 'r') as f:
            products_data = json.load(f)
        
        for data in products_data:
            data['price'] = Decimal(str(data['price']))
            if data.get('compare_at_price'):
                data['compare_at_price'] = Decimal(str(data['compare_at_price']))
            slug = data.pop('slug', None)
            product_id = data.pop('id', None)
            if slug:
                product, created = Product.objects.update_or_create(slug=slug, defaults=data)
                imported += 1
        
        print(f'✅ Imported real product data for {imported} products')
    else:
        print('⚠️  products_full_export.json not found')
except Exception as e:
    print(f'⚠️  Import error: {e}')
    import traceback
    traceback.print_exc()
EOF

    echo "=========================================="
    echo "MAKING ALL PRODUCTS VISIBLE..."
    echo "=========================================="
    python << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
import django
django.setup()

from apps.products.models import Product

total = Product.objects.count()
updated = 0
for p in Product.objects.all():
    changed = False
    if not p.is_active:
        p.is_active = True
        changed = True
    if not p.featured:
        p.featured = True
        changed = True
    if changed:
        p.save(update_fields=['is_active', 'featured'])
        updated += 1

featured = Product.objects.filter(featured=True).count()
active = Product.objects.filter(is_active=True).count()
print(f'✅ SUCCESS: All {total} products visible!')
print(f'   - Featured: {featured}/{total}')
print(f'   - Active: {active}/{total}')
print(f'🌐 Website: https://www.pieglobalfunitures.co.ke/products')
EOF
    
    echo "=========================================="
else
    echo "⚠️  Skipping S3 sync (USE_S3 disabled or AWS creds missing)"
fi

echo "Build complete!"
