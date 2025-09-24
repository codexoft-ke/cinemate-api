import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.users.models import LoginSession, PasswordReset

User = get_user_model()


class JWTService:
    """Service for handling JWT tokens"""
    
    @staticmethod
    def generate_access_token(user, session_id):
        """Generate JWT access token"""
        payload = {
            'user_id': str(user.id),
            'session_id': str(session_id),
            'type': 'access_token',
            'exp': timezone.now() + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME),
            'iat': timezone.now()
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def generate_refresh_token():
        """Generate random refresh token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token(user, reset_id):
        """Generate JWT reset token for password reset"""
        payload = {
            'user_id': str(user.id),
            'reset_id': str(reset_id),
            'type': 'forgot_password',
            'exp': timezone.now() + timedelta(hours=1),  # 1 hour expiry
            'iat': timezone.now()
        }
        
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    @staticmethod
    def decode_token(token):
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
    
    @staticmethod
    def create_login_session(user, ip_address, platform='mobile-app', device_name=None):
        """Create a new login session"""
        refresh_token = JWTService.generate_refresh_token()
        
        session = LoginSession.objects.create(
            user=user,
            ip_address=ip_address,
            platform=platform,
            device_name=device_name,
            refresh_token=refresh_token,
            refresh_token_expires_at=timezone.now() + timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)
        )
        
        access_token = JWTService.generate_access_token(user, session.id)
        
        return access_token, session
    
    @staticmethod
    def validate_session(session_id):
        """Validate if session is still active"""
        try:
            session = LoginSession.objects.get(id=session_id, status='active')
            if session.refresh_token_expires_at < timezone.now():
                session.status = 'expired'
                session.save()
                return None
            return session
        except LoginSession.DoesNotExist:
            return None


class OTPService:
    """Service for handling OTP operations"""
    
    @staticmethod
    def generate_otp():
        """Generate 6-digit OTP"""
        return f"{secrets.randbelow(1000000):06d}"
    
    @staticmethod
    def hash_otp(otp):
        """Hash OTP for secure storage"""
        return hashlib.sha256(otp.encode()).hexdigest()
    
    @staticmethod
    def verify_otp(otp, hashed_otp):
        """Verify OTP against hash"""
        return hashlib.sha256(otp.encode()).hexdigest() == hashed_otp
    
    @staticmethod
    def create_password_reset(user, ip_address):
        """Create password reset request with OTP"""
        # Revoke any existing pending requests
        PasswordReset.objects.filter(
            user=user,
            status__in=['pending', 'verified']
        ).update(status='revoked')
        
        # Generate OTP and hash it
        otp = OTPService.generate_otp()
        otp_hash = OTPService.hash_otp(otp)
        
        # Create reset request
        reset_request = PasswordReset.objects.create(
            user=user,
            otp_code_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=15),  # 15 minutes
            ip_address=ip_address
        )
        
        # Generate reset token
        reset_token = JWTService.generate_reset_token(user, reset_request.id)
        reset_request.reset_token = reset_token
        reset_request.save()
        
        # TODO: Send OTP via email
        # This would be implemented with your email service
        print(f"OTP for {user.email_address}: {otp}")  # For development only
        
        return reset_request, otp