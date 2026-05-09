"""Custom S3 Storage Backend Configuration.

Provides `S3MediaStorage` and `S3StaticStorage` backed by
`storages.backends.s3boto3.S3Boto3Storage` when available. If the
`django-storages` package is absent or corrupted, fall back to
Django's `FileSystemStorage` so local development continues to work.
"""
from django.conf import settings

try:
    from storages.backends.s3boto3 import S3Boto3Storage  # type: ignore
except Exception:
    from django.core.files.storage import FileSystemStorage as S3Boto3Storage  # type: ignore


class S3MediaStorage(S3Boto3Storage):
    """Storage for media files."""
    location = 'media'
    default_acl = None
    file_overwrite = False


class S3StaticStorage(S3Boto3Storage):
    """Storage for static files."""
    location = 'static'
    default_acl = None
    file_overwrite = True
