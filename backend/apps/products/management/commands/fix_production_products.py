"""
Management command to fix production products
Run on Render: python manage.py fix_production_products
"""
from django.core.management.base import BaseCommand
from apps.products.models import Product
from decimal import Decimal


class Command(BaseCommand):
    help = 'Fix production products by deleting bad ones and adding real ones'

    def add_arguments(self, parser):
        parser.add_argument(
            '--safe-mode',
            action='store_true',
            help='Use get_or_create instead of update_or_create to preserve existing products',
        )

    def handle(self, *args, **options):
        safe_mode = options.get('safe_mode', False)
        
        # Delete bad products
        bad_products = Product.objects.filter(price__lt=1)
        bad_count = bad_products.count()
        
        if bad_count > 0:
            self.stdout.write(f"🗑️  Deleting {bad_count} bad products...")
            bad_products.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Deleted {bad_count} bad products"))
        else:
            self.stdout.write("ℹ️  No bad products found")
        
        # Your real products
        products = [
            {
                'name': 'OUTDOOR SET-UP',
                'slug': 'outdoor-set-up',
                'price': Decimal('23000.00'),
                'compare_at_price': Decimal('28000.00'),
                'category': 'outdoor',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20251218-WA0012.jpg',
                'stock': 100,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'Bed',
                'slug': 'bed',
                'price': Decimal('23000.00'),
                'compare_at_price': Decimal('26000.00'),
                'category': 'bed',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20260109-WA0006.jpg',
                'stock': 78,
                'featured': True,
                'is_active': True,
            },
            {
                'name': 'COFFE TABLE',
                'slug': 'coffe-table',
                'price': Decimal('12000.00'),
                'compare_at_price': Decimal('15000.00'),
                'category': 'table',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20260109-WA0003.jpg',
                'stock': 600,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'WARDROBS',
                'slug': 'wardrobs',
                'price': Decimal('23000.00'),
                'compare_at_price': Decimal('25000.00'),
                'category': 'wardrobe',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20251218-WA0004.jpg',
                'stock': 55,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'COFFEE TABLE STOOLS',
                'slug': 'coffee-table-stools',
                'price': Decimal('1500.00'),
                'compare_at_price': Decimal('2500.00'),
                'category': 'table',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20260109-WA0075.jpg',
                'stock': 100,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'LEATHER OFFICE CHAIR',
                'slug': 'leather-office-chair',
                'price': Decimal('17000.00'),
                'compare_at_price': Decimal('20000.00'),
                'category': 'office',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20251218-WA0001.jpg',
                'stock': 100,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'OFFICE CHAIR',
                'slug': 'office-chair',
                'price': Decimal('7500.00'),
                'compare_at_price': Decimal('12000.00'),
                'category': 'office',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20251218-WA0000.jpg',
                'stock': 120,
                'featured': True,
                'on_sale': True,
                'is_active': True,
            },
            {
                'name': 'COFFEE TABLE',
                'slug': 'coffee-table',
                'price': Decimal('12000.00'),
                'compare_at_price': Decimal('15000.00'),
                'category': 'table',
                'short_description': 'A stylish centerpiece',
                'main_image': 'products/main/IMG-20260109-WA0012.jpg',
                'stock': 10000,
                'featured': True,
                'is_active': True,
            },
        ]
        
        created = 0
        updated = 0
        skipped = 0
        
        for product_data in products:
            if safe_mode:
                # Safe mode: only create if doesn't exist, never update
                if Product.objects.filter(slug=product_data['slug']).exists():
                    skipped += 1
                    existing = Product.objects.get(slug=product_data['slug'])
                    self.stdout.write(self.style.WARNING(f"⏭️  Skipped (exists): {existing.name}"))
                    continue
                product = Product.objects.create(**product_data)
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {product.name}"))
            else:
                # Normal mode: create or update
                product, created_new = Product.objects.update_or_create(
                    slug=product_data['slug'],
                    defaults=product_data
                )
                
                if created_new:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Created: {product.name}"))
                else:
                    updated += 1
                    self.stdout.write(self.style.WARNING(f"♻️  Updated: {product.name}"))
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS(f"✅ Import complete!"))
        self.stdout.write(f"   Created: {created} products")
        if safe_mode:
            self.stdout.write(f"   Skipped: {skipped} products (already exist)")
        else:
            self.stdout.write(f"   Updated: {updated} products")
        self.stdout.write("="*60)
