import secrets
from django.contrib.auth.hashers import make_password
import random
from cloudinary import uploader
from rest_framework.response import Response
import os
import cloudinary
import cloudinary.api
from user.models import MailVerificationToken, User
from  rest_framework import serializers
from django.core.mail import send_mail
from config.settings import base
import re



class UserUtils :

    @staticmethod
    def validate_password(value):
    # valid password : >= 8 char, must contains lower at least 1 char of each 
    # lower(alpha), upper(alpha), (number), (symbols)
    
    # will uncomment later : ---- !>
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        if  not re.search(r"\d", value) :
            raise serializers.ValidationError("Password must contains a number 0 to 9")
        
        if not re.search("[a-z]", value) :
            raise serializers.ValidationError("Password must contain a lowercase letter ")
        
        if not re.search("[A-Z]", value) :
            raise serializers.ValidationError("Password must contain a uppercase letter")
        
        if not re.search(r"[@#$%^&*()\-_+=.]", value):
            raise serializers.ValidationError("Password must contain a special character(@,#,$,%,^,&,*,(,),-,_,+,=,.)")

        return make_password(value)    # return hashed password
    

    
    @staticmethod
    def sendMailVerificationLink(email):
        token = secrets.token_urlsafe(32)
        user = User.objects.get(email = email)
        base_endpoint = os.getenv('BASE_ENDPOINT')
        print(os.getenv('BASE_ENDPOINT'))
        verification_link = base_endpoint+'user/verify/mail/'+f'?token={token}'
        print("link ======>", verification_link)
        body = f"""
Dear {user.username},

Thank you for registering with SPLIT BETWEEN. Please click the link below to verify your email address:

{verification_link}

If you did not create an account with us, please ignore this email.

Thank you,
Split-Between Team
        """         
        try :
            print("link ===>", verification_link)
            obj = MailVerificationToken.objects.filter(user = user).first()
            
            print("obj ===>", obj)
            if obj:
                obj.token = token  
                
            else:    
                obj = MailVerificationToken(user = user, token=token)
            
            obj.save()
            print("send =======")

            message = Mail(
                subject = 'Please Verify Your Email Address',
                body = body,
                emails = [email]
                )
            message.send()
            
        except Exception as e:
            print("error ===> ", str(e))
            pass



class CommonUtils:
    
    @staticmethod
    def UploadMediaToCloud(media):
        try : 
            path = f'public/split/avatar'
            upload = uploader.upload_large(media, folder = path, use_filename = True)   
            return upload['secure_url']
        
        except Exception as e:
            raise Exception(str(e))   
           
    @staticmethod
    def delete_media_from_cloudinary(urls):
        try :
            public_ids = [url[url.index('public/'):] for url in urls]
            response = cloudinary.api.delete_resources(public_ids, resource_type = 'raw')
             
        except Exception as e:
            pass
    
    @staticmethod
    def otp_generator():
        otp = random.randint(100001, 999999)
        return otp
    


class Mail:
    
    def __init__(self, subject, body, emails):
        self.subject = subject
        self.body = body
        self.emails = emails
    
    
    def send(self):
        
        send_mail(
            self.subject, 
            self.body,
            base.EMAIL_HOST_USER,
            self.emails,
            fail_silently=False)
        
