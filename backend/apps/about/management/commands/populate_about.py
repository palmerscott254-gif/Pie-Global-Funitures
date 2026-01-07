"""
Management command to populate the About page content.
"""

from django.core.management.base import BaseCommand
from apps.about.models import AboutPage


class Command(BaseCommand):
    help = 'Populate the About page with default content'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting About page population...")
        
        # Clear existing about pages (keep only one)
        AboutPage.objects.all().delete()
        
        about_content = AboutPage.objects.create(
            headline="Welcome to Pie Global Funitures",
            body="""
At Pie Global Funitures, we believe that your living space should reflect your personality and lifestyle. 
With over 15 years of experience in the furniture industry, we've become a trusted name in providing 
high-quality, stylish, and affordable furniture solutions for homes and businesses across East Africa.

Our extensive collection ranges from contemporary designs to classic pieces, all carefully curated to meet 
the diverse tastes and budgets of our customers. Whether you're furnishing a cozy apartment, a spacious 
family home, or a professional office, we have something special for you.

We work directly with manufacturers and suppliers to ensure the best prices without compromising on quality. 
Every piece in our collection undergoes rigorous quality checks to guarantee durability and elegance.
            """,
            mission="""
Our mission is to make premium furniture accessible to everyone. We are committed to:
• Providing exceptional quality furniture at competitive prices
• Delivering outstanding customer service and support
• Offering a seamless shopping experience both online and in-store
• Continuously innovating and updating our collections with latest trends
• Supporting sustainable and ethical manufacturing practices
            """,
            vision="""
We envision Pie Global Funitures as the leading furniture destination in East Africa, known for:
• Innovation and design excellence
• Customer satisfaction and loyalty
• Environmental responsibility
• Community engagement and social impact
• Setting industry standards for quality and service
            """
        )
        
        self.stdout.write(self.style.SUCCESS(f"✓ Created About page with headline: {about_content.headline}"))
        self.stdout.write(self.style.SUCCESS("✅ About page population complete!"))
