from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Membership, Group

@receiver(pre_delete, sender=Membership)
def check_settle_up_before_group_deletion(sender, instance, **kwargs):
    group = instance.group
    if not group.settled_up:
        raise ValueError("Cannot delete group with outstanding balances.")

def has_outstanding_balances(user, group):
    # Implement logic to check if the user has any outstanding balances in the group
    pass

def has_group_outstanding_balances(group):
    # Implement logic to check if there are any outstanding balances in the group
    pass
