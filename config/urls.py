"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from rest_framework import permissions, authentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static


# from user.views import PatchLogoutView

schema_view = get_schema_view(
    openapi.Info(
        title="Split your bills between Friends",
        # description='These are all the apis available to work with innotune. The backend also includes websockets to provide real-time updates on friends activities, such as their online/offline status and the songs they are currently listening to. However, since swagger does not support websocket documentation, these websocket endpoints are not included here. the apis cover various functionalities, including song management, user interactions, and playlist operations.\n\nSUPPORT: sumitaggarwal12022002@gmail.com',  
        default_version="v1",
    ),
    url = settings.BASE_ENDPOINT,
    public = True, # shows views which can be accessed by current user
    # permission_classes= [permissions.IsAuthenticated],
    # authentication_classes = [authentication.SessionAuthentication,authentication.TokenAuthentication]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # rest framework inbuilt
    path('rest/', include('rest_framework.urls', namespace='rest_framework')),
   
    # Swagger
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)