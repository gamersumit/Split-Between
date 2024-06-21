from rest_framework import serializers
from user.serializers import UserMiniProfileSerializer
from utils.utils import UserUtils
from .models import *
from rest_framework.serializers import ValidationError


class GroupBalenceSerializer(serializers.ModelSerializer):
    friend_owes = UserMiniProfileSerializer(read_only = True)
    friend_owns = UserMiniProfileSerializer(read_only = True)
    class Meta:
        model = GroupBalance
        fields = '__all__'
        
class PendingMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingMembers
        fields = '__all__'
        read_only_fields = ['id', 'invited_by', 'date_invited']

    def create(self, validated_data):
        validated_data['invited_by'] = self.context['user']
        members = validated_data['group'].members
        if self.context['user'] not in members:
            raise ValidationError("Group not found")
        
        if self.validated_data['user'] in members:
            raise ValidationError("Already a member of the group")
        return super().create(validated_data)

class MembershipSerializer(serializers.ModelSerializer):
    user = UserMiniProfileSerializer(read_only=True)
    class Meta:
        model = Membership
        fields = '__all__'
        
    def get_balance(self):
        pass

class GroupMiniDetailSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Group
        fields = [
            'id',
            'group_name',
            'group_icon',
            
        ]
        read_only_fields = ['id']


class GroupEditSerializer(serializers.Serializer):
    name = serializers.CharField(max_length = 50, required = False)
    description = serializers.CharField(required = False)
    icon = serializers.FileField(required = False)
        
    class Meta:
        fields = '__all__'

class GroupDeatilSerializer(serializers.ModelSerializer):
    balances = serializers.SerializerMethodField(read_only = True)
    group_picture = serializers.FileField(required = False, default = None, write_only = True)
    members = MembershipSerializer(read_only = True, many = True)
    pending_members = PendingMembersSerializer(read_only = True, many = True)
    # total_expense
    # monthly_expense
    # expenses 
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['id', 'total_spending','group_icon', 'admin', 'creator', 'created_at', 'is_deleted', 'members']


    def get_balances(self):
        from group.service import GroupService
        return GroupService.format_group_balances_for_all_members(group=self)

    def create(self, validated_data):
        validated_data['admin'] = self.context['user']
        validated_data['creator'] = self.context['user']
        validated_data['group_icon'] = self.context.get('group_icon', None)
        return super().create(validated_data)


class ActivitySerializer(serializers.ModelSerializer) :
    group = GroupMiniDetailSerializer(read_only=True)
    class Meta:
        model = Activity
        exclude = ['users']
        