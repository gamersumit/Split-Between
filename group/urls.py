from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateGroupView.as_view(), name = 'create-group'),
    path('invite/', views.SendGroupInvitationView.as_view(), name = 'group-invitation'),
    path('join/<str:id>', views.JoinGroupView.as_view(), name = 'group-invitation'),
    path('drop-invitation/<str:id>', views.DeleteInvitaionView.as_view(), name = 'drop-invitation'),
    path('list/', views.JoinedGroupsListView.as_view(), name = 'user-activities'),
    path('activity/list/', views.UserActivityListView.as_view(), name = 'list-groups'),
    path('<str:id>/', views.JoinedGroupDetailView.as_view(), name = 'group-details'),
    path('edit/<str:field>/<str:id>/', views.UpdateGroupDetailsView.as_view(), name = 'simplify-debts'),
    
]