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
            return super().create(validated_data)

class MembershipSerializer(serializers.ModelSerializer):
    user = UserMiniProfileSerializer(read_only=True)
    balance = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = Membership
        fields = '__all__'

    def get_balance(self):
        pass

class GroupMiniDetailsSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Group
        fields = [
            'id',
            'group_name',
            'group_icon',
            
        ]
        read_only_fields = ['id']


class GroupDeatilSerializer(serializers.ModelSerializer):
    members = MembershipSerializer(read_only = True, many = True)
    group_picture = serializers.FileField(required = False, default = None, write_only = True)
    class Meta:
        model = Group
        fields = '__all__'
        read_only_fields = ['id', 'total_spending','group_icon', 'admin', 'creator', 'created_at', 'is_deleted', 'is_simplified', 'members']


    def create(self, validated_data):
        validated_data['admin'] = self.context['user']
        validated_data['creator'] = self.context['user']
        validated_data['group_icon'] = self.context.get('group_icon', None)
        return super().create(validated_data)
