from functools import partial
from django.utils import timezone
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.utils import timezone
from .serializers import *
from .models import User
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
class RegisterView(generics.CreateAPIView) :
    serializer_class = UserRegistrationSerializer
    queryset = User.objects.all()
    
    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "REGISTER", operation_description = 'REGISTER YOURSELF TO USE OUR APPLICATION AND APIS', 
    responses={200: openapi.Response('Registeration Successful')},
    )       
    def post(self, request):
        try :
            response = super().post(request=request)   

            if response.status_code >= 200 and response.status_code < 300:
                UserUtils.sendMailVerificationLink(email = request.data['email'])
            
            return response    
        
        except Exception as e:
            return Response({'message' : str(e)}, status = 400)

class ResendEmailVerificationLink(generics.CreateAPIView):
    queryset = User.objects.all()

    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "SEND VERIFICATION LINK", operation_description = 'RESEND ACCOUNT VERIFICATION LINK', 
    responses={200: 'Link Sent to Registered email.'},
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['email'],
        )
    ) 
    def post(self, request):
        try : 
            email = request.data['email']
            user = User.objects.filter(email = email).first() 
           
            if not user:    
                raise Exception('Invalid Email ID')
            
            if user.is_verified:
                raise Exception('User Already Verified')

            UserUtils.sendMailVerificationLink(email = email)
            return Response({'message' : 'Link Sent to Registered email.'}, status=200)
        
        except Exception as e:
            return Response({'message' : str(e)}, status=400)

class UpdateUserProfileView(generics.GenericAPIView) :
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UserProfileEditSerializer
    @swagger_auto_schema(
    tags = ['User'],
    operation_summary= "EDIT PROFILE", operation_description = 'UPDATE FULL NAME OR PROFILE', 
    responses={200: openapi.Response('Profile Updated Succesfully', UserMiniProfileSerializer)},
    ) 
    def put(self, request):
        urls = []
        try :
            user = request.user
            current_avatar = None   
            data = {}

            if request.data.get('avatar', None):
                urls.append(CommonUtils.UploadMediaToCloud(request))
                data['avatar'] = urls[0]
                current_avatar =  user.avatar 

            if request.data.get('full_name', None):
                data['full_name'] = request.data['full_name']    

            if not dict:
                raise Exception('Zero fields provided')
            
            serializer = UserMiniProfileSerializer(user, data = data, partial = True)  
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            try :   
                if current_avatar:
                    CommonUtils.delete_media_from_cloudinary([current_avatar])
            except Exception as e:
                pass

            return Response({'message' : 'Profile Updated Succesfully', 'data' : serializer.data}, status = 200)
            
        except Exception as e:
            CommonUtils.delete_media_from_cloudinary(urls)
            return Response({'message' : str(e)}, status = 400)
        
#Login View
class LoginView(generics.GenericAPIView) :
    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "LOGIN", operation_description = 'GET LOGIN TOKEN AND USER DASHBOARD DETAILS ON LOGIN VIA EMAIL & PASSWORD', 
    responses = {
    200: openapi.Response(
        description="Successful response with token",
        schema=openapi.Schema(
            type='object',
            properties={
                'token': openapi.Schema(type='string')
            }
        )
    )
},
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ), )      
    
    def post(self, request, *args, **kwargs) :
        try :
            username = request.data['email']
            password = request.data['password']
            if not User.objects.filter(email = username).exists() :
               return Response({'status': False, 'message': 'New User'}, status=400)
                
            user = authenticate(password = password, username = username)
            
            if user:
                user.save()
                
                if not user.is_verified:
                    return Response({'status': False, 'message': 'Please verify your email first'}, status=403)
                
                if not user.is_active :
                    user.is_active = True
                    user.save()
                
                token, created = Token.objects.get_or_create(user=user)
                return Response({'token': token.key}, status = 200)
        
            else:
                return Response({'status': False, 'message': 'Invalid credentials'}, status=401)
        
        except Exception as e:
                return Response({'status': False, 'message': str(e)}, status=400)

# logout view // delete token       
class LogoutView(generics.RetrieveAPIView) :
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "LOGOUT", operation_description = 'Token Deletion', 
    responses={200: openapi.Response('User Logout Successfully')})       
    def get(self, request):
        try :
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Token '):
                token = auth_header.split(' ')[1]
                token = Token.objects.get(key = token)
                
                token.delete()
                return Response({'status': True, 'message': 'User Logout Successfully'}, status = 200)
            
            else :
                return Response({'status': False, 'message': 'Missing Token'}, status = 400)
        
        except Exception as e :
            return Response({'status': False, 'message': str(e)}, status = 400)
         

