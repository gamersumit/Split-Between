from collections import defaultdict
from group.algorithms import UnionFind
from group.serializers import GroupBalenceSerializer
from user.serializers import UserMiniProfileSerializer
from .models import Activity, GroupBalance
from django.db.models import Q
from django.db import transaction
from django.db.models import Sum, F, Case, When, Value
class GroupService:
    @staticmethod 
    def simplify_balances(group):
        users = set()
        edges = []
        balances = group.balances
        for balance in balances:
            users.add(balance.friend_owes_id)
            users.add(balance.friend_owns_id)
            edges.append((balance.balance, balance.friend_owes_id, balance.friend_owns_id))
        
        users = list(users)
        users_map = {user: idx for idx, user in enumerate(users)}
        n = len(users)
        
        uf = UnionFind(n)
        
        # Step 3: Sort edges by balance (amount owed)
        edges.sort()
        
        # Step 4: Apply Kruskal's algorithm to find the MST
        mst = []
        total_cost = 0
        
        for cost, u, v in edges:
            if uf.union(users_map[u], users_map[v]):
                mst.append((cost, u, v))
                total_cost += cost
        
        # Step 5: Format the result into GroupBalance objects
        simplified_balances = []
        for cost, u, v in mst:
            # Assuming balance is positive if u owes v, negative if v owes u
            if cost > 0:
                simplified_balances.append(GroupBalance(
                    group=group,
                    friend_owes_id=u,
                    friend_owns_id=v,
                    balance=cost
                ))
            else:
                simplified_balances.append(GroupBalance(
                    group=group,
                    friend_owes_id=v,
                    friend_owns_id=u,
                    balance=-cost  # Make sure balance is positive
                ))
        
        return simplified_balances

    @staticmethod
    def IsGroupSettledUp(group):
        """
        Check if all balances in the group are settled up.

        Args:
        group (Group): The group object for which balances are to be checked.

        Returns:
        bool: True if all balances are settled (zero), False otherwise.
        """
        return not GroupService.get_group_balances(group=group).filter(balance__ne=0).exists()
    
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
        return not GroupBalance.get_group_balances(group=group).filter(
            Q(friend_owes=user) | Q(friend_owns=user),
            balance__ne=0
        ).exists()

    @staticmethod
    def format_user_balence_in_the_group(group, user):
        balances = GroupService.get_all_group_members_balences(group = group)
        return balances.get(user, [])

    @staticmethod
    def format_group_balances_for_all_members(group):
        balances = GroupService.get_group_balances(group = group)
        all_balances = defaultdict(list)
        
        for balance in  balances:
            friend_owes = balance.friend_owes
            friend_owns = balance.friend_owns

            balance = GroupBalenceSerializer(balance).data    

            all_balances[friend_owes].append(balance)
            all_balances[friend_owns].append(balance)

        return all_balances
        
    @staticmethod
    def get_group_balances(group):
        if group.is_simplified:
            return GroupService.simplify_balances(group=group)
        return group.balances

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
    

    