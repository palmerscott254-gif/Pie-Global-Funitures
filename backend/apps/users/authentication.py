from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User
from .jwt_utils import decode_token


class PgfAuthentication(BaseAuthentication):
    """Authenticate via JWT bearer tokens or session data."""

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1].strip()
            if not token:
                raise AuthenticationFailed('Missing token.')
            try:
                payload = decode_token(token, expected_type='access')
            except Exception:
                raise AuthenticationFailed('Invalid or expired token.')

            user_id = payload.get('sub')
            if not user_id:
                raise AuthenticationFailed('Invalid token payload.')

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found.')

            return (user, None)

        session_user_id = request.session.get('user_id')
        if session_user_id:
            try:
                user = User.objects.get(id=session_user_id)
                return (user, None)
            except User.DoesNotExist:
                return None

        return None
