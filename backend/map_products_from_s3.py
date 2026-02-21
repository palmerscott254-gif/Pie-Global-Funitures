#!/usr/bin/env python
"""
Map real product details onto existing S3-created product records.

Matches by main_image path in local_products_export.json and updates fields.
Creates a product if no match is found.

Usage:
    python map_products_from_s3.py
"""
import os
import json
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pie_global.settings")
django.setup()

from apps.products.models import Product


def normalize_image_path(path: str) -> str:
    if not path:
        return ""
    path = str(path)
    return path[6:] if path.startswith("media/") else path


with open("local_products_export.json", "r") as f:
    products_data = json.load(f)

print(f"📦 Found {len(products_data)} products to map")

updated = 0
created = 0
slug_conflicts = 0

for data in products_data:
    # normalize and coerce fields
    main_image = normalize_image_path(data.get("main_image", ""))
    data["main_image"] = main_image

    data["price"] = Decimal(data["price"])
    compare_at = data.get("compare_at_price")
    data["compare_at_price"] = Decimal(compare_at) if compare_at else None

    # Ensure tags/gallery can be null
    if data.get("tags") == []:
        data["tags"] = []
    if data.get("gallery") == []:
        data["gallery"] = []

    # Try to match by image path
    product = None
    if main_image:
        product = Product.objects.filter(main_image=main_image).first()

    if product:
        desired_slug = data.get("slug") or ""
        if desired_slug:
            slug_taken = Product.objects.filter(slug=desired_slug).exclude(pk=product.pk).exists()
            if not slug_taken:
                product.slug = desired_slug
            else:
                slug_conflicts += 1

        for field, value in data.items():
            if field == "slug":
                continue
            setattr(product, field, value)
        product.save()
        updated += 1
    else:
        # Create new product (uses provided slug or auto-generated)
        Product.objects.create(**data)
        created += 1

print("\n" + "=" * 60)
print("✅ Mapping complete!")
print(f"   Updated: {updated} products")
print(f"   Created: {created} products")
if slug_conflicts:
    print(f"   Slug conflicts skipped: {slug_conflicts}")
print("=" * 60)
