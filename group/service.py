from user.models import Friendship
from user.serializers import UserMiniProfileSerializer
from .models import Activity, GroupBalance
from django.db.models import Q
from django.db import transaction
from datetime import datetime
from django.db.models import Sum, F, Case, When, Value
class GroupService:

    @staticmethod
    def IsGroupSettledUp(group):
        """
        Check if all balances in the group are settled up.

        Args:
        group (Group): The group object for which balances are to be checked.

        Returns:
        bool: True if all balances are settled (zero), False otherwise.
        """
        return not group.balances.filter(balance__ne=0).exists()
    
    @staticmethod
    def IsMemberSettledUp(group, user):
         """
        Check if a specific member in the group has settled up with all other members.

        Args:
        group (Group): The group object in which balances are to be checked.
        user (User): The user whose balances with other members are to be checked.

        Returns:
        bool: True if the user has settled up with all other members, False otherwise.
        """
         return not group.balances.filter(
            Q(friendship__friend_owes=user) | Q(friendship__friend_owns=user),
            balance__ne=0
        ).exists()

    @staticmethod
    def get_group_member_balances(group):
        # Annotate each user's total amount owed and owned within the group
        balances = GroupBalance.objects.filter(group=group).values(
            'friendship__friend_owes'
        ).annotate(
            total_owes=Sum(
                Case(
                    When(friendship__friend_owes=F('friendship__friend_owes'), then=F('balance')),
                    default=Value(0)
                )
            ),
            total_owns=Sum(
                Case(
                    When(friendship__friend_owns=F('friendship__friend_owes'), then=F('balance')),
                    default=Value(0)
                )
            )
        ).values(
            user=F('friendship__friend_owes'),
            total_owes=F('total_owes'),
            total_owns=F('total_owns'),
            net_balance=F('total_owns') - F('total_owes')
        )

        return balances

    @staticmethod
    def edit_group_info(user, group, name = None, description = None):
        if user not in group.members:
            raise Exception('Group does\'nt exists')

        if (not name and not description ) or (name and description):
            raise Exception('Only Name or Description is editable at a time')
        
        
        metadata = {
                'updated_by' : UserMiniProfileSerializer(user).data,
                'group_name' : group.group_name,
                }
        
        if name:
            group.group_name = name
            metadata = {'field' : 'group_name', 'new_name' : name}
        
        else:
            group.description = description
            metadata = {'field' : 'description'}

        
        activity = ActivityService.create_activity(
            type = 'group_info_edited',
            users = group.members,
            group=group,
            metadata=metadata
            )
        
        with transaction.atomic():
            group.save() 
            activity.save()

        return activity, group


    @staticmethod
    def delete_group(user, group):
        if user not in group.members:
            raise Exception('Group does\'nt exists')
        
        metadata = {
                'deleted_by' : UserMiniProfileSerializer(user).data,
                'group_name' : group.group_name,
                },
        
        activity = ActivityService.create_activity(
            type = 'group_deleted',
            users = group.members,
            metadata=metadata
            )
        
        with transaction.atomic():
            group.delete()
            activity.save()

        return activity

class ActivityService:
    @staticmethod
    def create_activity(type, users, group = None, metadata = {}):
        activity = Activity.objects.create(
            activity_type = type,
            group = group,
            metadata = metadata,
            )
        
        activity.user.add(*users)
        return activity
    

    