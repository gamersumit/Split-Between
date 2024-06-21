import datetime
import uuid
from django.utils import timezone
from django.db import models
from user.models import User
from django.db import transaction
# Create your models here.
class Group(models.Model): 
    """
    Represents a group in the system.

    A group can have multiple members and is used to organize users
    based on shared interests or purposes.

    Attributes:
        id (UUID): The unique identifier for the group.
        group_name (str): The name of the group.
        group_description (str): A brief description of the group.
        is_deleted (bool): Indicates whether the group has been marked as deleted.
        
        admin (ForeignKey): Represents the user who is the admin of the group.
        
        creator (ForeignKey): Represents the user who created the group.

        created_at (DateTimeField): Represents the date and time when the group was created.
        
        members (ManyToManyField): The users who are members of the group. 
            This field establishes a many-to-many relationship between the Group model 
            and the User model, allowing a group to have multiple users as members, 
            and a user to belong to multiple groups. 
            The 'through' parameter specifies the intermediary model ('Membership') 
            that manages the relationship, including additional fields such as 
            'added_by', date_joined, and 'invitation_accepted' to provide more information 
            about the relationship between users and groups.

    
        is_simplified (bool): Indicates whether the group's expenses are simplified 
            by consolidating debts among members. When enabled, the system calculates 
            and displays the net balances between each pair of members after canceling 
            out debts, ensuring that individuals don't have to make direct payments 
            to each other for shared expenses.
            Example:
                Suppose we have a group with three members: A, B, and C.
                - A owes $200 to B.
                - A owes $200 to C.
                - C owes $100 to B.
                Without simplification, each individual would need to directly settle their debts with others:
                - A pays $200 to B.
                - A pays $200 to C.
                - C pays $100 to B.
                However, with simplification enabled, we consolidate the debts:
                - A's net balance with B: $300 (owed to B)
                - A's net balance with C: $100 (owed to C)

    Signals:
        pre_delete: Signal receiver `check_settle_up_before_group_deletion` checks if there are outstanding balances
            before deleting the group instance.
        
        pre_delete: Signal receiver `check_settle_up_before_leaving_group` checks if there are outstanding balances
            before removing a member from the group.
        
        pre_save: Signal receiver `create_friendships_before_membership` creates friendships between the new member
            and existing group members before saving a new membership instance.
    """


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length = 50, null = False, blank=False)
    group_icon = models.URLField(null = True, blank = True)
    group_description = models.CharField(max_length=200, null =True, blank=True)
    members = models.ManyToManyField(User, related_name='groups_membership', through = 'Membership', through_fields=('group', 'user'),  blank=True)
    pending_members = models.ManyToManyField(User, related_name='groups_pending', through = 'PendingMembers', through_fields=('group', 'user'),  blank=True)
    total_spending = models.FloatField(default=0)
    is_simplified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    admin = models.ForeignKey(User, null = False, blank=False, editable=False, on_delete= models.CASCADE, related_name='group_admin')
    creator = models.ForeignKey(User, null = False, blank=False, editable=False, on_delete= models.CASCADE, related_name='group_creator')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    
    def __str__(self):
        return self.group_name

