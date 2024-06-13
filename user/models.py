import datetime
from django.forms import ValidationError
from django.utils import timezone
from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.db.models import CheckConstraint, Q
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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username
  
class Balance(models.Model):
    """
    Model representing a balance between two users.

    Fields:
    - friend_owes: ForeignKey to the User model, representing one user who owes the balance.
    - friend_owns: ForeignKey to the User model, representing the other user who owns the balance.
    - created_at: DateTime field for the timestamp when the balance record was created.
    - balance: Float field for tracking the balance amount between two users, default is 0.

    Methods:
    - __str__: Returns a string representation indicating the balance between friends.

    Meta:
    - unique_together: Ensures that each pair of users has a unique balance record.
    - CheckConstraint: Ensures friend_owes and friend_owns are different users.

    Signals:
    - pre_save: Signal receiver `check_bidirectional_friendship` ensures bidirectional uniqueness
      in the Balance model before saving new instances.

    """
    friend_owes = models.ForeignKey(User, on_delete=models.CASCADE, editable= False, related_name='balence_owes')
    friend_owns = models.ForeignKey(User, on_delete=models.CASCADE, editable=False, related_name='balence_owns')
    created_at = models.DateTimeField(auto_now_add = True, editable=False)
    balance = models.FloatField(default=0)   


    def __str__(self):
        return f"{self.friend_owes.username} owes {self.friend_owns.username} : {self.balance} amount."
    
    
    class Meta:
        unique_together = ('friends_owes', 'friend_owns')
        CheckConstraint(
                name='different_users',
                check=~Q(friend_owes=models.F('friend_owns')),  # friend_owes != friend_owns
            ),
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
        """
        Checks if the OTP has expired (older than 5 minutes) and deletes it if expired.
        Returns True if expired, False otherwise.
        """

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
        """
        Checks if the OTP has expired (older than 5 minutes) and deletes it if expired.
        Returns True if expired, False otherwise.
        """

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