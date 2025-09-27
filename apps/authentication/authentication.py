from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from .services import JWTService

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """Custom JWT authentication"""
    
    def authenticate(self, request):
        # List of paths that do not require authentication
        unauthenticated_paths = [
            '/auth/signup',
            '/auth/login',
            '/auth/forgot-password',
            '/movies/genres',
        ]

        if request.path in unauthenticated_paths:
            return None

        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        try:
            token = auth_header.split(' ')[1]
            payload = JWTService.decode_token(token)

            if payload.get('type') != 'access_token':
                raise AuthenticationFailed('Invalid token type')

            user = User.objects.get(id=payload['user_id'])

            # Validate session
            session = JWTService.validate_session(payload['session_id'])
            if not session:
                raise AuthenticationFailed('Session expired or invalid')

            return (user, token)

        except (User.DoesNotExist, ValueError, KeyError):
            raise AuthenticationFailed('Invalid token')
    
    def authenticate_header(self, request):
        return 'Bearer'