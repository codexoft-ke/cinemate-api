from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Genre, UserGenre, UserFavourite, 
    UserNotification, UserHistory, LoginSession, 
    PasswordReset, IPBlacklist
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    list_display = ['email_address', 'full_name', 'is_verified', 'is_active', 'date_joined']
    list_filter = ['is_active', 'is_verified', 'is_staff', 'date_joined']
    search_fields = ['email_address', 'full_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email_address', 'password')}),
        ('Personal info', {'fields': ('full_name', 'phone_number')}),
        ('Preferences', {'fields': ('preferred_language', 'maturity_filter')}),
        ('Permissions', {
            'fields': ('is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email_address', 'full_name', 'password1', 'password2'),
        }),
    )


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(UserGenre)
class UserGenreAdmin(admin.ModelAdmin):
    list_display = ['user', 'genre', 'created_at']
    list_filter = ['genre', 'created_at']
    search_fields = ['user__email_address', 'genre__name']


@admin.register(UserFavourite)
class UserFavouriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email_address', 'movie_id']


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'type', 'read', 'created_at']
    list_filter = ['type', 'read', 'created_at']
    search_fields = ['user__email_address', 'title', 'message']


@admin.register(UserHistory)
class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'movie_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email_address', 'movie_id']


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'platform', 'status', 'ip_address', 'session_start']
    list_filter = ['platform', 'status', 'session_start']
    search_fields = ['user__email_address', 'ip_address']


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'ip_address', 'attempts', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email_address', 'ip_address']


@admin.register(IPBlacklist)
class IPBlacklistAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'blocked_until', 'created_at']
    list_filter = ['blocked_until', 'created_at']
    search_fields = ['ip_address', 'reason']