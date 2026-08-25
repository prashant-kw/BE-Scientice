import logging
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from common.models import AuditLog
from .models import User
from .throttling import LoginRateThrottle
from .serializers import (
    UserProfileSerializer,
    UserRegisterSerializer,
    UserLoginSerializer,
)

logger = logging.getLogger('scientice.auth')

def get_client_ip(request):
    """Safely extract remote IP address handling proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

def record_auth_audit(request, action, user=None, email='', details=None):
    """
    Record an immutable authentication audit event into the database.
    Never raises an exception to ensure core auth flows remain resilient.
    """
    try:
        ip = get_client_ip(request)
        ua = request.META.get('HTTP_USER_AGENT', '')
        actor_email = email or (user.email if user else '')
        AuditLog.objects.create(
            user=user,
            actor_email=actor_email,
            action=action,
            ip_address=ip,
            user_agent=ua,
            details=details or {},
        )
    except Exception as err:
        logger.error(f"Failed to record auth audit log: {err}")

class RegisterView(APIView):
    """
    Public registration endpoint for healthcare professionals and patients.
    Returns JWT access & refresh tokens along with user profile.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserRegisterSerializer,
        responses={201: UserProfileSerializer},
        description="Register a new healthcare professional or user"
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            registered_email = request.data.get('email', '')
            record_auth_audit(
                request,
                AuditLog.Action.USER_REGISTERED,
                email=registered_email,
                details={'role': request.data.get('role', 'doctor')}
            )
            return Response(result, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    User login endpoint authenticating via email and password.
    Enforces IP-based rate throttling (5 attempts / minute).
    Returns JWT access & refresh tokens along with user profile.
    """
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserProfileSerializer},
        description="Authenticate user and return JWT tokens + profile"
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data.get('_user_obj')
            record_auth_audit(
                request,
                AuditLog.Action.LOGIN_SUCCESS,
                user=user_obj,
                email=user_obj.email if user_obj else request.data.get('email', '')
            )
            response_data = {
                'user': serializer.validated_data['user'],
                'access': serializer.validated_data['access'],
                'refresh': serializer.validated_data['refresh'],
            }
            return Response(response_data, status=status.HTTP_200_OK)

        # Log failed authentication attempt for security monitoring
        email_attempted = request.data.get('email', '')
        record_auth_audit(
            request,
            AuditLog.Action.LOGIN_FAILED,
            email=email_attempted,
            details={'errors': serializer.errors}
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    Blacklist the refresh token to logout user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Blacklist refresh token on logout",
        responses={200: dict}
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            record_auth_audit(
                request,
                AuditLog.Action.LOGOUT,
                user=request.user,
                email=request.user.email
            )
            return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'message': 'Invalid token or token already blacklisted'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    """
    Retrieve or update currently authenticated user profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: UserProfileSerializer},
        description="Retrieve current user profile"
    )
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserProfileSerializer,
        responses={200: UserProfileSerializer},
        description="Update current user profile"
    )
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ForgotPasswordView(APIView):
    """
    Public endpoint to initiate password reset request.
    Verifies user email exists and returns authorization for reset.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'email': ['Email address is required.']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'No registered account found with this email address. Please check your email or register.'},
                status=status.HTTP_404_NOT_FOUND
            )

        record_auth_audit(
            request,
            AuditLog.Action.LOGIN_FAILED,
            user=user,
            email=user.email,
            details={'reason': 'Password reset requested'}
        )

        return Response({
            'detail': f'Account verified for {user.email}. You can now enter your new password.',
            'email': user.email,
        }, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
    Public endpoint to set a new password for a user account.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        new_password = request.data.get('password', '').strip()

        if not email or not new_password:
            return Response(
                {'detail': 'Both email and new password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(new_password) < 6:
            return Response(
                {'detail': 'Password must be at least 6 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Account not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at'])

        record_auth_audit(
            request,
            AuditLog.Action.LOGIN_SUCCESS,
            user=user,
            email=user.email,
            details={'reason': 'Password reset successfully'}
        )

        return Response({
            'detail': 'Your password has been successfully reset! You can now log in with your new password.'
        }, status=status.HTTP_200_OK)

