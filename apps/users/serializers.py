from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.users.models import Genre, UserGenre, UserNotification

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    name = serializers.CharField(source='full_name', max_length=100)
    email = serializers.EmailField(source='email_address')
    genres = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'genres', 'maturity_filter', 'preferred_language']
        read_only_fields = ['id']
    
    def get_genres(self, obj):
        """Get user's preferred genres"""
        user_genres = UserGenre.objects.filter(user=obj).select_related('genre')
        return [ug.genre.name for ug in user_genres]


class UpdateProfileSerializer(serializers.Serializer):
    """Update profile serializer"""
    name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    maturity_filter = serializers.ChoiceField(
        choices=['all', 'teen', 'adult'],
        required=False
    )
    preferred_language = serializers.CharField(max_length=10, required=False)
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        user = self.context['request'].user
        if User.objects.filter(email_address=value).exclude(id=user.id).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value
    
    def update(self, instance, validated_data):
        """Update user profile"""
        genres_data = validated_data.pop('genres', None)
        
        # Update basic fields
        if 'name' in validated_data:
            instance.full_name = validated_data['name']
        if 'email' in validated_data:
            instance.email_address = validated_data['email']
        if 'maturity_filter' in validated_data:
            instance.maturity_filter = validated_data['maturity_filter']
        if 'preferred_language' in validated_data:
            instance.preferred_language = validated_data['preferred_language']
        
        instance.save()
        
        # Update genres
        if genres_data is not None:
            # Remove existing genres
            UserGenre.objects.filter(user=instance).delete()
            
            # Add new genres
            for genre_id in genres_data:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    UserGenre.objects.create(user=instance, genre=genre)
                except Genre.DoesNotExist:
                    pass
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate_new_password(self, value):
        """Validate new password"""
        validate_password(value)
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'type', 'image', 'movie_id', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarkNotificationReadSerializer(serializers.Serializer):
    """Mark notification as read serializer"""
    notification_id = serializers.CharField()