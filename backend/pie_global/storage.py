"""Custom S3 Storage Backend Configuration.

Provides `S3MediaStorage` and `S3StaticStorage` backed by
`storages.backends.s3boto3.S3Boto3Storage` when available. If the
`django-storages` package is absent or corrupted, fall back to
Django's `FileSystemStorage` so local development continues to work.
"""
from django.conf import settings

try:
    from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore
    HAS_S3 = True
except Exception:
    from django.core.files.storage import FileSystemStorage as S3Boto3Storage  # type: ignore
    HAS_S3 = False


class S3MediaStorage(S3Boto3Storage):
    """Storage for media files.
    
    For S3Boto3Storage: location='media' tells S3 to prefix all keys with 'media/'.
    For FileSystemStorage: we must explicitly set location='' to avoid /media/media/ double paths.
    """
    default_acl = None
    file_overwrite = False
    
    def __init__(self, *args, **kwargs):
        if HAS_S3:
            # S3: prefix all keys with 'media/'
            kwargs.setdefault('location', 'media')
        else:
            # FileSystemStorage: no location prefix (files go to MEDIA_ROOT directly)
            kwargs['location'] = ''
        super().__init__(*args, **kwargs)


class S3StaticStorage(S3Boto3Storage):
    """Storage for static files.
    
    For S3Boto3Storage: location='static' tells S3 to prefix all keys with 'static/'.
    For FileSystemStorage: location='' to store directly in staticfiles root.
    """
    default_acl = None
    file_overwrite = True
    
    def __init__(self, *args, **kwargs):
        if HAS_S3:
            # S3: prefix all keys with 'static/'
            kwargs.setdefault('location', 'static')
        else:
            # FileSystemStorage: no location prefix
            kwargs['location'] = ''
        super().__init__(*args, **kwargs)
