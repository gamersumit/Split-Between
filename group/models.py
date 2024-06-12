import datetime
import uuid
from django.utils import timezone
from django.db import models

from user.models import User


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
        
        members (ManyToManyField): The users who are members of the group. 
            This field establishes a many-to-many relationship between the Group model 
            and the User model, allowing a group to have multiple users as members, 
            and a user to belong to multiple groups. 
            The 'through' parameter specifies the intermediary model ('Membership') 
            that manages the relationship, including additional fields such as 
            'added_by', date_joined and 'invitation_accepted' to provide more information 
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
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length = 50, null = False, blank=False)
    group_description = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name='groups', through = 'Membership', blank=True)
    total_spending = models.FloatField(default=0)
    is_simplified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.group_name


class Membership(models.Model):
    """
    Represents the membership of a user in a group.

    This model tracks the relationship between users and groups,
    including details such as the user who added the member and
    whether the membership invitation has been accepted.

    Attributes:
        user (ForeignKey): The user who is a member of the group.
        group (ForeignKey): The group to which the user belongs.
        added_by (ForeignKey): The user who added the member to the group.
        invitation_accepted (bool): Indicates whether the membership invitation has been accepted.
        date_joined (DateTimeField): The date and time when the user joined the group.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='members')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='membership')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='added_membership')
    invitation_accepted = models.BooleanField(default=False)
    date_joined = models.DateTimeField(null = True, blank=True)


    def __str__(self):
        return "self.user added by {self.added_by}: invitation_accepted: {self.invitation_accepted}."
    


class Activity(models.Model):
    activity_types = ()