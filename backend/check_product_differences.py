#!/usr/bin/env python
"""
Check what's different between the 8 showing products and the 22 hidden ones.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pie_global.settings")
django.setup()

from apps.products.models import Product

# The 8 products from local_products_export.json
known_slugs = [
    'outdoor-set-up',
    'bed',
    'coffe-table',
    'wardrobs',
    'coffee-table-stools',
    'leather-office-chair',
    'office-chair',
    'coffee-table'
]

print("="*70)
print("ANALYZING PRODUCT DIFFERENCES")
print("="*70)

known_products = Product.objects.filter(slug__in=known_slugs)
other_products = Product.objects.exclude(slug__in=known_slugs)

print(f"\nKnown products (showing): {known_products.count()}")
print(f"Other products (hidden): {other_products.count()}")

print("\n" + "="*70)
print("FIELD COMPARISON")
print("="*70)

# Check one from each group
if known_products.exists() and other_products.exists():
    known = known_products.first()
    other = other_products.first()
    
    print(f"\nKNOWN PRODUCT: {known.name}")
    print(f"  Slug: {known.slug}")
    print(f"  Featured: {known.featured}")
    print(f"  Active: {known.is_active}")
    print(f"  On Sale: {known.on_sale}")
    print(f"  Price: {known.price}")
    print(f"  Short Desc: {known.short_description[:50] if known.short_description else 'EMPTY'}")
    print(f"  Description: {known.description[:50] if known.description else 'EMPTY'}")
    print(f"  Stock: {known.stock}")
    
    print(f"\nOTHER PRODUCT: {other.name}")
    print(f"  Slug: {other.slug}")
    print(f"  Featured: {other.featured}")
    print(f"  Active: {other.is_active}")
    print(f"  On Sale: {other.on_sale}")
    print(f"  Price: {other.price}")
    print(f"  Short Desc: {other.short_description[:50] if other.short_description else 'EMPTY'}")
    print(f"  Description: {other.description[:50] if other.description else 'EMPTY'}")
    print(f"  Stock: {other.stock}")

print("\n" + "="*70)
print("ALL OTHER PRODUCTS")
print("="*70)
for p in other_products.order_by('id'):
    print(f"ID {p.id}: {p.name} | Featured:{p.featured} | Active:{p.is_active} | Price:{p.price} | Stock:{p.stock}")
