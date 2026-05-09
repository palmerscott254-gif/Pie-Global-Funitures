"""Authentication and token management service."""
import logging
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import jwt

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

from apps.users.models import User
from apps.core.audit import AuditLogger, extract_client_ip

logger = logging.getLogger(__name__)


class TokenService:
    """Manage JWT token creation and validation."""

    @staticmethod
    def _utc_now() -> datetime:
        """Get current UTC time."""
        return datetime.now(timezone.utc)

    @staticmethod
    def create_access_token(user: User) -> str:
        """Create a new access token."""
        now = TokenService._utc_now()
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES)).timestamp()
            ),
        }
        try:
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            logger.debug(f"Access token created for user: {user.id}")
            return token
        except Exception as e:
            logger.exception(f"Failed to create access token: {e}")
            raise

    @staticmethod
    def create_refresh_token(user: User) -> str:
        """Create a new refresh token."""
        now = TokenService._utc_now()
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "type": "refresh",
            "iat": int(now.timestamp()),
            "exp": int(
                (now + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)).timestamp()
            ),
        }
        try:
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
            logger.debug(f"Refresh token created for user: {user.id}")
            return token
        except Exception as e:
            logger.exception(f"Failed to create refresh token: {e}")
            raise

    @staticmethod
    def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            raise ValueError("Token has expired.")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            raise ValueError("Invalid token.")

        if expected_type:
            token_type = payload.get("type")
            if token_type != expected_type:
                logger.warning(f"Invalid token type: expected {expected_type}, got {token_type}")
                raise ValueError(f"Invalid token type. Expected {expected_type}.")

        return payload

    @staticmethod
    def verify_token_payload(payload: Dict[str, Any]) -> Optional[str]:
        """Extract and validate user ID from token payload."""
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("Token missing 'sub' claim")
            raise ValueError("Invalid token: missing user ID.")
        return user_id


class AuthenticationService:
    """Handle user authentication and account operations."""

    @staticmethod
    def register_user(
        name: str,
        email: str,
        password: str,
        request=None,
    ) -> Tuple[User, Dict[str, str]]:
        """Register a new user account.
        
        Returns:
            Tuple of (User, Dict with 'access' and 'refresh' tokens)
        """
        try:
            # Create user
            user = User.objects.create(
                name=name,
                email=email.strip().lower(),
            )
            user.set_password(password)
            user.save()

            logger.info(f"User registered: {user.id} ({email})")

            # Log audit event
            ip = extract_client_ip(request) if request else None
            AuditLogger.log_auth_register(str(user.id), email, ip)

            # Create tokens
            tokens = {
                "access": TokenService.create_access_token(user),
                "refresh": TokenService.create_refresh_token(user),
            }

            return user, tokens

        except Exception as e:
            logger.exception(f"User registration failed: {e}")
            raise

    @staticmethod
    def login_user(
        email: str,
        password: str,
        request=None,
    ) -> Tuple[User, Dict[str, str]]:
        """Authenticate user and issue tokens.
        
        Returns:
            Tuple of (User, Dict with 'access' and 'refresh' tokens)
            
        Raises:
            User.DoesNotExist: User not found
            ValueError: Invalid password or inactive account
        """
        email = email.strip().lower()
        ip = extract_client_ip(request) if request else None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Login failed: no user found for {email}")
            AuditLogger.log_auth_failed(email, ip, "user_not_found")
            raise

        if not user.is_active:
            logger.warning(f"Login failed: user inactive {user.id}")
            AuditLogger.log_auth_failed(email, ip, "account_inactive")
            raise ValueError("Account is inactive. Please contact support.")

        if not user.check_password(password):
            logger.warning(f"Login failed: invalid password for {email}")
            AuditLogger.log_auth_failed(email, ip, "invalid_password")
            raise ValueError("Incorrect password.")

        logger.info(f"User login successful: {user.id}")
        AuditLogger.log_auth_login(str(user.id), email, ip)

        tokens = {
            "access": TokenService.create_access_token(user),
            "refresh": TokenService.create_refresh_token(user),
        }

        return user, tokens

    @staticmethod
    def refresh_access_token(refresh_token: str, request=None) -> Dict[str, str]:
        """Issue a new access token from a refresh token.
        
        Returns:
            Dict with new 'access' token
            
        Raises:
            ValueError: Invalid or expired refresh token
        """
        try:
            payload = TokenService.decode_token(refresh_token, expected_type="refresh")
            user_id = TokenService.verify_token_payload(payload)

            user = User.objects.get(id=user_id)

            logger.info(f"Token refreshed for user: {user_id}")
            AuditLogger.log_event(
                AuditLogger.AUTH_REFRESH_TOKEN,
                user_id=user_id,
                status="success",
            )

            return {
                "access": TokenService.create_access_token(user),
            }

        except Exception as e:
            logger.warning(f"Token refresh failed: {e}")
            raise ValueError("Invalid or expired refresh token.")

    @staticmethod
    def get_user_from_token(token: str) -> Optional[User]:
        """Retrieve user from access token."""
        try:
            payload = TokenService.decode_token(token, expected_type="access")
            user_id = TokenService.verify_token_payload(payload)
            return User.objects.get(id=user_id)
        except Exception:
            return None

    @staticmethod
    def validate_password_match(password: str, password_confirm: str) -> bool:
        """Check if passwords match."""
        return password == password_confirm
