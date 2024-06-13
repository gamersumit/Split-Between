from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Membership, Group
from user.service import FriendshipService
@receiver(pre_delete, sender=Group)
def check_settle_up_before_group_deletion(sender, instance, **kwargs):
    if not instance.settled_up:
        raise ValueError("Cannot delete group with outstanding balances.")

def has_outstanding_balances(user, group):
    # Implement logic to check if the user has any outstanding balances in the group
    pass

def has_group_outstanding_balances(group):
    # Implement logic to check if there are any outstanding balances in the group
    pass

@receiver(pre_save, sender=Membership)
def create_frienships_before_membership(sender, instance, created, **kwargs):
    if created:
        members = instance.group.members
        FriendshipService.bulk_add_friends(user = instance.user, friends = members)