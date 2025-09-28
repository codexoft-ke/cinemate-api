from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.users.models import Genre, UserGenre, UserNotification

User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Genre serializer"""
    class Meta:
        model = Genre
        fields = ['id', 'name']


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
        """Get user's preferred genre IDs from UserGenre table"""
        # Using prefetch_related in the view would be more efficient
        user_genres = UserGenre.objects.filter(user=obj).select_related('genre')
        return [ug.genre.id for ug in user_genres]


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer with prefetched genres as IDs"""
    name = serializers.CharField(source='full_name', max_length=100)
    email = serializers.EmailField(source='email_address')
    genres = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'genres', 'maturity_filter', 'preferred_language']
        read_only_fields = ['id']
    
    def get_genres(self, obj):
        """Get user's preferred genre IDs from prefetched UserGenre relationship"""
        return [ug.genre.id for ug in obj.user_genres.all()]


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
    
    def validate_genres(self, value):
        """Validate that all genre IDs exist"""
        if value:
            existing_genres = set(Genre.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_genres = set(value) - existing_genres
            if invalid_genres:
                raise serializers.ValidationError(f'Invalid genre IDs: {list(invalid_genres)}')
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
        
        # Update genres in UserGenre table
        if genres_data is not None:
            # Remove existing user genres
            UserGenre.objects.filter(user=instance).delete()
            
            # Add new genres
            user_genres_to_create = []
            for genre_id in genres_data:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    user_genres_to_create.append(
                        UserGenre(user=instance, genre=genre)
                    )
                except Genre.DoesNotExist:
                    # This should be caught by validate_genres, but keeping as safety
                    continue
            
            # Bulk create for better performance
            if user_genres_to_create:
                UserGenre.objects.bulk_create(user_genres_to_create)
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate_new_password(self, value):
        """Validate new password"""
        user = self.context['request'].user
        validate_password(value, user)
        return value
    
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer"""
    
    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'type', 'image', 'movie_id', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarkNotificationReadSerializer(serializers.Serializer):
    """Mark notification as read serializer"""
    notification_id = serializers.UUIDField()
    
    def validate_notification_id(self, value):
        """Validate notification exists and belongs to user"""
        user = self.context['request'].user
        try:
            notification = UserNotification.objects.get(id=value, user=user)
            return notification
        except UserNotification.DoesNotExist:
            raise serializers.ValidationError('Notification not found')
    
    def save(self):
        """Mark notification as read"""
        notification = self.validated_data['notification_id']
        notification.read = True
        notification.save()
        return notification


class UserGenreSerializer(serializers.ModelSerializer):
    """User genre relationship serializer"""
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    genre_id = serializers.CharField(source='genre.id', read_only=True)
    
    class Meta:
        model = UserGenre
        fields = ['id', 'genre_id', 'genre_name', 'created_at']
        read_only_fields = ['id', 'created_at']


# Alternative serializer for getting user genres directly from UserGenre table
class UserGenreListSerializer(serializers.Serializer):
    """Serializer to get user genres from UserGenre table"""
    user_id = serializers.UUIDField()
    
    def validate_user_id(self, value):
        """Validate user exists"""
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError('User not found')
    
    def to_representation(self, instance):
        """Return user genres as array of IDs"""
        user = self.validated_data['user_id']
        user_genres = UserGenre.objects.filter(user=user).select_related('genre')
        return {
            'user_id': str(user.id),
            'user_email': user.email_address,
            'genres': [ug.genre.id for ug in user_genres]
        }