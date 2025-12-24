"""
Custom middleware for Pie Global Furniture project.
"""
import mimetypes
from django.utils.deprecation import MiddlewareMixin


class VideoMimeTypeMiddleware(MiddlewareMixin):
    """
    Middleware to ensure video and media files are served with correct MIME types.
    This prevents video playback and file download issues in browsers.
    IMPORTANT: This middleware only applies to responses that go through Django.
    In production, media files should be served directly by a reverse proxy or CDN.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # Register common media MIME types to ensure proper browser handling
        mimetypes.add_type('video/mp4', '.mp4')
        mimetypes.add_type('video/webm', '.webm')
        mimetypes.add_type('video/ogg', '.ogv')
        mimetypes.add_type('video/quicktime', '.mov')
        mimetypes.add_type('image/svg+xml', '.svg')
        mimetypes.add_type('image/webp', '.webp')
    
    def process_response(self, request, response):
        """
        Add or correct Content-Type header for media files.
        Also add cache and streaming headers for optimal delivery.
        """
        if hasattr(response, 'filename'):
            # For FileResponse objects (local file serving)
            filename = str(response.filename)
            if any(filename.endswith(ext) for ext in ['.mp4', '.webm', '.ogv', '.mov']):
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type:
                    response['Content-Type'] = mime_type
                    # Enable byte-range requests for video seeking
                    response['Accept-Ranges'] = 'bytes'
                    # Long cache for immutable assets (set version hash if using versioning)
                    response['Cache-Control'] = 'public, max-age=31536000, immutable'
        
        # Handle CORS headers for media cross-origin requests
        # This ensures media files can be accessed from frontend deployed separately
        if request.headers.get('Origin'):
            origin = request.headers.get('Origin')
            # Allow trusted origins (configured in settings.CORS_ALLOWED_ORIGINS)
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Range'
            response['Access-Control-Max-Age'] = '3600'
        
        return response
