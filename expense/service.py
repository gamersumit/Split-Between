from collections import defaultdict
from expense.serializers import ExpenseSerializer
from group.algorithms import UnionFind
from group.serializers import GroupBalenceSerializer
from user.serializers import UserMiniProfileSerializer
from .models import Activity, ExpenseContribution
from group.models import GroupBalance
from django.db.models import Q
from django.db import transaction
from django.db.models import Sum, F, Case, When, Value
from group.service import ActivityService
class ExpenseService:
    @staticmethod
    def add_expense(type, user , data): 
        # create an expense
        context = {
                   'user' : user,
                   'expense_type' : type
                   }
                
        expense_data = {
            'description' : data['descritpion'],
            'paid_by' : data['paid_by'],
            'group' : data['group'],
        }

        expense = ExpenseSerializer(data = expense_data, context=context)
        expense.is_valid(raise_exception=True)
        expense = expense.save()

        members = expense.group.members.all()
        
        if user not in  members:
            raise "Only Existing group members can add an expense to the group."
        
        contributions = []
        paid_to_users = {}

        # add contributions
        for contribution in data['contributions']:
            
            contributor = contribution['user']
            share_amount = contribution['share_amount']

            if contributor in members:
                contributions.append(ExpenseContribution(expense = expense, user = contributor, share_amount = contribution['share_amount']))
                expense.total_amount += share_amount
                if contributor != expense.paid_by:
                    paid_to_users[contributor.id] = {'share_amount' : share_amount}

        contributions = ExpenseContribution.objects.bulk_create(contributions, returning = True)
        expense.save()

        # add an activity
        activity_type = None
        metadata = {
                    'group_name' : expense.group_name, 
                    'amount' : expense.total_amount,
                },
                    
        if type == 'settleup':
            activity_type = 'settledup'
            {
                'with' : contributions.first().user.username
            }
            
        else:
            activity_type = 'expense_added'
            metadata = {
                    'expense_description' : expense.description,
                        }

        balances = ExpenseService.update_balances_after_adding_expense(paid_by=expense.paid_by, paid_to_users = paid_to_users, group=expense.group)
        activty = ActivityService.create_activity(type = activity_type, users = members, triggered_by = user, group = expense.group, metadata = metadata)
        return expense

    @staticmethod
    def update_balances_after_adding_expense(paid_by, paid_to_users, group):
        balances = group.balances.filter(
            Q(friend_owes=paid_by) | Q(friend_owns=paid_by))
        
        updated_balances = []
        
        for balance in balances:

            if balance.friend_owes == paid_by:
                friend =  paid_to_users.pop(balance.friend_owns.id, None)
                if friend:
                    balance.balance -= friend['share_amount']
                    updated_balances.append(balance)
        
            else :
                friend = paid_to_users.pop(balance.friend_owes.id, None)
                if friend:
                    balance.balance += friend['share_amount']
                    updated_balances.append(balance)
        
        # Perform bulk update
        if updated_balances:
            GroupBalance.objects.bulk_update(updated_balances, ['balance'])

        return updated_balances