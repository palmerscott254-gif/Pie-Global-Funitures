import logging
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.sessions.models import Session
from .models import User
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user registration and authentication."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegisterSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            logger.warning(f"Registration validation failed: {exc}")
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()
            # Create session
            request.session['user_id'] = str(user.id)
            request.session['user_email'] = user.email
            
            return Response(
                {
                    'success': True,
                    'message': 'Account created successfully.',
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.exception(f"Failed to create user: {e}")
            return Response(
                {'success': False, 'error': 'Failed to create account. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login a user."""
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            logger.warning(f"Login validation failed: {exc}")
            return Response(
                {'success': False, 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': 'No account found for this email.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'success': False, 'error': 'Account is inactive. Please contact support.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.check_password(password):
            logger.warning(f"Failed login attempt for {email}")
            return Response(
                {'success': False, 'error': 'Incorrect password.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Create session
        request.session['user_id'] = str(user.id)
        request.session['user_email'] = user.email
        request.session.modified = True

        return Response(
            {
                'success': True,
                'message': 'Signed in successfully.',
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout the current user."""
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'user_email' in request.session:
            del request.session['user_email']
        request.session.modified = True

        return Response(
            {'success': True, 'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current authenticated user."""
        user_id = request.session.get('user_id')
        
        if not user_id:
            return Response(
                {'success': False, 'error': 'Not authenticated.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = User.objects.get(id=user_id)
            return Response(
                {'success': True, 'user': UserSerializer(user).data},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            # Clear session
            del request.session['user_id']
            return Response(
                {'success': False, 'error': 'User not found.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
