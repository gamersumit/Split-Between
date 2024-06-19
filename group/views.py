from functools import partial
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone
from .serializers import *
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from django.contrib.auth import authenticate
from user.models import User
from utils.utils import CommonUtils, Mail, UserUtils
from django.core.mail import send_mail
from django.contrib.auth.views import LogoutView as DRFLogoutView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.
class CreateGroupView(generics.CreateAPIView):
    serializer_class = GroupDeatilSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  # Include the request object in context
        icon = self.request.data.get('group_picture', None)
        if icon:
            try:
                icon = CommonUtils.UploadMediaToCloud(icon)
            except Exception as e:
                icon = None
        context['group_icon'] = icon # Include the request object in context
        return context
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "CREATE GROUP", operation_description = 'Create a new group to record all your expenses.', 
    ) 
    def post(self, request, *args, **kwargs):
        return  super().post(request, *args, **kwargs)
        
class SendGroupInvitationView(generics.CreateAPIView):
    serializer_class = PendingMembersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  # Include the request object in context
        return context
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "INVITE USERS TO JOIN GROUP", operation_description = 'Any group member can send invite to users to join their expense group. One User can only be invited by one group member at a time.', 
    ) 
    def post(self, request, *args, **kwargs):
        return  super().post(request, *args, **kwargs)
        