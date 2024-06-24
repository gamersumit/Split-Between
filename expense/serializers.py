from rest_framework import serializers
from user.serializers import UserMiniProfileSerializer
from utils.utils import UserUtils
from .models import *
from rest_framework.serializers import ValidationError

class ExpenseContributionSerializer(serializers.ModelSerializer):
    user = UserMiniProfileSerializer()
    class Meta:
        model = ExpenseContribution
        exclude = ['expense']


class ExpenseHistorySerializer(serializers.ModelSerializer):
    updated_by = UserMiniProfileSerializer()
    class Meta:
        model = ExpenseHistory
        exclude = ['expense']
        

class ExpenseSerializer(serializers.ModelSerializer):
    contibutions = ExpenseContributionSerializer(read_only = True, many = True)
    history = ExpenseHistorySerializer(read_only = True, many = True)
    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'expense_type', 'created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['user']
        validated_data['expense_type'] = self.context['expense_type']
        return super().create(validated_data)
        
