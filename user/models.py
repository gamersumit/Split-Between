import datetime
from django.utils import timezone
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.URLField(null = True, blank = True)
    email = models.EmailField(unique=True, null = False, blank = False)
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    last_deactivation = models.DateTimeField(null = True, blank = True)
    unseen_total_activities = models.PositiveIntegerField(default=0, null=True, blank=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
    
    def add_friend(self, friend):
        if friend != self:
            self.friends.add(friend) 
  

class ForgotPasswordOTP(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    otp = models.PositiveIntegerField(null=True, blank=False)
    updated_at = models.DateTimeField(auto_now=True)

    def isExpired(self):
        # Get the current time with timezone information
        five_minute_ago = timezone.now() - datetime.timedelta(minutes=5)
        
        # Ensure `self.updated_at` is also timezone-aware
        if timezone.is_naive(self.updated_at):
            self.updated_at = timezone.make_aware(self.updated_at, timezone.get_current_timezone())
        
    
        if self.updated_at < five_minute_ago:
            self.delete()
            return True

        return False
    
    def __str__(self):
        return f"FORGOT PASSWORD OTP for {self.user_id.username}"
    
class MailVerificationToken(models.Model):
    user_id = models.OneToOneField(User, related_name= 'verification_token', on_delete=models.CASCADE, unique=True)
    token = models.CharField(128)
    updated_at = models.DateTimeField(auto_now=True)

    def isExpired(self):
        # Get the current time with timezone information
        five_minute_ago = timezone.now() - datetime.timedelta(minutes=5)
        
        # Ensure `self.updated_at` is also timezone-aware
        if timezone.is_naive(self.updated_at):
            self.updated_at = timezone.make_aware(self.updated_at, timezone.get_current_timezone())
        
    
        if self.updated_at < five_minute_ago:
            self.delete()
            return True

        return False
    
    def __str__(self):
        return f"Verification token for {self.user_id.username}"