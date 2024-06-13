from .models import User, Balance
from django.db import transaction
from django.db.models import Q
from django.db import transaction

class FriendshipService:
    
    @staticmethod
    def get_balances_for_user_and_friends(user):
        """
        Retrieve balances where the specified user is either the 'friend_owes' or 'friend_owns'.

        Args:
        user (User): The user for whom balances are retrieved.

        Returns:
        QuerySet: QuerySet of Balance objects where 'user' is either 'friend_owes' or 'friend_owns'.

        Example:
        ```
        user = User.objects.get(username='example_user')
        balances = FriendshipService.get_balances_for_user_and_friends(user)
        ```
        """
        balences = Balance.objects.filter(Q(friend_owes=user) | Q(friend_owns=user))
        return balences

    @staticmethod
    def get_balances_for_user_and_specific_friends(user, friend_ids):
        """
        Retrieve balance objects between a user and their friends based on friend IDs.

        Args:
        user (User): The user whose balances are to be retrieved.
        friend_ids (list): List of friend IDs.

        Returns:
        QuerySet: QuerySet of Balance objects involving the user and their friends.
        """
        
        # Fetch Balance objects where user is either friend_owes or friend_owns
        balances = Balance.objects.filter(
            Q(friend_owes=user, friend_owns__id__in=friend_ids) |
            Q(friend_owns=user, friend_owes__id__in=friend_ids)
        )

        return balances

    @staticmethod
    def bulk_add_friends(user, friends):
        """
        Bulk create Balance objects to represent friendships between a user and multiple friends.

        Args:
        user (User): The user initiating the friendships.
        friends (list): List of User objects representing friends to add.

        Note:
        Excludes the user itself from being added as a friend.
        """
        friendships = [Balance(friend_owes=user, friend_owns=friend) for friend in friends if friend != user]

        with transaction.atomic():
            Balance.objects.bulk_create(friendships)

    @staticmethod
    def bulk_update_balances(payer, payments):
        """
        Bulk update balances where a single user pays multiple friends.

        Args:
        payer (User): The user making the payments.
        payments (dict): Dictionary where keys are User instances representing friends,
                        and values are amounts paid (float).

        Example:
        ```
        payer = User.objects.get(username='example_payer')
        payments = {
            User.objects.get(username='friend1'): 50.0,
            User.objects.get(username='friend2'): 30.0,
            User.objects.get(username='friend3'): 20.0,
        }
        FriendshipService.bulk_update_balances(payer, payments)
        ```

        Process:
        - Uses `transaction.atomic()` to ensure all operations are atomic, meaning they succeed or fail together.
        - Calls `FriendshipService.get_balances_for_user_and_specific_friends()` to retrieve relevant Balance objects.
        - Iterates through the retrieved friends and updates their balances based on whether they owe or are owed by `payer`.
        - Saves the updated balances in bulk to minimize database queries using `QuerySet.update()`.

        """
        with transaction.atomic():
            # Retrieve or create the corresponding Friendship instance
            friends = FriendshipService.get_balances_for_user_and_specific_friends(user = payer, friend_ids= payments.keys())
            for friend in  friends:
                if friend.friend_owes == payer :
                    friend.balance += payments[f'{friend.friend_owns.id}']

                else :
                    friend.balance -= payments[f'{friend.friend_owes.id}']
                

            # Save the updated friendships
            friends.save(update_fields=['balance'])
            