from django.db.models.signals import pre_delete, pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Membership, Group
from user.service import FriendshipService
from .service import ActivityService, GroupService

@receiver(pre_delete, sender=Group)
def check_settle_up_before_group_deletion(sender, instance, **kwargs):
    """
    Signal receiver to check if all balances are settled before deleting a group.

    Args:
    sender: The sender of the signal (Group model).
    instance: The instance of the Group model being deleted.
    kwargs: Additional keyword arguments passed by the signal.

    Raises:
    ValueError: If there are outstanding balances in the group, prevents group deletion.
    """
    if not GroupService.IsGroupSettledUp(group = instance):
        raise ValueError("Cannot delete group with outstanding balances.")


@receiver(pre_delete, sender=Membership)
def check_settle_up_before_leaving_group(sender, instance, **kwargs):
    """
    Signal receiver to check if a member has settled up before leaving a group.

    Args:
    sender: The sender of the signal (Membership model).
    instance: The instance of the Membership model being deleted.
    kwargs: Additional keyword arguments passed by the signal.

    Raises:
    ValueError: If the member has outstanding balances in the group, prevents leaving the group.
    """
    if not GroupService.IsMemberSettledUp(group = instance.group, user=instance.user):
        raise ValueError("Cannot leave group with outstanding balances.")


@receiver(pre_save, sender=Membership)
def create_frienships_before_membership(sender, instance, **kwargs):
    """
    Signal receiver to create friendships for new members joining a group.

    Args:
    sender: The sender of the signal (Membership model).
    instance: The instance of the Membership model being saved.
    kwargs: Additional keyword arguments passed by the signal.

    Notes:
    Checks if the instance is new (not yet saved to the database) and creates friendships
    between the new member and existing members of the group.
    """
    if not instance.pk:
        members = instance.group.members
        FriendshipService.bulk_add_friends(user = instance.user, friends = members)



@receiver(post_save, sender = Group)
def group_creation_activity(sender, instance, created, **kwargs):
    if created:
        activity = ActivityService.create_activity(
            type = 'group_created',
            users = instance.members,
            metadata = {
                'creator' : 'user_serializer(instance.creator).data',
                'group_name' : instance.group_name,
                },
            )


        
