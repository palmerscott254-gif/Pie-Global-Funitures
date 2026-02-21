#!/usr/bin/env python
"""
Complete diagnostic and verification script.
Run this to confirm all products are properly configured.
"""
import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pie_global.settings")
django.setup()

from apps.products.models import Product

print("\n" + "="*70)
print(" COMPLETE PRODUCT DATABASE DIAGNOSTIC ")
print("="*70)

# 1. Total count
all_products = Product.objects.all()
print(f"\n📊 TOTAL PRODUCTS: {all_products.count()}")

# 2. Status breakdown
active_count = Product.objects.filter(is_active=True).count()
inactive_count = Product.objects.filter(is_active=False).count()
featured_count = Product.objects.filter(featured=True).count()
not_featured_count = Product.objects.filter(featured=False).count()
on_sale_count = Product.objects.filter(on_sale=True).count()

print(f"\n✅ ACTIVE STATUS:")
print(f"   Active: {active_count}")
print(f"   Inactive: {inactive_count}")

print(f"\n⭐ FEATURED STATUS:")
print(f"   Featured: {featured_count}")
print(f"   Not Featured: {not_featured_count}")

print(f"\n💰 SALE STATUS:")
print(f"   On Sale: {on_sale_count}")

# 3. Category breakdown
print(f"\n📁 BY CATEGORY:")
for category, category_name in Product.CATEGORY_CHOICES:
    count = Product.objects.filter(category=category).count()
    if count > 0:
        print(f"   {category_name}: {count}")

# 4. Price check
print(f"\n💵 PRICE CHECK:")
low_price = Product.objects.filter(price__lt=Decimal('100')).count()
no_price = Product.objects.filter(price=Decimal('0')).count()
if low_price > 0:
    print(f"   ⚠️  {low_price} products with price < KSh 100")
    for p in Product.objects.filter(price__lt=Decimal('100')):
        print(f"      - {p.name}: KSh {p.price}")
else:
    print(f"   ✓ All products have realistic prices")

if no_price > 0:
    print(f"   ⚠️  {no_price} products with zero price")
else:
    print(f"   ✓ No products with zero price")

# 5. Image check
print(f"\n🖼️  IMAGE CHECK:")
with_images = Product.objects.exclude(main_image='').count()
without_images = Product.objects.filter(main_image='').count()
print(f"   With images: {with_images}")
if without_images > 0:
    print(f"   ⚠️  Without images: {without_images}")
else:
    print(f"   ✓ All products have images")

# 6. Stock check
print(f"\n📦 STOCK CHECK:")
in_stock = Product.objects.filter(stock__gt=0).count()
out_of_stock = Product.objects.filter(stock=0).count()
print(f"   In stock: {in_stock}")
if out_of_stock > 0:
    print(f"   Out of stock: {out_of_stock}")
else:
    print(f"   ✓ All products in stock")

# 7. Issues
print(f"\n🔍 POTENTIAL ISSUES:")
issues = []

# Check for inactive products
if inactive_count > 0:
    issues.append(f"{inactive_count} products are INACTIVE (won't show on website)")

# Check for non-featured products
if not_featured_count > 0:
    issues.append(f"{not_featured_count} products are NOT FEATURED")

# Check for missing images
if without_images > 0:
    issues.append(f"{without_images} products have NO IMAGES")

# Check for out of stock
if out_of_stock > 0:
    issues.append(f"{out_of_stock} products are OUT OF STOCK")

if issues:
    for issue in issues:
        print(f"   ⚠️  {issue}")
else:
    print(f"   ✓ No issues detected!")

# 8. Final verdict
print(f"\n" + "="*70)
if all_products.count() == 30 and active_count == 30 and featured_count == 30 and with_images == 30:
    print(" 🎉 SUCCESS! ALL 30 PRODUCTS ARE PROPERLY CONFIGURED! ")
    print(f"    ✓ All products are ACTIVE")
    print(f"    ✓ All products are FEATURED")
    print(f"    ✓ All products have IMAGES")
    print(f"\n 🌐 Website will display all {all_products.count()} products correctly!")
elif all_products.count() < 30:
    print(" ⚠️  WARNING: Expected 30 products, found {all_products.count()}")
    print("    Run: python manage.py sync_s3_to_db")
else:
    print(f" ⚠️  ATTENTION: {all_products.count()} products exist, but some may not display")
    if inactive_count > 0:
        print(f"    → {inactive_count} products are INACTIVE")
    if not_featured_count > 0:
        print(f"    → {not_featured_count} products are NOT FEATURED")
    if without_images > 0:
        print(f"    → {without_images} products have NO IMAGES")
    print(f"\n    Fix: Run python ensure_all_products_visible.py")

print("="*70 + "\n")
