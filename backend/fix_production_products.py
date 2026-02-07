#!/usr/bin/env python
"""
Script to fix production products by exporting local products
and providing commands to update production.
"""
import os
import django
import json
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pie_global.settings')
django.setup()

from apps.products.models import Product

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError

# Export all active products from local database
products = Product.objects.filter(is_active=True)
products_data = []

for product in products:
    products_data.append({
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'short_description': product.short_description,
        'price': str(product.price),
        'compare_at_price': str(product.compare_at_price) if product.compare_at_price else None,
        'category': product.category,
        'tags': product.tags,
        'main_image': str(product.main_image),
        'gallery': product.gallery,
        'stock': product.stock,
        'sku': product.sku,
        'dimensions': product.dimensions,
        'material': product.material,
        'color': product.color,
        'weight': product.weight,
        'featured': product.featured,
        'is_active': product.is_active,
        'on_sale': product.on_sale,
        'meta_title': product.meta_title,
        'meta_description': product.meta_description,
    })

# Save to JSON file
output_file = 'local_products_export.json'
with open(output_file, 'w') as f:
    json.dump(products_data, f, indent=2, default=decimal_default)

print(f"✅ Exported {len(products_data)} products to {output_file}")
print("\n" + "="*60)
print("NEXT STEPS TO FIX PRODUCTION:")
print("="*60)
print("\n1. Delete bad products from production database:")
print("   Go to: https://pie-global-funitures.onrender.com/admin/products/product/")
print("   - Login with your superuser credentials")
print("   - Filter by price <= 1.00 or manually select bad products")
print("   - Select all bad products and use 'Delete selected products' action")
print("\n2. Import your real products:")
print("   Option A - Via Django Admin (easiest):")
print("   - Manually add each product through the admin interface")
print("   - Copy data from local_products_export.json")
print("\n   Option B - Via Render Shell:")
print("   - Upload local_products_export.json to your Render service")
print("   - Run: python manage.py shell < import_products.py")
print("\n3. Or create products directly on production admin:")
print("   - Add products one by one through the admin interface")
print("   - Make sure to upload images and set correct prices")
