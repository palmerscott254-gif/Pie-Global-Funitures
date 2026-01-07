"""
Management command to populate sample media data (sliders, videos).
This command creates sample SliderImage and HomeVideo entries with placeholder data.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.home.models import SliderImage, HomeVideo


class Command(BaseCommand):
    help = 'Populate sample media data for homepage sliders and videos'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Starting media population...")
        
        # Clear existing data
        SliderImage.objects.all().delete()
        HomeVideo.objects.all().delete()
        
        # Create slider images
        sliders = [
            {
                "title": "Premium Sofas Collection",
                "image": "home/sliders/sofa-1.jpg",
                "order": 1,
            },
            {
                "title": "Modern Bedroom Sets",
                "image": "home/sliders/bedroom-1.jpg",
                "order": 2,
            },
            {
                "title": "Elegant Dining Tables",
                "image": "home/sliders/dining-1.jpg",
                "order": 3,
            },
            {
                "title": "Office Furniture Solutions",
                "image": "home/sliders/office-1.jpg",
                "order": 4,
            },
        ]
        
        for slider_data in sliders:
            slider = SliderImage.objects.create(
                title=slider_data["title"],
                image=slider_data["image"],
                order=slider_data["order"],
                active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created slider: {slider.title}"))
        
        # Create videos
        videos = [
            {
                "title": "Showroom Tour",
                "video": "home/videos/showroom-tour.mp4",
            },
            {
                "title": "Product Highlights",
                "video": "home/videos/product-highlights.mp4",
            },
        ]
        
        for video_data in videos:
            video = HomeVideo.objects.create(
                title=video_data["title"],
                video=video_data["video"],
                active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created video: {video.title}"))
        
        self.stdout.write(self.style.SUCCESS("✅ Media population complete!"))
