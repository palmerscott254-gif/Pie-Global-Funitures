"""
Custom middleware for Pie Global Furniture project.
"""
import logging
import mimetypes

from .performance import mark_request_and_get_state


logger = logging.getLogger('django')


class StartupPerformanceMiddleware:
    """
    Lightweight middleware to log cold-start versus warm requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_cold_request, uptime_ms = mark_request_and_get_state()
        if is_cold_request:
            logger.info(
                'COLD_START first_request path=%s startup_ms=%.2f',
                request.path,
                uptime_ms,
            )
        else:
            logger.debug('WARM_REQUEST path=%s uptime_ms=%.2f', request.path, uptime_ms)

        return self.get_response(request)


class VideoMimeTypeMiddleware:
    """
    Middleware to ensure video files are served with correct MIME types.
    This prevents video playback issues in browsers.
    Updated to use modern middleware pattern (no MiddlewareMixin).
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Register common video MIME types
        mimetypes.add_type('video/mp4', '.mp4')
        mimetypes.add_type('video/webm', '.webm')
        mimetypes.add_type('video/ogg', '.ogv')
        mimetypes.add_type('video/quicktime', '.mov')
    
    def __call__(self, request):
        """Process the request and response."""
        response = self.get_response(request)
        return self.process_response(request, response)
    
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