class Membership(models.Model):
    """
    Represents the membership of a user in a group.

    This model tracks the relationship between users and groups,
    including details such as the user who added the member and
    whether the membership invitation has been accepted.

    Attributes:
        user (ForeignKey): The user who is added as a member of the group.
          - editable=False: Prevents direct editing of the user field.
          - on_delete=models.CASCADE: Deletes the membership if the associated user is deleted.
          - related_name='members': Allows reverse querying from the User model to access all memberships.

        group (ForeignKey): The group to which the user belongs.
          - editable=False: Prevents direct editing of the group field.
          - on_delete=models.CASCADE: Deletes the membership if the associated group is deleted.
          - related_name='membership': Allows reverse querying from the Group model to access all memberships.

        added_by (ForeignKey): The user who added the member to the group.
          - editable=False: Prevents direct editing of the added_by field.
          - on_delete=models.CASCADE: Deletes the membership if the associated added_by user is deleted.
          - related_name='added_membership': Allows reverse querying from the User model to access all memberships added by this user.

        
        date_joined (DateTimeField): The date and time when the user joined the group.
          - null=True, blank=True: Allows the date_joined field to be nullable and blank initially.

    Methods:
        __str__: Returns a string representation of the membership instance indicating details like user, added_by, and invitation_accepted.

    Signals:
        pre_save: Signal receiver `create_friendships_before_membership` creates friendships between the new member and existing group members before saving a new membership instance.

        pre_delete: Signal receiver `check_settle_up_before_leaving_group` checks if there are outstanding balances
            before removing a member from the group.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='Membership')
    group = models.ForeignKey(Group, editable=False, on_delete=models.CASCADE)
    added_by = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='added_membership')
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} is a member of {self.gorup}"
    class Meta:
      unique_together = ('group', 'user')

class PendingMembers(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='invitaions')
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    invited_by = models.ForeignKey(User, editable=False, on_delete=models.CASCADE, related_name='invited_by')
    date_invited = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user} invited by {self.added_by} to {self.group} group"
    

    class Meta:
      unique_together = ('group', 'user')

class GroupBalance(models.Model):
    """
    Model representing the balance between two friends within a group context.

    Fields:
    - group (ForeignKey): A reference to the Group model, representing the group to which this balance belongs.
      - related_name='balances': Allows reverse querying from the Group model to access all related GroupBalance instances.
      - null=False, blank=False: Ensures the field is mandatory.
      - editable=False: Prevents editing of the field in admin forms.
      - on_delete=models.CASCADE: Deletes the related GroupBalance instances when the Group is deleted.
    
    - friendship (ForeignKey): A reference to the Friendship model, representing the friendship relation for this balance.
      - related_name='balances': Allows reverse querying from the Friendship model to access all related GroupBalance instances.
      - null=False, blank=False: Ensures the field is mandatory.
      - on_delete=models.CASCADE: Deletes the related GroupBalance instances when the Friendship is deleted.
    
    - balance (FloatField): A float field representing the balance amount between the two friends in the group.
      - default=0: Sets the default value of the balance to 0.

    Methods:
    - __str__: Returns a string representation of the GroupBalance instance.

    Meta:
    - unique_together: Ensures that each combination of group and friendship has a unique GroupBalance record.
    """
    group = models.ForeignKey(Group, related_name='balances', null=False, blank=False, editable=False, on_delete=models.CASCADE)
    friend_owes = models.ForeignKey(User, editable=False, on_delete=models.CASCADE,  related_name='balence_owes')
    friend_owns = models.ForeignKey(User, editable = False, on_delete=models.CASCADE,  related_name='balence_owns')
    balance = models.FloatField(default=0)

    def __str__(self):
        return f"Group: {self.group.group_name}, Friendship: {self.friend_owes, self.friend_owns}, Balance: {self.balance}"

    class Meta:
        unique_together = ('group', 'friend_owes', 'friend_owns')


class Activity(models.Model):
    ACTIVITY_CHOICES = (
        ('group_created', 'Group Created'),
        ('group_info_edited', 'Group Inforamtion Edited'),
        ('group_deleted', 'Group Deleted'),
        ('member_invited', 'Member Invited to Join Group'),
        ('invitation_dropped', 'Reject/Cancel Invitation to Join Group'),
        ('member_added', 'Member Added to Group'),
        ('member_left', 'Member Left Group'),
        ('expense_added', 'Expense Added to Group'),
        ('expense_edited', 'Expense Edited in Group'),
        ('expense_deleted', 'Expense Deleted from Group'),
        ('group_invitation_received', 'Group Invitation Received'),
        ('settled_up_with_user', 'Settled Up with User'),
        # Add more choices as needed
    )
    id = models.UUIDField(primary_key=True, editable=False)
    activity_type = models.CharField(null = False, blank=False, max_length=40, choices=ACTIVITY_CHOICES)
    group = models.ForeignKey(Group, null = True, default = None, on_delete=models.SET_NULL)
    users = models.ManyToManyField(User, symmetrical=False, related_name='activites')
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    metadata = models.JSONField(null = True, blank=True, default=dict)
    
    def __str__(self):
        return f"{self.users} - {self.activity_type} - {self.created_at}"
