from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.common.responses import success_response, error_response
from apps.users.models import UserNotification
from apps.authentication.services import JWTService
from .serializers import (
    UserProfileSerializer, UpdateProfileSerializer, 
    ChangePasswordSerializer, NotificationSerializer,
    MarkNotificationReadSerializer
)


class ProfileView(APIView):
    """User profile endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user profile"""
        serializer = UserProfileSerializer(request.user)
        
        return success_response({
            "user": serializer.data
        })
    
    def post(self, request):
        """Update user profile"""
        serializer = UpdateProfileSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.update(request.user, serializer.validated_data)
            
            # Get updated profile
            profile_serializer = UserProfileSerializer(request.user)
            
            return success_response({
                "user": profile_serializer.data
            }, "Profile updated successfully")
        
        return error_response(
            "Validation failed",
            "VALIDATION_ERROR",
            serializer.errors
        )


class ChangePasswordView(APIView):
    """Change password endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Generate new access token (invalidate current sessions)
            ip_address = self.get_client_ip(request)
            
            # Terminate all existing sessions
            user.login_sessions.filter(status='active').update(
                status='terminated',
                session_end=timezone.now()
            )
            
            # Create new session
            access_token, session = JWTService.create_login_session(
                user, ip_address,
                platform='mobile-app'  # Default platform
            )
            
            return success_response({
                "auth_token": access_token
            }, "Password changed successfully")
        
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


class NotificationsView(APIView):
    """User notifications endpoint"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user notifications"""
        page = int(request.query_params.get('page', 1))
        limit = min(int(request.query_params.get('limit', 20)), 50)
        unread_only = request.query_params.get('unread_only', '').lower() == 'true'
        
        # Get notifications query
        notifications_query = UserNotification.objects.filter(user=request.user)
        
        if unread_only:
            notifications_query = notifications_query.filter(read=False)
        
        # Get unread count
        unread_count = UserNotification.objects.filter(user=request.user, read=False).count()
        
        # Paginate
        paginator = Paginator(notifications_query, limit)
        
        try:
            page_obj = paginator.page(page)
        except:
            return error_response(
                "Invalid page number",
                "INVALID_PAGE"
            )
        
        # Serialize notifications
        serializer = NotificationSerializer(page_obj, many=True)
        
        return success_response({
            "notifications": serializer.data,
            "unread_count": unread_count,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": paginator.count,
                "total_pages": paginator.num_pages
            }
        })


class MarkNotificationReadView(APIView):
    """Mark notifications as read endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        notification_id = request.data.get('notification_id')
        
        if not notification_id:
            return error_response(
                "notification_id is required",
                "MISSING_PARAM"
            )
        
        # Handle single notification ID or list of IDs
        if isinstance(notification_id, list):
            notification_ids = notification_id
        else:
            notification_ids = [notification_id]
        
        # Update notifications
        updated_count = UserNotification.objects.filter(
            user=request.user,
            id__in=notification_ids
        ).update(read=True)
        
        if updated_count == 0:
            return error_response(
                "No notifications found to mark as read",
                "NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        return success_response(
            message=f"Marked {updated_count} notification(s) as read"
        )