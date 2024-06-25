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
    expense_type = models.CharField(max_length=40, choices=EXPENSE_CHOICES)
    description = models.CharField(max_length = 250, default = 'Expense')
    total_amount = models.FloatField(default = 0)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, null = False, related_name='expense_owners')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='expenses')
    contributors = models.ManyToManyField(User, related_name='contributed_expenses', through='ExpenseContribution')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_creators')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contributions')
    share_amount = models.FloatField(default = 0)

    class Meta:
        unique_together = ('expense', 'user')

class ExpenseHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='expense_history')
    updated_by =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='expense_history')
    updated_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null = True, blank=True, default=dict)


