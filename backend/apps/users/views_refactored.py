"""Refactored user views using AuthenticationService with improved error handling."""
import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.users.models import User
from apps.users.serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    RefreshTokenSerializer,
)
from apps.users.auth_service import AuthenticationService, TokenService
from apps.core.response_helpers import ResponseFormatter
from apps.core.audit import extract_client_ip

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user registration and authentication.
    
    Endpoints:
    - POST /users/register/ - Register new account
    - POST /users/login/ - Login with email/password
    - POST /users/refresh/ - Refresh access token
    - POST /users/logout/ - Logout (clears session)
    - GET /users/me/ - Get current user
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'register':
            return UserRegisterSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'refresh':
            return RefreshTokenSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user account.
        
        Request body:
            {
                "name": "John Doe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "password_confirm": "SecurePass123"
            }
        """
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return ResponseFormatter.validation_error(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user, tokens = AuthenticationService.register_user(
                name=serializer.validated_data['name'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                request=request,
            )

            # Set session for hybrid auth support
            request.session['user_id'] = str(user.id)
            request.session['user_email'] = user.email

            return ResponseFormatter.created(
                message='Account created successfully.',
                data={
                    'user': UserSerializer(user).data,
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                },
            )

        except Exception as e:
            logger.exception(f"Registration error: {e}")
            return ResponseFormatter.server_error()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login with email and password.
        
        Request body:
            {
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        """
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return ResponseFormatter.validation_error(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user, tokens = AuthenticationService.login_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                request=request,
            )

            # Set session for hybrid auth support
            request.session['user_id'] = str(user.id)
            request.session['user_email'] = user.email
            request.session.modified = True
            # If frontend provided guest cart items, merge into persistent cart
            try:
                guest_items = request.data.get('cart', {}).get('items') if isinstance(request.data.get('cart'), dict) else request.data.get('cart')
                if guest_items:
                    from apps.cart.models import Cart, CartItem
                    from django.db import transaction

                    cart, _ = Cart.objects.get_or_create(user=user)
                    with transaction.atomic():
                        for it in guest_items:
                            pid = it.get('product_id')
                            qty = int(it.get('quantity', 1)) if it.get('quantity') is not None else 1
                            if not pid:
                                continue
                            obj, created = CartItem.objects.get_or_create(cart=cart, product_id=pid,
                                                                          defaults={'quantity': qty})
                            if not created:
                                obj.quantity = obj.quantity + qty
                                obj.save()
            except Exception:
                logger.exception('Failed to merge guest cart during login')

            return ResponseFormatter.success(
                message='Signed in successfully.',
                data={
                    'user': UserSerializer(user).data,
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                },
            )

        except ValueError as e:
            return ResponseFormatter.unauthorized(str(e))
        except User.DoesNotExist:
            return ResponseFormatter.unauthorized('No account found for this email.')
        except Exception as e:
            logger.exception(f"Login error: {e}")
            return ResponseFormatter.server_error()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout the current user."""
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'user_email' in request.session:
            del request.session['user_email']
        request.session.modified = True

        return ResponseFormatter.success(message='Logged out successfully.')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current authenticated user."""
        if isinstance(request.user, User):
            return ResponseFormatter.success(
                data={'user': UserSerializer(request.user).data}
            )

        user_id = request.session.get('user_id')
        if not user_id:
            return ResponseFormatter.unauthorized('Not authenticated.')

        try:
            user = User.objects.get(id=user_id)
            return ResponseFormatter.success(
                data={'user': UserSerializer(user).data}
            )
        except User.DoesNotExist:
            if 'user_id' in request.session:
                del request.session['user_id']
            return ResponseFormatter.unauthorized('User not found.')

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        """Refresh access token using a refresh token.
        
        Request body:
            {
                "refresh": "<refresh_token>"
            }
        """
        serializer = self.get_serializer(data=request.data)
        
        if not serializer.is_valid():
            return ResponseFormatter.validation_error(serializer.errors)

        try:
            tokens = AuthenticationService.refresh_access_token(
                refresh_token=serializer.validated_data['refresh'],
                request=request,
            )
            return ResponseFormatter.success(
                message='Token refreshed.',
                data={'access': tokens['access']},
            )
        except ValueError as e:
            return ResponseFormatter.unauthorized(str(e))
        except Exception as e:
            logger.exception(f"Token refresh error: {e}")
            return ResponseFormatter.server_error()
