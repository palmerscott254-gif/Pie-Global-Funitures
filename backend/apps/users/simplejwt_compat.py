from typing import Optional, Tuple

from rest_framework.authentication import BaseAuthentication


class JWTAuthCompat(BaseAuthentication):
    """Lazy adapter for rest_framework_simplejwt.authentication.JWTAuthentication.

    This avoids importing SimpleJWT at Django startup (which can fail if the
    installed SimpleJWT version expects different Django internals). The real
    backend is imported on first use.
    """

    _delegate = None

    def _get_delegate(self):
        if self._delegate is None:
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication

                self._delegate = JWTAuthentication()
            except Exception:
                # Leave delegate as None — the adapter will behave as a no-op
                self._delegate = None
        return self._delegate

    def authenticate(self, request) -> Optional[Tuple[object, object]]:
        delegate = self._get_delegate()
        if delegate is None:
            return None
        return delegate.authenticate(request)

    def authenticate_header(self, request) -> str:
        delegate = self._get_delegate()
        if delegate is None:
            return ''
        return delegate.authenticate_header(request)
