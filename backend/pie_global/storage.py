"""
Custom S3 Storage Backend Configuration
Ensures efficient media uploads to S3 from Django Admin
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class S3MediaStorage(S3Boto3Storage):
    """
    Custom S3 storage for media files with optimized settings
    """
    location = 'media'
    default_acl = None  # Disable ACLs - rely on bucket policy
    file_overwrite = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
    
    def get_default_settings(self):
        settings_dict = super().get_default_settings()
        # Ensure proper cache control for media
        settings_dict['CacheControl'] = 'public, max-age=604800'  # 7 days
        return settings_dict


class S3StaticStorage(S3Boto3Storage):
    """
    Custom S3 storage for static files
    """
    location = 'static'
    default_acl = None  # Disable ACLs - rely on bucket policy
    file_overwrite = True
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN
