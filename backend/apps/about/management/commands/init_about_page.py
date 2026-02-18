"""
Management command to initialize default About page.

Usage: python manage.py init_about_page [--force-update]
"""
from django.core.management.base import BaseCommand
from apps.about.models import AboutPage


class Command(BaseCommand):
    help = 'Initialize default About page if none exists'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Update existing About page with default content (WARNING: overwrites existing data)',
        )

    def handle(self, *args, **options):
        force_update = options.get('force_update', False)
        
        if AboutPage.objects.exists():
            if not force_update:
                self.stdout.write(
                    self.style.SUCCESS('✓ About page already exists (use --force-update to overwrite)')
                )
                about = AboutPage.objects.first()
                self.stdout.write(f'  Headline: {about.headline}')
                return
            else:
                # Update existing
                about = AboutPage.objects.first()
                about.headline = 'About Pie Global Furniture'
                about.body = 'Welcome to Pie Global Furniture. We provide quality furniture solutions for your home and office.'
                about.mission = 'To provide affordable, high-quality furniture that enhances lives.'
                about.vision = 'To be the leading furniture provider in East Africa.'
                about.save()
                self.stdout.write(
                    self.style.WARNING('⚠️  About page updated with default content')
                )
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
