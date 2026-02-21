#!/usr/bin/env python
"""
IMMEDIATE FIX for Render Shell - Run this NOW to show all 30 products

Paste this entire script into Render Shell or run:
python fix_render_products_now.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pie_global.settings")
django.setup()

from apps.products.models import Product

print("\n" + "="*70)
print(" IMMEDIATE PRODUCT VISIBILITY FIX FOR RENDER ")
print("="*70)

# Step 1: Check current status
total = Product.objects.count()
print(f"\n📊 Current products in database: {total}")

if total < 30:
    print(f"\n⚠️  Only {total} products found!")
    print("   You need to run: python manage.py sync_s3_to_db first")
    print("   Then run this script again.")
    exit(1)

# Step 2: Make ALL products visible
print(f"\n✨ Making all {total} products visible...")

updated = 0
for product in Product.objects.all():
    changed = False
    
    if not product.is_active:
        product.is_active = True
        changed = True
    
    if not product.featured:
        product.featured = True
        changed = True
    
    if changed:
        product.save(update_fields=['is_active', 'featured'])
        updated += 1

print(f"   ✅ Updated {updated} products")

# Step 3: Verify
featured = Product.objects.filter(featured=True).count()
active = Product.objects.filter(is_active=True).count()

print(f"\n📊 VERIFICATION:")
print(f"   Total products: {total}")
print(f"   Featured: {featured}")
print(f"   Active: {active}")

if featured == total and active == total:
    print(f"\n🎉 SUCCESS! All {total} products are now visible!")
    print(f"\n🌐 Check your website:")
    print(f"   https://www.pieglobalfunitures.co.ke/products")
    print(f"\n   You should now see {total} products instead of 8!")
else:
    print(f"\n⚠️  Warning: Some products may still not be visible")

print("="*70 + "\n")
