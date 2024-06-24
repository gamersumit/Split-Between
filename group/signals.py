from django.db.models.signals import pre_delete, pre_save, post_save, post_delete
from django.dispatch import receiver
from user.serializers import UserMiniProfileSerializer
from utils.utils import CommonUtils
from .models import GroupBalance, Membership, Group, PendingMembers
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

    if instance.group_icon:
         CommonUtils.delete_media_from_cloudinary([instance.group_icon])

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
    is_settled, all_balances, member_balances = GroupService.IsMemberSettledUp(group = instance.group, user=instance.user)
    
    if not is_settled:
        raise ValueError("Cannot leave group with outstanding balances: outstanding balances  will be calculated with SIMPLIFY feature OFF")

    all_balances.save()
    member_balances.delete()
    instance.group.pending_members.filter(invited_by = instance.user).delete()
    
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
    members = instance.group.members
    if not instance.pk and members:
        balance = []
        for member in members:
            balance.append(GroupBalance(group = instance.group, friend_owes=member.user, friend_owns=instance.user))
        
        if balance:
            GroupBalance.objects.bulk_create(balance)

@receiver(post_save, sender = Membership)
def create_member_added_activity(send, instance, created, **kwargs):
    if created and instance.group.members.count() > 1:
        activity = ActivityService.create_activity(
            type = 'member_added',
            group = instance.group,
            users = instance.group.members,
            metadata = {
                'added_by' : UserMiniProfileSerializer(instance.added_by).data,
                'user': UserMiniProfileSerializer(instance.user).data,
                'group_name' : instance.group.group_name,
                },
            )


@receiver(post_save, sender = Group)
def group_created_activity(sender, instance, created, **kwargs):
    if created:
        Membership.objects.create(user = instance.creator, group = instance, added_by = instance.creator)
        activity = ActivityService.create_activity(
            type = 'group_created',
            users = instance.members,
            group = instance,
            metadata = {
                'creator' : UserMiniProfileSerializer(instance.creator).data,
                'group_name' :  instance.group_name,
                },
            )

        
@receiver(post_save, sender = PendingMembers)
def group_invitation_sent_activity(send, instance, created, **kwargs):
    if created:
        activity = ActivityService.create_activity(
            type = 'member_invited',
            group = instance.group,
            users = instance.group.members,
            metadata = {
                'invited_by' : UserMiniProfileSerializer(instance.invited_by).data,
                'invited_user': UserMiniProfileSerializer(instance.user).data,
                },
            )