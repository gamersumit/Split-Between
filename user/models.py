import datetime
from django.utils import timezone
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import transaction

# Create your models here.
class User(AbstractUser): 
    """
    Custom User model extending the AbstractUser model.
    - id: Primary key, UUID field with default value set to a new UUID4.
    - avatar: URL field for user's avatar, optional.
    - email: Email field, unique and required.
    - is_deleted: Boolean field to mark if the user is deleted, default is False.
    - is_verified: Boolean field to mark if the user is verified, default is False.
    - last_deactivation: DateTime field for the last deactivation timestamp, optional.
    - unseen_total_activities: PositiveInteger field for tracking unseen activities, default is 0.

    Methods:
    - __str__: Returns the username of the user.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.URLField(null = True, blank = True)
    email = models.EmailField(unique=True, null = False, blank = False)
    is_deleted = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    unseen_total_activities = models.PositiveIntegerField(default=0, null=True, blank=True)
    
    friends = models.ManyToManyField('self', symmetrical=True, through='Friendship', null=True, blank=True)
   
   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
  
class Friendship(models.Model):
    """
    Model representing a friendship between two users.
    - user1: ForeignKey to the User model, representing one user in the friendship.
    - user2: ForeignKey to the User model, representing the other user in the friendship.
    - created_at: DateTime field for the timestamp when the friendship was created.
    - balence: Float field for tracking the balance between two users, default is 0.

    Methods:
    - __str__: Returns a string representation of the friendship indicating the balance.

    Meta:
    - unique_together: Ensures that each pair of users has a unique friendship record.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendship')
    friend = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_set')
    created_at = models.DateTimeField(auto_now_add = True)
    balance = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user.username} owes {self.friend.username} : {self.balance} amount."
    
    
    class Meta:
        unique_together = ('user', 'friend')

class ForgotPasswordOTP(models.Model):
    """
    Model for storing OTPs for password reset functionality.
    - user_id: OneToOneField to the User model, ensures each user has a unique OTP.
    - otp: PositiveInteger field for the OTP value.
    - updated_at: DateTime field for the timestamp when the OTP was last updated.

    Methods:
    - isExpired: Checks if the OTP has expired (older than 5 minutes) and deletes it if expired.
    - __str__: Returns a string representation indicating the user the OTP is for.
    """
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
    """
    Model for storing email verification tokens.
    - user_id: OneToOneField to the User model, ensures each user has a unique verification token.
    - token: CharField for the token value, maximum length of 128 characters.
    - updated_at: DateTime field for the timestamp when the token was last updated.

    Methods:
    - isExpired: Checks if the token has expired (older than 5 minutes) and deletes it if expired.
    - __str__: Returns a string representation indicating the user the token is for.
    """

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