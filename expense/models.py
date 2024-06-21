import datetime
import uuid
from django.utils import timezone
from django.db import models

from user.models import User
from group.models import Group

# Create your models here.
class Expense(models.Model):
    """
    Represents an expense within a group.

    There are two types of expense:
    1. Setlle up expense : where a user settle ups his/her balences with other user 
    2. Group Expense : where allor some user of a group contributed to an expense

    If case 1:
        Represents a settlement between users within a group.

        This model tracks settlements made between users within a group,
        including details such as the users involved in the settlement, the amount settled,
        and the timestamp of creation.
    
    If case 2:
        This model tracks individual expenses made by users within a group,
        including details such as the amount, the user who paid for the expense,
        the user who created the expense, and the timestamp of creation.

    Attributes:
        id (UUID): The unique identifier for the expense.
        group (ForeignKey): The group to which the expense belongs.
        paid_by (ForeignKey): The user who paid for the expense.
        created_by (ForeignKey): The user who created the expense.
        amount (FloatField): The amount of the expense.
        settled_with (ForeignKey): The user with whom the settlement is made if expense type is settleup.
        created_at (DateTimeField): The date and time when the expense was created.
        updated_at (DateTimeField): The date and time when the expense was last updated.
    """
    EXPENSE_CHOICES = [
        ('group_expense', 'Group Expense'),
        ('settleup', 'Settle Up'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense_type = models.CharField(max_length=40, choices=EXPENSE_CHOICES, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses', editable=False)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_owners')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_creators', editable=False)
    contributors = models.ManyToManyField(User, related_name='contributed_expenses', through='ExpenseContribution')
    settled_with = models.OneToOneField(User, on_delete=models.CASCADE, related_name='expense_settled_with', null=True, blank=True)
    automatic = models.BooleanField(default=False)
    total_amount = models.FloatField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ExpenseContribution(models.Model):
    """
    Represents a contribution made towards an expense.

    This model tracks individual contributions made by users towards an expense,
    including details such as the user who made the contribution and the amount contributed.

    Attributes:
        expense (ForeignKey): The expense to which the contribution belongs.
        user (ForeignKey): The user who made the contribution.
        share_amount (FloatField): The amount contributed by the user towards the expense.
    """
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    share_amount = models.FloatField(default = 0)



