#!/bin/bash
# 
# Complete deployment script for Render
# This will sync all 30 products from S3 to the Render database
#
# INSTRUCTIONS TO RUN ON RENDER:
# 1. Go to: https://dashboard.render.com
# 2. Find your backend service: pie-global-funitures
# 3. Click "Shell" tab
# 4. Paste and run each command below:

echo "🚀 Starting product sync on Render..."

# Step 1: Sync S3 files to database (creates 30 products with S3 images)
echo "📦 Step 1: Syncing S3 images to database..."
python manage.py sync_s3_to_db

# Step 2: Make all products active and featured
echo "✨ Step 2: Making all products visible..."
python -c "
import django
django.setup()
from apps.products.models import Product

all_products = Product.objects.all()
print(f'Total products: {all_products.count()}')

for product in all_products:
    product.is_active = True
    product.featured = True
    product.save()
    
print(f'✅ All {all_products.count()} products are now active and featured')
"

echo "✅ Deployment complete!"
echo "🌐 Check your website: https://www.pieglobalfunitures.co.ke/products"
