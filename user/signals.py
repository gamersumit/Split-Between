from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.forms import ValidationError
from .models import Friendship
from group.models import Activity
from group.service import ActivityService
@receiver(pre_save, sender=Friendship)
def check_bidirectional_friendship(sender, instance, **kwargs):
    """
    Signal receiver function to check bidirectional uniqueness in the Friendship model.

    This function checks if a reverse relationship (friend_owes and friend_owns swapped) already exists
    before saving a new instance of Balance. If such a relationship exists, it raises a ValidationError
    to prevent the instance from being saved.

    Parameters:
    - sender: The model class sending the signal (Balance in this case).
    - instance: The instance of Balance being saved.
    - kwargs: Additional keyword arguments passed to the signal.

    Raises:
    - ValidationError: If a bidirectional relationship already exists between friend_owes and friend_owns.

    Notes:
    - This function runs only during the creation of new instances (created=True), not during updates.
    """
    
    if not instance.pk:  # Only execute for initial creations not updates
       if sender.objects.filter(friend_owes=instance.friend_owns, friend_owns=instance.friend_owes).exists():
            raise ValidationError(f'{instance.friend_owes.username} is already friend with {instance.friend_owns.username}')



@receiver(post_save, sender = Friendship)
def friendship_creation_activity(sender, instance, created, **kwargs):
    if created:
        activity = ActivityService.create_activity(
            type = 'friend_added',
            users = [instance.friend_owes, instance.friend_own],
            metadata = {'friends' : ['userserializer([instance.friend_owes, instance.friend_owns], many = True).data']},
            )
        
