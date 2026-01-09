from django.conf import settings
print(f'USE_S3: {settings.USE_S3}')
print(f'Has AWS Access Key: {bool(settings.AWS_ACCESS_KEY_ID)}')
print(f'Has AWS Secret Key: {bool(settings.AWS_SECRET_ACCESS_KEY)}')
print(f'Storage Backend: {settings.STORAGES["default"]}')
from apps.home.models import SliderImage
s = SliderImage.objects.first()
if s and s.image:
    print(f'Example image.url: {s.image.url}')
    print(f'Example image.name: {s.image.name}')
