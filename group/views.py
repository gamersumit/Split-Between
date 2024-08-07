from rest_framework import generics
from rest_framework.response import Response
from group.service import ActivityService
from .serializers import *
from rest_framework import permissions, status
from utils.utils import CommonUtils
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
        try:
            with transaction.atomic():
                return  super().post(request, *args, **kwargs)
        
        except Exception as e:
            print("error in group creation: ", str(e))
            return Response({'error': str(e)}, status=500)

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
        try:
            with transaction.atomic() :
                return  super().post(request, *args, **kwargs)
        
        except ValidationError as e :
            return Response({'error' : str(e)}, status=403)
            
        except Exception as e:
            return Response({"error" : str(e)}, status=500)
        
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
            
            with transaction.atomic():
                member = Membership.objects.create(user = request.user, group = invite.group, added_by = invite.invited_by)
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
    lookup_field = 'id'
    def get_queryset(self):
       return self.request.user.groups_membership.all()
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "DETAILS OF A JOINED GROUPS", 
    operation_description = 'PROVIDES ALL THE DETAILS OF A GROUP BY GROUP_ID WHERE THE CURRENT USER IS MEMBER.', 
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class RemoveMemberFromGroupView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Membership.objects.all()
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "REMOVE OR LEAVE GROUP", 
    operation_description = 'REMOVE ANY MEMBER FROM GROUP OR LEAVE GROUP YOURSELF.', 
    ) 
    def delete(self, request, *args, **kwargs):
        try:
            member = self.get_object()
            type = None
            metadata = {'who' : UserMiniProfileSerializer(member.user), 'group_name' : member.group.group_name}
            
            if request.user == member.user : 
                type = 'left_group'

            elif request.user in member.group.members :
                type = 'removed_from_group'
                metadata = {'by' : UserMiniProfileSerializer(request.user)}

            else:
                return Response({'error' : 'member not found'}, status=404)

            with transaction.atomic():
                ActivityService.create_activity(type = type, group=member.group, users = member.group.members, metadata=metadata)
                member.delete()
                return Response({'message' : 'Request Succesful'}, status=204)
        
        except Exception as e:
            return Response({'error' : str(e)}, status=500)

class DeleteGroupView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return self.request.user.groups_membership.all()
    
    @swagger_auto_schema(tags = ['Group'], 
    operation_summary= "DELETE A GROUP", 
    operation_description = 'DELETE A SETTLED GROUP(GROUP IN WHICH OUTSATNDING BALANCES ARE ZERO) WHERE CURRENT USER IS MEMBER.', 
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
class UpdateGroupDetailsView(generics.UpdateAPIView):

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = GroupEditSerializer
    lookup_field = 'id'
    http_method_names = ['patch']
    def get_queryset(self):
        return self.request.user.groups_membership

    @swagger_auto_schema(
    tags=['Group'],
    operation_summary="TURN ON/OFF SIMPLIFY DEBTS",
    operation_description='DISABLE OR ENABLE SIMPLIFICATION OF BALANCES IN THE GROUP.',
    responses={200: openapi.Response(description='Success', schema=GroupDeatilSerializer)}
    )
    def patch(self, request, *args, **kwargs):
        try:
            group = self.get_object()
            field = kwargs.get('field', None)
            print("request.data ===>", request.data)
            if field not in ['name', 'description', 'icon', 'simplified']:
                return Response({'error': 'PAGE NOT FOUND'}, status=400)
            

            type = None
            icon = None
            metadata = {'updated_by' : {
                                'username' : request.user.username, 
                                'id' : str(request.user.id),
                            }, 'group_name' : group.group_name}
            print("metadata ===>", metadata)
            response = {'message' : 'request successful'}
            
            
            if field  == 'simplified':
                type = 'group_simplified'
                group.is_simplified =  not group.is_simplified   
                from .service import GroupService
                balances = GroupService.format_group_balances_for_all_members(group)
                response = {'state': group.is_simplified, 'balances' : balances}
            
            if field == 'name' :
                type = 'changed_group_name'
                group.group_name = request.data['name']
                metadata['new_name'] = group.group_name
                
            if field == 'description' :
                type = 'changed_group_description'
                group.description = request.data['description']
            
            if field == 'icon' :
                icon = CommonUtils.UploadMediaToCloud(request.data['icon'])
                type = 'changed_group_icon'
                group.group_icon = icon
                response = {'group_icon' : icon}
                
            try:    
                with transaction.atomic():
                    group.save()
                    ActivityService.create_activity(type=type, group = group, triggered_by= request.user, users=group.members.all(), metadata=metadata)
            
            except Exception as e:
                if icon:
                    CommonUtils.delete_media_from_cloudinary([icon])

                raise Exception(str(e))
            return Response(response, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
       return self.request.user.activites.all()
    
    @swagger_auto_schema(tags = ['Activity'], 
    operation_summary= "LIST OF ALL THE ACTIVITY", 
    operation_description = 'PROVIDES A LIST OF ALL THE GROUP ACTIVITIES CONCERNING CURRENT USER WHERE THE CURRENT USER IS MEMBER OF THE GROUP.', 
    ) 
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

