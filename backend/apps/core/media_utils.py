"""
Centralized media URL utility for consistent URL construction across all serializers.
Handles both S3 and local storage configurations with proper fallbacks.

CRITICAL: All media must be served with absolute URLs to ensure:
1. Frontend can load from S3 without additional URL construction
2. CORS headers are properly handled
3. New uploads work immediately in production
4. No re-deployment required for new media
"""
from django.conf import settings
import logging

logger = logging.getLogger('django')


def get_absolute_media_url(media_url):
    """
    Convert relative media URLs to absolute URLs for frontend consumption.
    
    This function ensures that:
    - S3 URLs are returned as-is (already absolute)
    - Local storage URLs are prefixed with BACKEND_URL
    - Null/empty URLs return None safely
    - Already-absolute URLs are returned unchanged
    - Deduplicates any extra /media/ prefixes
    - Errors are logged for debugging
    
    Args:
        media_url: Can be a File object's URL, string path, or None
        
    Returns:
        Absolute URL string or None if media_url is falsy
        
    Example:
        >>> get_absolute_media_url(obj.image.url)
        'https://pieclobal.s3.amazonaws.com/media/home/sliders/image.jpg'
        
        or (local storage):
        'https://pie-global-funitures.onrender.com/media/home/sliders/image.jpg'
    
    IMPORTANT for production:
    - S3 must have CORS configured for frontend domain
    - All media objects must have public read ACL
    - URLs are absolute - frontend should NOT reconstruct them
    """
    if not media_url:
        return None
    
    try:
        media_str = str(media_url)
        
        # If already absolute, deduplicate /media/ and return
        if media_str.startswith('http://') or media_str.startswith('https://'):
            # Fix double /media/ in absolute URLs
            media_str = media_str.replace('/media/media/', '/media/', 1)
            return media_str
        
        # If using S3 storage backend, URLs from storage are already absolute
        # but may have double /media/ so deduplicate
        if settings.USE_S3:
            media_str = media_str.replace('/media/media/', '/media/', 1)
            media_str = media_str.replace('media/media/', 'media/', 1)
            return media_str
        
        # For local storage, prepend BACKEND_URL (used in development or Render with local media)
        # This ensures frontend gets absolute URLs even with local Django development server
        backend_url = settings.BACKEND_URL.rstrip('/')
        media_path = media_str.lstrip('/')
        absolute_url = f"{backend_url}/{media_path}"
        # Deduplicate any double /media/
        absolute_url = absolute_url.replace('/media/media/', '/media/', 1)
        
        return absolute_url
        
    except Exception as e:
        logger.error(f"[MediaURL] Error constructing absolute URL for {media_url}: {str(e)}")
        return None
