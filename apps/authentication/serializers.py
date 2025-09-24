from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from apps.users.models import Genre, UserGenre

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), 
                              username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('Account is deactivated')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class SignupSerializer(serializers.Serializer):
    """Signup serializer"""
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    password = serializers.CharField()
    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )
    
    def validate_email(self, value):
        if User.objects.filter(email_address=value).exists():
            raise serializers.ValidationError('User with this email already exists')
        return value
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        genres_data = validated_data.pop('genres', [])
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['name']
        )
        
        # Add selected genres
        for genre_id in genres_data:
            try:
                genre = Genre.objects.get(id=genre_id)
                UserGenre.objects.create(user=user, genre=genre)
            except Genre.DoesNotExist:
                pass
        
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    """Forgot password serializer"""
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            User.objects.get(email_address=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')
        return value


class VerifyOTPSerializer(serializers.Serializer):
    """Verify OTP serializer"""
    otp_code = serializers.CharField(max_length=6, min_length=6)


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    new_password = serializers.CharField()
    
    def validate_new_password(self, value):
        validate_password(value)
        return value


class RefreshTokenSerializer(serializers.Serializer):
    """Refresh token serializer (uses Authorization header)"""
    pass