from functools import wraps
from typing import Callable
from django.http import HttpRequest, HttpResponse


def _lazy_view(import_path: str) -> Callable:
    """Return a view callable that lazy-imports the real view class and
    dispatches the request to it. If the import fails, returns a 501 response."""

    def view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            module_path, cls_name = import_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[cls_name])
            view_cls = getattr(module, cls_name)
            return view_cls.as_view()(request, *args, **kwargs)
        except Exception:
            from django.http import JsonResponse

            return JsonResponse(
                {'detail': 'Token views are not available (missing or incompatible SimpleJWT).'},
                status=501,
            )

    # Preserve attributes like __name__ for Django's URL resolver
    view.__name__ = f"lazy_{import_path.split('.')[-1]}"
    return view


# Lazy proxy views for SimpleJWT token endpoints
token_obtain_pair_view = _lazy_view('rest_framework_simplejwt.views.TokenObtainPairView')
token_refresh_view = _lazy_view('rest_framework_simplejwt.views.TokenRefreshView')
