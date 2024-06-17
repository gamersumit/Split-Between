from rest_framework import serializers

from utils.utils import UserUtils
from .models import *
from rest_framework.serializers import ValidationError



class UserMiniProfileSerializer(serializers.ModelSerializer) :
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name'
            'avatar',
        ]
        read_only_fields = ['id', 'username']

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'username',
            'full_name'
        ]
    
    def validate_password(self, value):
       return UserUtils.validate_password(value)
    
class UserProfileSerializer(UserMiniProfileSerializer):
    class Meta(UserMiniProfileSerializer.Meta):
        model = User
        fields = UserMiniProfileSerializer.Meta.fields + ['email']

class FriendshipSerializer(serializers.ModelSerializer):
    friend_owes = UserMiniProfileSerializer(read_only = True)
    friend_owns = UserMiniProfileSerializer(read_only = True)
    
    class Meta:
        model = ForgotPasswordOTP
        fields = '__all__'
        read_only_fields = ['id', 'friend_owes', 'friend_owns', 'created_at']


class ForgotPasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ForgotPasswordOTP
        fields = '__all__'
        read_only_fields = ['id', 'user', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
