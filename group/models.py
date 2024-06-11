import datetime
import uuid
from django.utils import timezone
from django.db import models

from user.models import User


# Create your models here.
class Group(models.Model): 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    groupname = models.CharField(max_length = 50)
    friends = models.ManyToManyField(User, related_name='groups',blank=True)
    is_simplified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.groupname
