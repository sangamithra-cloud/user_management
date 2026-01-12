from time import time
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,user_passes_test
import json
import random
import time

User = get_user_model()


# Temporary OTP store
OTP_STORE = {}
OTP_VALIDITY = 300  # 5 minutes

def generate_otp(email):
    otp = random.randint(100000, 999999)
    OTP_STORE[email] = {
        "otp": otp,
        "timestamp": time.time()
    }
    print(f"OTP for {email}: {otp}")  # Console shows OTP for Postman
    return otp

@csrf_exempt
def index(request):
    return JsonResponse({"status": "success", "message": "Welcome to User Management System"})




@csrf_exempt
def user_signup(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST requests allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)

    if User.objects.filter(username=email).exists():
        return JsonResponse({"status": "error", "message": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)

    # Create inactive user
    user = User.objects.create_user(username=username, email=email, password=password)
    user.is_active = False
    user.save()

    # Generate OTP
    otp=generate_otp(email)

    try:
        send_mail(
            "Your OTP Verification Code",
            f"Hello {username},\n\nYour OTP is: {otp}\nIt is valid for 5 minutes.",
            "sangamithra@uniqnex360.com",  
            [email],
            fail_silently=False,
        )
    except Exception as e:
     
        return JsonResponse({"status": "error", "message": "Failed to send OTP email"}, status=500)
    request.session['verify_email'] = email
    request.session['username'] = username
    request.session.set_expiry(300) 

    return JsonResponse({"status": "success", "message": "User created successfully"}, status=201)




@csrf_exempt
def verify_otp(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return JsonResponse({"status": "error", "message": "Email and OTP required"}, status=400)

    stored = OTP_STORE.get(email)
    if not stored:
        return JsonResponse({"status": "error", "message": "Invalid OTP"}, status=400)

    if time.time() - stored['timestamp'] > OTP_VALIDITY:
        OTP_STORE.pop(email)
        return JsonResponse({"status": "error", "message": "OTP expired"}, status=400)

    if str(stored['otp']) != str(otp):
        return JsonResponse({"status": "error", "message": "Invalid OTP"}, status=400)

    try:
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        OTP_STORE.pop(email)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    return JsonResponse({"status": "success", "message": "Email verified successfully"})


@csrf_exempt
def resend_otp(request):
    email = request.session.get('verify_email')
    username = request.session.get('username')
    if not email:
        return JsonResponse({"status": "error", "message": "Session expired. Please signup again."})

    otp = random.randint(100000, 999999)
    OTP_STORE[email] = {'otp': otp, 'timestamp': time.time()}

    try:
        send_mail(
            "Your OTP Verification Code",
            f"Hello {username},\n\nYour OTP is: {otp}\nIt is valid for 5 minutes.",
            "sangamithra@uniqnex360.com",  
            [email],
            fail_silently=False,
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": "Failed to send OTP email"}, status=500)

    return JsonResponse({"status": "success", "message": f"New OTP sent to {email}"})


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return JsonResponse({"status": "error", "message": "Email and password are required"}, status=400)

    user = authenticate(request, username=email, password=password)  # or use username=email if auth backend supports
    if not user:
        return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)

    if not user.is_active:
        return JsonResponse({"status": "error", "message": "Account not verified"}, status=403)

    if getattr(user, 'is_blocked', False):
        return JsonResponse({"status": "error", "message": "Your account has been blocked. Contact admin."}, status=403)

    login(request, user)

    if user.is_superuser:
        return JsonResponse({
        "status": "success",
        "message": "Admin logged in successfully",
        "admin_dashboard_url": "/admin/dashboard/"  #
    })
    else:
        return JsonResponse({"status": "success", "message": "user Logged in successfully"})


@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "success", "message": "Logged out successfully"})


@login_required
def home(request):
    return JsonResponse({"status": "success", "message": f"Welcome {request.user.username}"})

@csrf_exempt
def forgot_password(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    email = data.get('email')
    if not email:
        return JsonResponse({"status": "error", "message": "Email is required"}, status=400)

    if not User.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "message": "Email does not exist"}, status=404)

    otp = random.randint(100000, 999999)
    OTP_STORE[email] = {'otp': otp, 'timestamp': time.time()}

   
   

    
    send_mail(
        "Password Reset OTP",
        f"Your OTP is {otp}",
        'noreply@example.com',
        [email],
    )

    request.session['reset_email'] = email
  
    return JsonResponse({"status": "success", "message": f"OTP sent to {email}"})

    



@csrf_exempt
def reset_password(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    # Get email from session
    email = request.session.get('reset_email')
    if not email:
        return JsonResponse({"status": "error", "message": "Session expired. Please try again."}, status=400)

    # Parse JSON from request body
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    otp_input = data.get('otp')
    new_password = data.get('new_password')

    if not otp_input or not new_password:
        return JsonResponse({"status": "error", "message": "OTP and new password are required"}, status=400)

    stored = OTP_STORE.get(email)
    if not stored:
        return JsonResponse({"status": "error", "message": "OTP not found. Request again."}, status=400)

    if str(stored['otp']) != str(otp_input):
        return JsonResponse({"status": "error", "message": "Invalid OTP"}, status=400)

    if time.time() - stored['timestamp'] > OTP_VALIDITY:
        OTP_STORE.pop(email)
        return JsonResponse({"status": "error", "message": "OTP expired. Request again."}, status=400)

    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        OTP_STORE.pop(email)
        request.session.flush()  # clear session after password reset
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    return JsonResponse({"status": "success", "message": "Password reset successful ,login with new password"})




#Admin Views 

def is_admin(user):
    return user.is_superuser



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    search_query = request.GET.get("search", "")
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query)
        )

    users_data = [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active,
            "is_blocked": getattr(u, "is_blocked", False),
            "is_superuser": u.is_superuser
        }
        for u in users
    ]
    return JsonResponse({"status": "success", "users": users_data})



@csrf_exempt
@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id): #edit user details
    if request.method != "PUT":
        return JsonResponse({"status": "error", "message": "Only PUT allowed"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    username = data.get("username")
    email = data.get("email")
    is_active = data.get("is_active")

    if username:
        user.username = username
    if email:
        user.email = email
    if is_active is not None:
        user.is_active = is_active

    user.save()
   

    return JsonResponse({"status": "success", "message": "User updated successfully"})




@csrf_exempt
@login_required
@user_passes_test(is_admin)
def block_user(request, user_id):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"status": "error", "message": "User not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    block = data.get("block", True)
    setattr(user, "is_blocked", bool(block))
    user.save()

    status_msg = "blocked" if block else "unblocked"
    return JsonResponse({"status": "success", "message": f"User {status_msg} successfully"})