# ArtistSerializer --- to provide list of all artist
class SearchUsersView(generics.ListAPIView) :
    serializer_class = UserMiniProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        queryset = queryset.filter(username__icontains=username)
        return queryset
    

    @swagger_auto_schema(
        tags=['User'],
        operation_summary="SEARCH USER",
        operation_description='Results in User\'s detailed list based on search with username or select all with pagination',
        manual_parameters=[
            openapi.Parameter(
                name='username',  # name of the parameter
                in_=openapi.IN_QUERY,  # location of the parameter
                description='Username for search',  # description of the parameter
                type=openapi.TYPE_STRING,  # type of the parameter
                required=True,  # make it required
            ),
        ],
        responses={200: openapi.Response('LIST OF USERS', UserMiniProfileSerializer(many=True))}
    )
    def get(self, request):
        return super().get(request)


class CurrentUserDetailView(generics.GenericAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]  
    
    @swagger_auto_schema(
            tags = ['User'],
            operation_summary= "AUTHENTICATED USER\'S DETAILS", 
            operation_description = 'Provides details of current user with mini profile details of its follower and following')       
    def get(self, request):
        try:
            user = request.user
            serializer = self.serializer_class(user)
            return Response({'data' : serializer.data}, status = 200)
        
        except Exception as e:
            return Response({'message' : str(e)}, status = 400)



class SendPasswordResetOTPView(generics.UpdateAPIView):
    serializer_class = ForgotPasswordSerializer
    queryset = ForgotPasswordOTP.objects.all()
    http_method_names = ['put']
    
    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "OTP FOR PASSWORD RESET", operation_description = 'Sends OTP to the provided email in request body', 
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email'],
        ),
    responses={200: openapi.Response('OTP sent to your mail succesfully')})       
    def put(self, request):
        try:
            email = request.data['email']
            subject = 'Passwrod Reset Verfication Mail'
            body = CommonUtils.otp_generator()
            mail = Mail(subject, f'OTP: {str(body)}', [email])
            
            if User.objects.filter(email = email).exists():
                user = User.objects.get(email = email)
                
                if ForgotPasswordOTP.objects.filter(user = user.id).exists():
                    serializer = ForgotPasswordOTP.objects.get(user = user.id)
                    serializer.otp = body
                    
                else :
                    data = {'otp' : body, 'user_id' : user.id}
                    serializer = self.serializer_class(data = data)
                    serializer.is_valid(raise_exception=True)
                mail.send()
                serializer.save()
                return Response({'message' : 'OTP sent to your mail succesfully'}, status=200)
            
            else :
                raise Exception('EMAIL NOT FOUND')
            
        except Exception as e:
            return Response({'message' : str(e)}, status = 400)
    

class ResetPasswordTokenGenerationView(APIView):
    http_method_names = ['post']

    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "GET RESET PASSWORD TOKEN", operation_description = 'Generates a Token for the User from email and otp sent to their email to allow password resetting', 
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required= ['email', 'otp']
        ),
    responses={
            200: openapi.Response(
                description="Token generated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }) 

    def post(self, request):
        try :
            otp = request.data['otp']
            email = request.data['email']
            if User.objects.filter(email = email).exists():
                user = User.objects.get(email = email)
            else : raise Exception('email not found')
            
            if ForgotPasswordOTP.objects.filter(user_id = user.id).exists():
                obj = ForgotPasswordOTP.objects.get(user_id = user.id)
            else : raise Exception('try resending otp')
            
           
            if obj.isExpired():
                raise Exception('otp expired')
            
            if obj.otp != int(otp):
                raise Exception('incorrect otp')
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token' : str(token)}, status = 200)
        
        except Exception as e:
            return Response({'message': str(e)}, status = 400)
        
class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    @swagger_auto_schema(tags = ['Auth'], 
    operation_summary= "RESET PASSWORD", operation_description = 'JUST SEND YOUR NEW PASSWORD WITH THE TOKEN IN AUTHORIZATION HEADERS', 
    responses={
            200: 'password reset successfully'
        },
    request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['password'],
        ),        
        )
    def patch(self, request):
        try :
            token = Token.objects.get(key = request.headers['Authorization'].split(" ")[1])
            user = token.user
            data = {'password' : request.data['password']}
            serializer = UserRegistrationSerializer(user, data = data, partial = True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        
            return Response({'message' : 'password reset successfully'}, status = 200)
        except Exception as e:
            return Response({'message': str(e)}, status = 400)


class MailVerifyView(generics.GenericAPIView):
    http_method_names = ['get']
    queryset = None
    pagination_class = None
    @swagger_auto_schema(
        tags = ['Auth'], 
        operation_summary= "VERIFY EMAIL",
        operation_description = 'VERIFY YOUR MAIL BY CLICKING LINK SENT TO YOUR REGISTERED EMAIL', 
        responses={200: 'Verification Successful'},
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="Verification Token",
                type=openapi.TYPE_STRING,  # Specify your choices here
            ),
        ],
        ) 
    def get(self, request, *args, **kwargs):
        try : 
            token = request.GET['token']
            token = MailVerificationToken.objects.filter(token = token).first()
            if not token:
                raise Exception("Invalid Link")

            if token.isExpired():
                raise Exception("Link Expired")  

            user = token.user
            user.is_verified = True
            user.save()
            token.delete()
            return  Response({'message' : 'Verification Successful'}, status=200)
        
        except Exception as e:
            return Response({'message' : str(e)}, status=400)

        

