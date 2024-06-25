from rest_framework import generics
from django.db import transaction
from rest_framework.response import Response
from expense.service import ExpenseService
from .serializers import *
from rest_framework import permissions
from drf_yasg.utils import swagger_auto_schema

# Create your views here.


# 1. Add Expense
# 2. EDIT expense
# 3. Delete Expense

class AddExpenseView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags = ['Expense'], 
    operation_summary= "ADD AN EXPENSE", 
    operation_description = 'ADD AN EXPENSE TO THE GORUP'  
    ) 
    def post(self, request, *args, **kwargs):
        try:
            data = None
            with transaction.atomic():
                expense = ExpenseService.add_expense(type = 'group_expense', data = request.data, user = request.user)   
                data = self.serializer_class(expense).data

            return Response({"data" : data}, status = 204) 
        except Exception as e:
            return Response({'error' : str(e)}, status=500)
        
class SettleUpView(generics.CreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags = ['Expense'], 
    operation_summary= "SETTLE UP", 
    operation_description = 'SETTLE WITH A GROUP MEMBER'  
    ) 
    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            data = {'contributions' : [data.pop('contribution')]}
            with transaction.atomic():
                expense = ExpenseService.AddExpense(type = 'settleup', data = request.data, user = request.user)   
                data = self.serializer_class(expense).data

            return Response({"data" : data}, status = 204) 
        except Exception as e:
            return Response({'error' : str(e)}, status=500)

class ExpenseListView(generics.ListAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return self.request.user.groups_membership.filter(id = self.kwargs['id']).expenses
    
    @swagger_auto_schema(tags = ['Activity'], 
    operation_summary= "LIST OF ALL THE EXPENSES", 
    operation_description = 'PROVIDES A LIST OF ALL THE GROUP EXPENSES.'  
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)