"""
Management command to initialize default About page.

Usage: python manage.py init_about_page
"""
from django.core.management.base import BaseCommand
from apps.about.models import AboutPage


class Command(BaseCommand):
    help = 'Initialize default About page if none exists'

    def handle(self, *args, **options):
        if AboutPage.objects.exists():
            self.stdout.write(
                self.style.SUCCESS('✓ About page already exists')
            )
            about = AboutPage.objects.first()
            self.stdout.write(f'  Headline: {about.headline}')
            return

        # Create default about page
        AboutPage.objects.create(
            headline='About Pie Global Furniture',
            body='Welcome to Pie Global Furniture. We provide quality furniture solutions for your home and office.',
            mission='To provide affordable, high-quality furniture that enhances lives.',
            vision='To be the leading furniture provider in East Africa.'
        )
        
        self.stdout.write(
            self.style.SUCCESS('✓ Default About page created successfully')
        )
