from rest_framework import serializers

from utils.utils import UserUtils
from .models import *
from rest_framework.serializers import ValidationError


class UserProfileEditSerializer(serializers.ModelSerializer):
    avatar = serializers.FileField(required=False)
    class Meta:
        model = User
        fields = ['full_name', 'avatar']
class UserMiniProfileSerializer(serializers.ModelSerializer) :
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'full_name',
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


class ForgotPasswordSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ForgotPasswordOTP
        fields = '__all__'
        read_only_fields = ['id', 'user', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['user']
        return super().create(validated_data)
