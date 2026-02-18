"""
Management command to mark all real products as featured and active
"""
from django.core.management.base import BaseCommand
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Mark all real products as featured and active'

    def handle(self, *args, **options):
        # Update all products with price >= 1 to be featured and active
        updated = Product.objects.filter(price__gte=1).update(
            featured=True,
            is_active=True
        )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Updated {updated} products to featured=True, is_active=True'))
        
        # Show summary
        total = Product.objects.count()
        featured = Product.objects.filter(featured=True).count()
        active = Product.objects.filter(is_active=True).count()
        
        self.stdout.write(f'\nSummary:')
        self.stdout.write(f'  Total products: {total}')
        self.stdout.write(f'  Featured products: {featured}')
        self.stdout.write(f'  Active products: {active}')
