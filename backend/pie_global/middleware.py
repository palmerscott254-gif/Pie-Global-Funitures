"""
Custom middleware for Pie Global Furniture project.
"""
import mimetypes
from django.utils.deprecation import MiddlewareMixin


class VideoMimeTypeMiddleware(MiddlewareMixin):
    """
    Middleware to ensure video files are served with correct MIME types.
    This prevents video playback issues in browsers.
    """
    
    def __init__(self, get_response):
        super().__init__(get_response)
        # Register common video MIME types
        mimetypes.add_type('video/mp4', '.mp4')
        mimetypes.add_type('video/webm', '.webm')
        mimetypes.add_type('video/ogg', '.ogv')
        mimetypes.add_type('video/quicktime', '.mov')
    
    def process_response(self, request, response):
        """
        Add or correct Content-Type header for video files.
        """
        if hasattr(response, 'filename'):
            # For FileResponse objects
            filename = str(response.filename)
            if any(filename.endswith(ext) for ext in ['.mp4', '.webm', '.ogv', '.mov']):
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type:
                    response['Content-Type'] = mime_type
                    # Add headers to optimize video streaming
                    response['Accept-Ranges'] = 'bytes'
                    response['Cache-Control'] = 'public, max-age=31536000'
        
        return response
