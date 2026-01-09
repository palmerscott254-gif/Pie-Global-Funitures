from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Debug storage configuration'

    def handle(self, *args, **options):
        self.stdout.write(f'USE_S3: {settings.USE_S3}')
        self.stdout.write(f'Has AWS_ACCESS_KEY_ID: {bool(settings.AWS_ACCESS_KEY_ID)}')
        self.stdout.write(f'Has AWS_SECRET_ACCESS_KEY: {bool(settings.AWS_SECRET_ACCESS_KEY)}')
        self.stdout.write(f'AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}')
        self.stdout.write(f'Storage Backend Default: {settings.STORAGES["default"]}')
        self.stdout.write(f'MEDIA_URL: {settings.MEDIA_URL}')
        
        # Check actual storage
        from django.core.files.storage import default_storage
        self.stdout.write(f'Actual default_storage class: {default_storage.__class__.__name__}')
        
        # Check example image
        from apps.home.models import SliderImage
        s = SliderImage.objects.first()
        if s and s.image:
            self.stdout.write(f'\nExample SliderImage:')
            self.stdout.write(f'  ID: {s.id}')
            self.stdout.write(f'  image.name: {s.image.name}')
            self.stdout.write(f'  image.url: {s.image.url}')
