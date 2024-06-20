from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone

from group.service import ActivityService
from .serializers import *
from rest_framework import permissions
from django.contrib.auth import authenticate
from user.models import User
from utils.utils import CommonUtils, UserUtils
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
    operation_summary= "INVITE USERS TO JOIN GROUP", 
    operation_description = 'Any group member can send invite to users to join their expense group. One User can only be invited by one group member at a time.', 
    ) 
    def post(self, request, *args, **kwargs):
        return  super().post(request, *args, **kwargs)
        
class JoinGroupView(generics.RetrieveAPIView):
    serializer_class = MembershipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user  # Include the request object in context
        return context
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "JOIN GROUP BY INVITAION ID", 
    operation_description = 'Any group member can send invite to users to join their expense group. One User can only be invited by one group member at a time.', 
    ) 
    def get(self, request, *args, **kwargs):
        try:
            id = kwargs['id']
            invite = PendingMembers.objects.get(id = id)
            if invite.user != request.user :
                return Response({'error' : 'invitation not found'}, status=404)
            
            member = Membership.objects.create(user = request.user.id, group = invite.group, added_by = invite.invited_by)
            invite.delete()
            return Response(MembershipSerializer(member).data, status=200)
        except Exception as e:
            return Response({'error' : str(e)}, status=400)
        
class DeleteInvitaionView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        try :
            id = self.kwargs['id']
            invite = PendingMembers.objects.get(id = id)

            if invite.user != self.request.user or invite.user not in invite.group.members:
               return PendingMembers.objects.none() 

            return PendingMembers.objects.all()
    
        except Exception as e:
            return PendingMembers.objects.none()
    
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "DELETE PENDING INVITATION", 
    operation_description = 'Any group member or invited user can delete an invitaion.', 
    ) 
    def delete(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            users = list(self.object.group.members.all())
            users.append(self.object.user)
            metadata = {
                        'delete_by' : request.user,
                        'invitation_for' :  self.object.user,
                        'group_name' : self.object.group.group_name,
                        }
            with transaction.atomic():
                ActivityService.create_activity(type = 'invitation_dropped', users = users, group=self.object.group, metadata = metadata)
                response = super().delete(request, *args, **kwargs) 
            
            return response
        except Exception as e:
            return Response({'error' : str(e)}, status=400)

class JoinedGroupsListView(generics.ListAPIView):
    serializer_class = GroupMiniDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return self.request.user.groups_membership.all()
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "LIST OF JOINED GROUPS", 
    operation_description = 'PROVIDES A LIST OF ALL THE GROUPS WHERE THE CURRENT USER IS MEMBER.', 
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class JoinedGroupDetailView(generics.RetrieveAPIView):
    serializer_class = GroupDeatilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return self.request.user.groups_membership.all()
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "DETAILS OF A JOINED GROUPS", 
    operation_description = 'PROVIDES ALL THE DETAILS OF A GROUP BY GROUP_ID WHERE THE CURRENT USER IS MEMBER.', 
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)