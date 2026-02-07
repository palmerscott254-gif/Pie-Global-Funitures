#!/usr/bin/env python
"""
Script to import products into production database.
Upload this file and local_products_export.json to Render, then run:
python manage.py shell < import_products.py
"""
import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
django.setup()

from apps.products.models import Product

# Read the exported products
with open('local_products_export.json', 'r') as f:
    products_data = json.load(f)

print(f"📦 Found {len(products_data)} products to import")

# First, delete bad products (price < 1)
bad_products = Product.objects.filter(price__lt=1)
bad_count = bad_products.count()
if bad_count > 0:
    print(f"🗑️  Deleting {bad_count} bad products...")
    bad_products.delete()

# Import products
created = 0
updated = 0

for data in products_data:
    # Convert price strings back to Decimal
    data['price'] = Decimal(data['price'])
    if data['compare_at_price']:
        data['compare_at_price'] = Decimal(data['compare_at_price'])
    
    # Try to find existing product by slug
    product, created_new = Product.objects.update_or_create(
        slug=data['slug'],
        defaults=data
    )
    
    if created_new:
        created += 1
        print(f"✅ Created: {product.name}")
    else:
        updated += 1
        print(f"♻️  Updated: {product.name}")

print("\n" + "="*60)
print(f"✅ Import complete!")
print(f"   Created: {created} products")
print(f"   Updated: {updated} products")
print("="*60)
