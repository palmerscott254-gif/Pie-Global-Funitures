#!/usr/bin/env python
"""
Complete solution to ensure all products are visible.
Run this after sync_s3_to_db to make all products active and featured.

Usage on Render Shell:
    python ensure_all_products_visible.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pie_global.settings")
django.setup()

from apps.products.models import Product

print("="*60)
print("ENSURING ALL PRODUCTS ARE VISIBLE")
print("="*60)

# Get all products
all_products = Product.objects.all()
print(f"\nTotal products in database: {all_products.count()}")

if all_products.count() == 0:
    print("\n⚠️  No products found! Run 'python manage.py sync_s3_to_db' first.")
    exit(1)

# Update all products to be active and featured
updated_count = 0
for product in all_products:
    changed = False
    
    if not product.is_active:
        product.is_active = True
        changed = True
    
    if not product.featured:
        product.featured = True
        changed = True
    
    # Ensure minimum price
    if product.price < 100:
        print(f"⚠️  Warning: {product.name} has very low price: KSh {product.price}")
    
    if changed:
        product.save(update_fields=['is_active', 'featured'])
        updated_count += 1

print(f"\n{'='*60}")
print(f"✅ UPDATE COMPLETE!")
print(f"   Total products: {all_products.count()}")
print(f"   Updated: {updated_count} products")
print(f"   All products are now ACTIVE and FEATURED")
print(f"{'='*60}")

# Verify the fix
featured_count = Product.objects.filter(featured=True).count()
active_count = Product.objects.filter(is_active=True).count()

print(f"\n📊 VERIFICATION:")
print(f"   ✓ Featured products: {featured_count}/{all_products.count()}")
print(f"   ✓ Active products: {active_count}/{all_products.count()}")

if featured_count == all_products.count() and active_count == all_products.count():
    print(f"\n🎉 SUCCESS! All {all_products.count()} products will now display on the website!")
else:
    print(f"\n⚠️  Warning: Some products may not be visible")

print("\n🌐 Visit your website to verify:")
print("   https://www.pieglobalfunitures.co.ke/products")
print("="*60)
