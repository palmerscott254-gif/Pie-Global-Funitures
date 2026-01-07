"""
Management command to populate sample product data.
Creates diverse furniture products across all categories.
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.products.models import Product


class Command(BaseCommand):
    help = 'Populate sample product data'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting product population...")
        
        # Only clear products if table is empty to avoid data loss
        if Product.objects.exists():
            response = input("⚠️  Products already exist. Clear them? (y/n): ")
            if response.lower() == 'y':
                Product.objects.all().delete()
            else:
                self.stdout.write("Skipping population.")
                return
        
        products = [
            # Sofas
            {
                "name": "Premium Leather Sofa",
                "category": "sofa",
                "price": Decimal("45000"),
                "compare_at_price": Decimal("55000"),
                "description": "Luxurious full-grain leather sofa with deep seating comfort",
                "short_description": "Premium leather seating for your living room",
                "main_image": "products/main/sofa-leather.jpg",
                "stock": 8,
                "sku": "SOFA-LTH-001",
                "material": "Full-grain leather",
                "color": "Black",
                "dimensions": "250x100x85 cm",
                "weight": "120 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Contemporary Fabric Sofa",
                "category": "sofa",
                "price": Decimal("28000"),
                "compare_at_price": Decimal("35000"),
                "description": "Modern fabric sofa with clean lines and minimalist design",
                "short_description": "Stylish modern sofa in neutral tones",
                "main_image": "products/main/sofa-fabric.jpg",
                "stock": 12,
                "sku": "SOFA-FAB-001",
                "material": "Premium fabric",
                "color": "Grey",
                "dimensions": "220x90x80 cm",
                "weight": "95 kg",
                "featured": True,
                "is_active": True,
            },
            
            # Beds
            {
                "name": "King Size Platform Bed",
                "category": "bed",
                "price": Decimal("35000"),
                "compare_at_price": Decimal("42000"),
                "description": "Sturdy king-size platform bed with integrated storage",
                "short_description": "Spacious platform bed for ultimate comfort",
                "main_image": "products/main/bed-platform.jpg",
                "stock": 6,
                "sku": "BED-KNG-001",
                "material": "Solid wood with upholstery",
                "color": "Walnut brown",
                "dimensions": "200x150x40 cm",
                "weight": "110 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Queen Size Upholstered Bed",
                "category": "bed",
                "price": Decimal("28000"),
                "compare_at_price": Decimal("34000"),
                "description": "Elegant queen-size bed with soft upholstered headboard",
                "short_description": "Classic queen bed with modern comfort",
                "main_image": "products/main/bed-queen.jpg",
                "stock": 10,
                "sku": "BED-QN-001",
                "material": "Wood with fabric upholstery",
                "color": "Cream",
                "dimensions": "160x200x100 cm",
                "weight": "85 kg",
                "featured": False,
                "is_active": True,
            },
            
            # Tables
            {
                "name": "Glass Dining Table",
                "category": "table",
                "price": Decimal("22000"),
                "compare_at_price": Decimal("28000"),
                "description": "Modern glass-top dining table with sturdy metal base",
                "short_description": "Contemporary dining table for 6-8 people",
                "main_image": "products/main/table-dining.jpg",
                "stock": 7,
                "sku": "TBL-DIN-001",
                "material": "Tempered glass and steel",
                "color": "Black/Clear",
                "dimensions": "180x90x75 cm",
                "weight": "75 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Coffee Table Marble",
                "category": "table",
                "price": Decimal("12000"),
                "compare_at_price": Decimal("15000"),
                "description": "Elegant marble coffee table with gold accents",
                "short_description": "Premium coffee table for living spaces",
                "main_image": "products/main/table-coffee.jpg",
                "stock": 15,
                "sku": "TBL-COF-001",
                "material": "Marble and brass",
                "color": "White/Gold",
                "dimensions": "120x60x45 cm",
                "weight": "45 kg",
                "featured": False,
                "is_active": True,
            },
            
            # Wardrobes
            {
                "name": "5-Door Wardrobe",
                "category": "wardrobe",
                "price": Decimal("32000"),
                "compare_at_price": Decimal("40000"),
                "description": "Spacious 5-door wardrobe with mirror and drawers",
                "short_description": "Complete storage solution for bedrooms",
                "main_image": "products/main/wardrobe-5door.jpg",
                "stock": 5,
                "sku": "WRD-5DR-001",
                "material": "MDF wood",
                "color": "Walnut",
                "dimensions": "250x60x200 cm",
                "weight": "150 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Sliding Door Wardrobe",
                "category": "wardrobe",
                "price": Decimal("28000"),
                "compare_at_price": Decimal("35000"),
                "description": "Modern sliding door wardrobe with LED lighting",
                "short_description": "Space-saving wardrobe with modern design",
                "main_image": "products/main/wardrobe-slide.jpg",
                "stock": 8,
                "sku": "WRD-SLD-001",
                "material": "Plywood and laminate",
                "color": "White",
                "dimensions": "220x60x200 cm",
                "weight": "120 kg",
                "featured": False,
                "is_active": True,
            },
            
            # Office Furniture
            {
                "name": "Executive Desk",
                "category": "office",
                "price": Decimal("18000"),
                "compare_at_price": Decimal("24000"),
                "description": "Professional executive desk with storage compartments",
                "short_description": "Premium office desk for professionals",
                "main_image": "products/main/desk-executive.jpg",
                "stock": 6,
                "sku": "OFF-DSK-001",
                "material": "Solid wood and steel",
                "color": "Dark brown",
                "dimensions": "160x80x75 cm",
                "weight": "70 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Office Chair - Ergonomic",
                "category": "office",
                "price": Decimal("8500"),
                "compare_at_price": Decimal("11000"),
                "description": "Ergonomic office chair with lumbar support",
                "short_description": "Comfortable seating for long work hours",
                "main_image": "products/main/chair-office.jpg",
                "stock": 20,
                "sku": "OFF-CHR-001",
                "material": "Mesh and metal",
                "color": "Black",
                "dimensions": "70x70x100-110 cm",
                "weight": "25 kg",
                "featured": False,
                "is_active": True,
            },
            
            # Dining
            {
                "name": "Wooden Dining Set",
                "category": "dining",
                "price": Decimal("35000"),
                "compare_at_price": Decimal("45000"),
                "description": "Complete dining set with table and 6 chairs",
                "short_description": "Full dining solution for family meals",
                "main_image": "products/main/dining-set.jpg",
                "stock": 4,
                "sku": "DIN-SET-001",
                "material": "Solid wood",
                "color": "Mahogany",
                "dimensions": "180x90x75 cm",
                "weight": "180 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Bar Stools Set",
                "category": "dining",
                "price": Decimal("6500"),
                "compare_at_price": Decimal("8000"),
                "description": "Set of 3 adjustable bar stools with footrest",
                "short_description": "Modern bar seating for kitchen islands",
                "main_image": "products/main/barstools.jpg",
                "stock": 18,
                "sku": "DIN-BST-001",
                "material": "Metal and leather",
                "color": "Black",
                "dimensions": "40x40x65-75 cm",
                "weight": "8 kg each",
                "featured": False,
                "is_active": True,
            },
            
            # Outdoor
            {
                "name": "Patio Furniture Set",
                "category": "outdoor",
                "price": Decimal("25000"),
                "compare_at_price": Decimal("32000"),
                "description": "Weather-resistant outdoor furniture set",
                "short_description": "Durable seating for patios and gardens",
                "main_image": "products/main/patio-set.jpg",
                "stock": 5,
                "sku": "OUT-PAT-001",
                "material": "Aluminum and waterproof fabric",
                "color": "Grey/Beige",
                "dimensions": "200x150x80 cm",
                "weight": "60 kg",
                "featured": True,
                "is_active": True,
            },
            {
                "name": "Garden Bench",
                "category": "outdoor",
                "price": Decimal("9500"),
                "compare_at_price": Decimal("12000"),
                "description": "Teak wood garden bench with classic design",
                "short_description": "Elegant outdoor seating for gardens",
                "main_image": "products/main/garden-bench.jpg",
                "stock": 9,
                "sku": "OUT-BNC-001",
                "material": "Teak wood",
                "color": "Natural",
                "dimensions": "150x60x75 cm",
                "weight": "35 kg",
                "featured": False,
                "is_active": True,
            },
            
            # Storage
            {
                "name": "Storage Cabinet",
                "category": "storage",
                "price": Decimal("14000"),
                "compare_at_price": Decimal("18000"),
                "description": "Multi-compartment storage cabinet with shelves",
                "short_description": "Versatile storage for any room",
                "main_image": "products/main/storage-cabinet.jpg",
                "stock": 11,
                "sku": "STR-CAB-001",
                "material": "Engineered wood",
                "color": "White",
                "dimensions": "120x40x180 cm",
                "weight": "55 kg",
                "featured": False,
                "is_active": True,
            },
        ]
        
        created_count = 0
        for product_data in products:
            product = Product.objects.create(**product_data)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"✓ Created product: {product.name}"))
        
        self.stdout.write(self.style.SUCCESS(f"✅ Created {created_count} products!"))
