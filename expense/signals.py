# from django.db.models.signals import pre_delete, pre_save
# from django.dispatch import receiver
# from .models import Expense, ExpenseContribution



# @receiver(pre_save, sender=ExpenseContribution)
# def create_exspense(sender, instance, created, **kwargs):
#     if created:
#         (instance.expense.paid_by, payments = {f'{instance.user.id}' : instance.share_amount})
        