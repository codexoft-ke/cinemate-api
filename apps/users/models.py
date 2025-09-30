import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email_address=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
def create_superuser(self, email_address, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email_address=email_address, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model"""
    
    MATURITY_CHOICES = [
        ('all', 'All'),
        ('teen', 'Teen'),
        ('adult', 'Adult'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=25, unique=True, null=True, blank=True)
    email_address = models.EmailField(max_length=100, unique=True)
    is_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    maturity_filter = models.CharField(
        max_length=10, 
        choices=MATURITY_CHOICES, 
        default='all'
    )
    
    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.email_address
    
    @property
    def name(self):
        return self.full_name
    
    @property
    def email(self):
        return self.email_address


class Genre(models.Model):
    """Movie genres model"""
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'genres'
    
    def __str__(self):
        return self.name


class UserGenre(models.Model):
    """User preferred genres"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_genres')
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_genres'
        unique_together = ['user', 'genre']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.genre.name}"


class UserFavourite(models.Model):
    """User favourite movies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    movie_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_favourites'
        unique_together = ['user', 'movie_id']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.movie_id}"


class UserNotification(models.Model):
    """User notifications"""
    
    NOTIFICATION_TYPES = [
        ('movie_added', 'Movie Added'),
        ('movie_recommendation', 'Movie Recommendation'),
        ('system_update', 'System Update'),
        ('favorite_update', 'Favorite Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=25, choices=NOTIFICATION_TYPES, default='movie_added')
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.TextField(null=True, blank=True)
    movie_id = models.CharField(max_length=50, null=True, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.title}"


class UserHistory(models.Model):
    """User movie viewing history"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='history')
    movie_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.movie_id}"


class LoginSession(models.Model):
    """User login sessions for JWT management"""
    
    PLATFORM_CHOICES = [
        ('mobile-app', 'Mobile App'),
        ('web', 'Web'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('terminated', 'Terminated'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_sessions')
    ip_address = models.GenericIPAddressField()
    platform = models.CharField(max_length=15, choices=PLATFORM_CHOICES)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    refresh_token = models.CharField(max_length=255)
    refresh_token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'login_sessions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.platform} - {self.status}"


class PasswordReset(models.Model):
    """Password reset requests with OTP"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('completed', 'Completed'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_resets')
    reset_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    otp_code_hash = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    ip_address = models.GenericIPAddressField()
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'password_resets'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email_address} - {self.status}"


class IPBlacklist(models.Model):
    """IP blacklist for security"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ip_address = models.GenericIPAddressField()
    reason = models.TextField(null=True, blank=True)
    blocked_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ip_blacklist'
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"