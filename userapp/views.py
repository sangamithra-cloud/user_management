from django.shortcuts import render, redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response as response
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.contrib import messages
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
import random 
import time

User = get_user_model()
OTP_STORE = {}


@api_view(['GET'])
def index(request):
    return render(request, 'index.html',{'request':request})



@api_view(['GET', 'POST'])
def user_signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')  # browser form

   
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return response({'message': 'All fields are required'}, status=400)

    if User.objects.filter(email=email).exists():
        return response({'message': 'Email already exists'}, status=400)

    otp = random.randint(100000, 999999)

    OTP_STORE[email] = {'otp': otp, 'timestamp': time.time()}

  
    user = User.objects.create_user(username=email, email=email, password=password, is_active=False)
    send_mail(
        "OTP Verification",
        f"Your OTP code is {otp}",
        'noreply@example.com',
        [email],
    )
    return redirect(f'/verify-otp/?email={email}')  


@api_view(['GET', 'POST'])
def verify_otp(request):
    if request.method == 'GET':
        return render(request, 'verify_otp.html') 
    OTP_VALIDITY = 3 * 60 
    email = request.data.get('email')
    otp = int(request.data.get('otp'))
    
    
    stored = OTP_STORE.get(email)
    if not stored:
        return response({'message': 'Invalid OTP'}, status=400)
    
    if time.time() - stored['timestamp'] > OTP_VALIDITY:
            OTP_STORE.pop(email)
            return response({'message': 'OTP expired'}, status=400)
    if stored['otp'] != otp:
             return response({'message': 'Invalid OTP'}, status=400)
    
    user = User.objects.get(email=email)
    user.is_active = True
    user.is_verified = True
    user.save()

    OTP_STORE.pop(email)
    return response({'message': 'Email verified successfully'})

@api_view(['GET', 'POST'])
def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return response({'message': 'Email and password are required'}, status=400)

    user = authenticate(request, email=email, password=password)

    if user is None:
        return response({'message': 'Invalid credentials'}, status=401)

    if not user.is_active:
        return response({'message': 'Account not verified'}, status=403)

    login(request, user)

    refresh = RefreshToken.for_user(user)

    return redirect('home')




def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('user_login')

@api_view(['GET'])
def home(request):
 
    if not request.user.is_authenticated:
        return redirect('/login/') 
   
    return render(request, 'home.html')

@api_view(['POST'])
def forgot_password(request):
        email = request.data.get("email")
        if not User.objects.filter(email=email).exists():
            return response({'message': 'Email does not exist'}, status=404)

        otp = random.randint(100000, 999999)
        OTP_STORE[email] = otp

        send_mail(
            "Password Reset OTP",
            f"Your password reset OTP code is {otp}",
            'noreply@example.com',
            [email]
        )
        return render(request,'verify_otp.html',{'email':email})



@api_view(['POST'])
def reset_password(request):
        email = request.data.get("email")
        otp = int(request.data.get("otp"))
        new_password = request.data.get("new_password")

        if OTP_STORE.get(email) != otp:
            return response({'message': 'Invalid OTP'}, status=400)

        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        OTP_STORE.pop(email)
        return response({'message': 'Password reset successfully'})
