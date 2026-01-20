"""
Centralized media URL utility for consistent URL construction across all serializers.
Handles both S3 and local storage configurations with proper fallbacks.
"""
from django.conf import settings


def get_absolute_media_url(media_url):
    """
    Convert relative media URLs to absolute URLs for frontend consumption.
    
    This function ensures that:
    - S3 URLs are returned as-is (already absolute)
    - Local storage URLs are prefixed with BACKEND_URL
    - Null/empty URLs return None
    - Already-absolute URLs are returned unchanged
    
    Args:
        media_url: Can be a File object's URL, string path, or None
        
    Returns:
        Absolute URL string or None if media_url is falsy
        
    Example:
        >>> get_absolute_media_url(obj.image.url)
        'https://pieclobal.s3.amazonaws.com/media/products/image.jpg'
        
        or (local storage):
        'https://pie-global-funitures.onrender.com/media/products/image.jpg'
    """
    if not media_url:
        return None
    
    media_str = str(media_url)
    
    # If already absolute, return as-is (S3 URLs or previously constructed)
    if media_str.startswith('http://') or media_str.startswith('https://'):
        return media_str
    
    # If using S3 storage backend, URLs from storage are already absolute
    if settings.USE_S3:
        return media_str
    
    # For local storage, prepend BACKEND_URL (used in development or Render with local media)
    # This ensures frontend gets absolute URLs even with local Django development server
    backend_url = settings.BACKEND_URL.rstrip('/')
    media_path = media_str.lstrip('/')
    return f"{backend_url}/{media_path}"
