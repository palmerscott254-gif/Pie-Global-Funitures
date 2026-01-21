from django.apps import AppConfig


class AboutConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about'

    def ready(self):
        """Initialize default about page when app starts."""
        from .models import AboutPage
        
        # Create default about page if none exist
        if not AboutPage.objects.exists():
            AboutPage.objects.create(
                headline='About Pie Global Furniture',
                body='Welcome to Pie Global Furniture. We provide quality furniture solutions for your home and office.',
                mission='To provide affordable, high-quality furniture that enhances lives.',
                vision='To be the leading furniture provider in East Africa.'
            )
