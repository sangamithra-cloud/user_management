

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
  
    email=models.EmailField(unique=True)
  
    is_blocked=models.BooleanField(default=False)
    is_email_verified=models.BooleanField(default=False) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class OTPVerification(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)
    expires_at=models.DateTimeField()  
