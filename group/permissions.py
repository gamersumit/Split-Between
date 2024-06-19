
# from math import perm
# from rest_framework import permissions

# from utils.utils import UserUtils
# import json

# # class for normal user / Audiance
# class IsGroupMember(permissions.IsAuthenticated):
#     permission_queryset = None

#     perms_map = {
#        # 'GET': [],   // original
#         'OPTIONS': [],
#         'HEAD': [],
#         'GET': ['%(app_label)s.view_%(model_name)s'],
#         'POST': ['%(app_label)s.add_%(model_name)s'],
#         'PUT': ['%(app_label)s.change_%(model_name)s'],
#         'PATCH': ['%(app_label)s.change_%(model_name)s'],
#         'DELETE': ['%(app_label)s.delete_%(model_name)s'],
#     }

#     def has_permission(self, request, view):
#         try :
#             # Write permissions are only allowed to the owner of the playlist.
#             return super().has_permission and request.user intoken_user.id)
        
#         except Exception as e:
#             return False
        
