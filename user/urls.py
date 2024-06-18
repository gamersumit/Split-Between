from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('register/', views.RegisterView.as_view(), name = 'register'),
    path('verification/link/', views.ResendEmailVerificationLink.as_view(), name = 'send-verification-link'),
    path('verify/mail/', views.MailVerifyView.as_view(), name = 'verify-mail'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('send/password/otp/', views.SendPasswordResetOTPView.as_view(), name = 'reset_password_otp_mail'),
    path('reset/password/token/', views.ResetPasswordTokenGenerationView.as_view(), name = 'reset_password_token'),
    path('reset/password/', views.ResetPasswordView.as_view(), name = 'reset_password'),
    path('logout/', views.LogoutView.as_view(), name = 'logout'),
    path('', views.CurrentUserDetailView.as_view(), name = 'current_user_detail'),
    path('search/', views.SearchUsersView.as_view(), name = 'search_users'),
    path('edit/', views.UpdateUserProfileView.as_view(), name = 'edit_profile'),
]