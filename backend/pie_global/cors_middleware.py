import re
from django.conf import settings


class CorsMiddleware:
    """Small, local CORS middleware shim used when django-cors-headers is unavailable.

    It implements a minimal subset of behavior: if the request has an Origin header
    and it matches the configured allowed origins (or CORS_ALLOW_ALL_ORIGINS=True),
    the middleware appends appropriate CORS response headers.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        self.allowed_origins = set(getattr(settings, 'CORS_ALLOWED_ORIGINS', []))
        self.allowed_regexes = [re.compile(p) for p in getattr(settings, 'CORS_ALLOWED_ORIGIN_REGEXES', [])]
        self.allow_credentials = getattr(settings, 'CORS_ALLOW_CREDENTIALS', False)
        self.allow_methods = ', '.join(getattr(settings, 'CORS_ALLOW_METHODS', [
            'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT'
        ]))
        self.allow_headers = ', '.join(getattr(settings, 'CORS_ALLOW_HEADERS', []))

    def _origin_allowed(self, origin: str) -> bool:
        if self.allow_all:
            return True
        if origin in self.allowed_origins:
            return True
        for rx in self.allowed_regexes:
            if rx.match(origin):
                return True
        return False

    def __call__(self, request):
        response = self.get_response(request)

        origin = request.headers.get('Origin') or request.META.get('HTTP_ORIGIN')
        if not origin:
            return response

        if self._origin_allowed(origin):
            # Set the basic CORS headers
            response['Access-Control-Allow-Origin'] = '*' if self.allow_all else origin
            response['Access-Control-Allow-Methods'] = self.allow_methods
            if self.allow_credentials:
                response['Access-Control-Allow-Credentials'] = 'true'
            if self.allow_headers:
                response['Access-Control-Allow-Headers'] = self.allow_headers

        return response
