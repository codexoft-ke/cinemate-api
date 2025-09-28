from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.common.responses import success_response, error_response
from apps.users.models import LoginSession, PasswordReset
from .serializers import (
    LoginSerializer, SignupSerializer, ForgotPasswordSerializer,
    VerifyOTPSerializer, ChangePasswordSerializer, RefreshTokenSerializer
)
from .services import JWTService, OTPService

User = get_user_model()


class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            ip_address = self.get_client_ip(request)
            
            # Create login session
            access_token, session = JWTService.create_login_session(
                user, ip_address, 
                platform=request.data.get('platform', 'mobile-app'),
                device_name=request.data.get('device_name')
            )
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return success_response({
                "auth_token": access_token,
                "user": {
                    "id": str(user.id),
                    "name": user.full_name,
                    "email": user.email_address
                }
            }, "Login successful")
        
        return error_response(
            "Invalid email or password",
            "INVALID_CREDENTIALS",
            serializer.errors,
            status.HTTP_401_UNAUTHORIZED
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SignupView(APIView):
    """User signup endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            ip_address = self.get_client_ip(request)
            
            # Create login session
            access_token, session = JWTService.create_login_session(
                user, ip_address,
                platform=request.data.get('platform', 'mobile-app'),
                device_name=request.data.get('device_name')
            )
            
            return success_response({
                "auth_token": access_token,
                "user": {
                    "id": str(user.id),
                    "name": user.full_name,
                    "email": user.email_address
                }
            }, "Account created successfully", status.HTTP_201_CREATED)
        
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            serializer.errors
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ForgotPasswordView(APIView):
    """Forgot password endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email_address=email)
            ip_address = self.get_client_ip(request)
            
            # Create password reset request
            reset_request, otp = OTPService.create_password_reset(user, ip_address)
            
            return success_response({
                "reset_token": reset_request.reset_token
            }, "OTP sent to your email")
        
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            serializer.errors
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class VerifyOTPView(APIView):
    """Verify OTP endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get reset token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response(
                "Reset token required",
                "TOKEN_REQUIRED",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = JWTService.decode_token(token)
            
            if payload.get('type') != 'forgot_password':
                return error_response(
                    "Invalid token type",
                    "INVALID_TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            reset_request = PasswordReset.objects.get(
                id=payload['reset_id'],
                status='pending'
            )
            
        except (ValueError, PasswordReset.DoesNotExist):
            return error_response(
                "Invalid or expired reset token",
                "INVALID_TOKEN",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = VerifyOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp_code']
            
            # Check if OTP is correct
            if not OTPService.verify_otp(otp_code, reset_request.otp_code_hash):
                reset_request.attempts += 1
                reset_request.save()
                
                if reset_request.attempts >= 3:
                    reset_request.status = 'revoked'
                    reset_request.save()
                    return error_response(
                        "Too many failed attempts. Please request a new OTP",
                        "MAX_ATTEMPTS_EXCEEDED"
                    )
                
                return error_response(
                    "Invalid OTP code",
                    "INVALID_OTP"
                )
            
            # Verify IP address
            if reset_request.ip_address != self.get_client_ip(request):
                return error_response(
                    "Invalid request source",
                    "INVALID_SOURCE"
                )
            
            # Check if expired
            if reset_request.expires_at < timezone.now():
                reset_request.status = 'revoked'
                reset_request.save()
                return error_response(
                    "OTP has expired",
                    "OTP_EXPIRED"
                )
            
            # Mark as verified
            reset_request.status = 'verified'
            reset_request.save()
            
            return success_response(message="OTP verified successfully")
        
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            serializer.errors
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ChangePasswordView(APIView):
    """Change password endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get reset token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response(
                "Reset token required",
                "TOKEN_REQUIRED",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = JWTService.decode_token(token)
            
            if payload.get('type') != 'forgot_password':
                return error_response(
                    "Invalid token type",
                    "INVALID_TOKEN",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            reset_request = PasswordReset.objects.get(
                id=payload['reset_id'],
                status='verified'
            )
            
        except (ValueError, PasswordReset.DoesNotExist):
            return error_response(
                "Invalid or expired reset token",
                "INVALID_TOKEN",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            new_password = serializer.validated_data['new_password']
            
            # Update user password
            user = reset_request.user
            user.set_password(new_password)
            user.save()
            
            # Mark request as completed
            reset_request.status = 'completed'
            reset_request.save()
            
            # Revoke all other pending requests for this user
            PasswordReset.objects.filter(
                user=user,
                status__in=['pending', 'verified']
            ).exclude(id=reset_request.id).update(status='revoked')
            
            return success_response(message="Password reset successfully")
        
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            serializer.errors
        )

class RefreshTokenView(APIView):
    """Refresh token endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return error_response(
                "Authentication token required",
                "TOKEN_REQUIRED",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            token = auth_header.split(' ')[1]
            
            # Decode token ignoring expiration for refresh operations
            payload = JWTService.decode_token_ignore_expiration(token)
            
            # Validate it's an access token
            if payload.get('type') != 'access_token':
                return error_response(
                    "Invalid token type",
                    "INVALID_TOKEN_TYPE",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check required fields
            session_id = payload.get('session_id')
            if not session_id:
                return error_response(
                    "Token missing session information",
                    "INVALID_TOKEN_STRUCTURE",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            # Validate session exists and is active
            session = JWTService.validate_session(session_id)
            if not session:
                return error_response(
                    "Session expired or invalid",
                    "SESSION_INVALID",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate new access token
            new_access_token = JWTService.generate_access_token(session.user, session.id)
            
            return success_response({
                "auth_token": new_access_token
            }, "Token refreshed successfully")
            
        except (ValueError, KeyError) as e:
            return error_response(
                "Invalid or expired token",
                "INVALID_TOKEN",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return error_response(
                "Failed to refresh token",
                "REFRESH_FAILED",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class LogoutView(APIView):
    """Logout endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get current token from request
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            token = auth_header.split(' ')[1]
            payload = JWTService.decode_token(token)
            
            # Terminate session
            session = LoginSession.objects.get(id=payload['session_id'])
            session.status = 'terminated'
            session.session_end = timezone.now()
            session.save()
            
            return success_response(message="Logged out successfully")
            
        except Exception as e:
            return error_response(
                "Logout failed",
                "LOGOUT_FAILED"
            )