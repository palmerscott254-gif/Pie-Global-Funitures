from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from django.conf import settings


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(payload: Dict[str, Any]) -> str:
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def create_access_token(user) -> str:
    now = _utc_now()
    payload = {
        'sub': str(user.id),
        'email': user.email,
        'type': 'access',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)).timestamp()),
    }
    return _encode(payload)


def create_refresh_token(user) -> str:
    now = _utc_now()
    payload = {
        'sub': str(user.id),
        'email': user.email,
        'type': 'refresh',
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)).timestamp()),
    }
    return _encode(payload)


def decode_token(token: str, expected_type: str | None = None) -> Dict[str, Any]:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    token_type = payload.get('type')
    if expected_type and token_type != expected_type:
        raise ValueError('Invalid token type.')
    return payload
