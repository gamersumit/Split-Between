from django.urls import path
from . import views



urlpatterns = [
    path('create/', views.CreateGroupView.as_view(), name = 'create-group'),
    path('invite/<str:group>/<str:user>', views.SendGroupInvitationView.as_view(), name = 'group-invitation'),
    
]