from time import time
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required,user_passes_test
import json
import random
import time
from .models import Product, Cart, CartItem, Wishlist   
from django.db import transaction
from .brevo_email import send_email_brevo   

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
  
    return otp


@csrf_exempt
def health_check(request):
    return JsonResponse({"status": "ok", "message": "Service is running"})

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

    email = data.get("email")
    password = data.get("password")
    username = data.get("username")  
    
    print(email,password,username)

    if not email or not password:
        return JsonResponse({"status": "error", "message": "Email and password required"}, status=400)

    if User.objects.filter(email=email).exists():
        return JsonResponse({"status": "error", "message": "Email already exists"}, status=400)

    try:
        
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False
        user.save()

    except ValidationError as e:
        return JsonResponse({"status": "error", "message": e.messages}, status=400)

    otp = generate_otp(email)
    subject = "Your OTP Verification Code"
    html_content = f"<p>Hello {username},<br>Your OTP is <b>{otp}</b><br>It is valid for 5 minutes.</p>"

    try:
        status, resp = send_email_brevo(
            email, subject, html_content,
            sender_email="sangamithra@uniqnex360.com",
            sender_name="uniqnex360"
        )
    except Exception as e:
        return JsonResponse({"status": "error", "message": "Failed to send OTP email", "detail": str(e)}, status=500)

    if status not in [200, 201]:
        return JsonResponse({"status": "error", "message": "Brevo rejected email", "detail": resp}, status=500)

    request.session['verify_email'] = email
    request.session.set_expiry(300)
    
    print("User created and OTP sent via Brevo", otp)
    print("Brevo response:", resp)
    print("Session data:", request.session.items())
    
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
    
    subject = "Your OTP Verification Code - Resent"
    html_content = f"<p>Hello {username},<br>Your new OTP is <b>{otp}</b><br>It is valid for 5 minutes.</p>"
    status, resp = send_email_brevo(email, subject, html_content, 
                                    sender_email="sangamithra@uniqnex360.com",
                                     sender_name="uniqnex360")

    if status not in [200, 201]:
        return JsonResponse({"status": "error", "message": "Failed to send OTP email via Brevo", "detail": resp}, status=500)

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
     
    print(email,password)

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
    
    print(user.is_superuser)
    print(user.username)
    print(user.email)

    if user.is_superuser:
        return JsonResponse({
        "status": "success",
        "message": "Admin logged in successfully",
        "admin_dashboard_url": "/admin/dashboard/"  #
    })
    else:
        return JsonResponse({"status": "success", "message": "user Logged in successfully"})


@csrf_exempt
@login_required
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

    subject = "Your Password Reset OTP"
    html_content = f"<p>Hello,<br>Your OTP for password reset is <b>{otp}</b><br>It is valid for 5 minutes.</p>"
    status, resp = send_email_brevo(
        to_email=email,
        subject=subject,
        html_content=html_content,
        sender_email="sangamithra@uniqnex360.com",
        sender_name="uniqnex360"
    )
    
    if status not in [200, 201]:
        return JsonResponse({"status": "error", "message": "Failed to send OTP email via Brevo", "detail": resp}, status=500)

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
def edit_user(request, user_id): #Admin can edit user details
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


#add product 
@csrf_exempt
@login_required
@user_passes_test(is_admin)
def add_product(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    name = data.get("name")
    description = data.get("description")
    brand = data.get("brand")
    category = data.get("category")
    price = data.get("price")
    stock = data.get("stock")

    if not all([name, description, brand, category, price, stock]):
        return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)

    try:
        price = float(price)
        stock = int(stock)
    except ValueError:
        return JsonResponse({"status": "error", "message": "Invalid price or stock value"}, status=400)

    from userapp.models import Product  # Import here to avoid circular import

    product = Product.objects.create(
        name=name,
        description=description,
        brand=brand,
        category=category,
        price=price,
        stock=stock
    )

    return JsonResponse({"status": "success", "message": "Product added successfully", "product_id": product.id})

#to view all products
@csrf_exempt
@login_required
@user_passes_test(is_admin)
def view_all_product(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)
    products = Product.objects.all()
    products_data = [       
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "brand": p.brand,
            "category": p.category,
            "price": str(p.price),
            "stock": p.stock,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in products
    ]   
    return JsonResponse({"status": "success,To view all the products", "products": products_data})  

#to view a single product details
@csrf_exempt
@login_required     
@user_passes_test(is_admin)
def view_product(request, product_id):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "brand": product.brand,
        "category": product.category,
        "price": str(product.price),
        "stock": product.stock,
        "created_at": product.created_at,
        "updated_at": product.updated_at
    }

    return JsonResponse({"status": "success", "product": product_data})

@csrf_exempt
@login_required
@user_passes_test(is_admin)
def edit_product(request, product_id):
    if request.method != "PUT":
        return JsonResponse({"status": "error", "message": "Only PUT allowed"}, status=405)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    name = data.get("name")
    description = data.get("description")
    brand = data.get("brand")
    category = data.get("category")
    price = data.get("price")
    stock = data.get("stock")

    if name:
        product.name = name
    if description:
        product.description = description
    if brand:
        product.brand = brand
    if category:
        product.category = category
    if price is not None:
        try:
            product.price = float(price)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid price value"}, status=400)
    if stock is not None:
        try:
            product.stock = int(stock)
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid stock value"}, status=400)

    product.save()

    return JsonResponse({"status": "success", "message": "Product updated successfully"})

@csrf_exempt
@login_required 
@user_passes_test(is_admin)
def delete_product(request, product_id):        
    if request.method != "DELETE":
        return JsonResponse({"status": "error", "message": "Only DELETE allowed"}, status=405)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    product.delete()

    return JsonResponse({"status": "success", "message": "Product deleted successfully"})   


# User view to see products
@csrf_exempt
@login_required
def user_view_products(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)
    products = Product.objects.all()
    products_data = [       
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "brand": p.brand,
            "category": p.category,
            "price": str(p.price),
            "stock": p.stock,
            "created_at": p.created_at,
            "updated_at": p.updated_at
        }
        for p in products
    ]   
    return JsonResponse({"status": "success", "message": "To view all the products", "products": products_data})



@csrf_exempt 
@login_required
def add_to_cart(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({"status": "error", "message": "Quantity must be a positive integer"}, status=400)

    if not product_id:
        return JsonResponse({"status": "error", "message": "Product ID is required"}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    cart, _ = Cart.objects.get_or_create(user=request.user)

    with transaction.atomic():
       
        product = Product.objects.select_for_update().get(id=product_id)

        if product.stock < quantity:
            return JsonResponse({"status": "error", "message": "Insufficient stock"}, status=400)

        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

 
        product.stock -= quantity
        product.save()

    return JsonResponse({
        "status": "success",
        "message": "Product added to cart",
        "product_id": product.id,
        "quantity": cart_item.quantity
    })

@csrf_exempt
@login_required
def view_cart(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({"status": "success", "cart_items": []})  # Empty cart

    cart_items = CartItem.objects.filter(cart=cart)
    items_data = [
        {
            "product_id": item.product.id,
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price_per_item": str(item.product.price),
            "total_price": str(item.product.price * item.quantity)
        }
        for item in cart_items
    ]

    return JsonResponse({"status": "success", "cart_items": items_data})
@csrf_exempt
@login_required
def remove_from_cart(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    product_id = data.get("product_id")

    if not product_id:
        return JsonResponse({"status": "error", "message": "Product ID is required"}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Cart not found"}, status=404)

    try:
       with transaction.atomic():
         cart_item = CartItem.objects.get(cart=cart, product=product)
         quantity_to_restore = cart_item.quantity
         cart_item.delete()
         product.stock += quantity_to_restore
         product.save()

    except CartItem.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Item not in cart"}, status=404)

    return JsonResponse({"status": "success", "message": f"Product {product.name} removed from cart"})

@csrf_exempt
@login_required 
def add_to_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:    
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    product_id = data.get("product_id")
    if not product_id:
        return JsonResponse({"status": "error", "message": "Product ID is required"}, status=400)
    try:
        product = Product.objects.get(id=product_id)    
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return JsonResponse({"status": "success", "message": f"Product {product.name} added to wishlist"})




@csrf_exempt
@login_required
def view_wishlist(request):
    if request.method != "GET":
        return JsonResponse({"status": "error", "message": "Only GET allowed"}, status=405)

    try:
        wishlist = Wishlist.objects.get(user=request.user)
    except Wishlist.DoesNotExist:
        return JsonResponse({"status": "success", "wishlist_items": []})  # Empty wishlist

    products = wishlist.products.all()
    products_data = [
        {
            "product_id": p.id,
            "name": p.name,
            "description": p.description,
            "brand": p.brand,
            "category": p.category,
            "price": str(p.price),
            "stock": p.stock
        }
        for p in products
    ]

    return JsonResponse({"status": "success", "wishlist_items": products_data})

@csrf_exempt
@login_required 
def remove_from_wishlist(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    product_id = data.get("product_id")

    if not product_id:
        return JsonResponse({"status": "error", "message": "Product ID is required"}, status=400)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)

    try:
        wishlist = Wishlist.objects.get(user=request.user)
        wishlist.products.remove(product)
    except Wishlist.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Wishlist not found"}, status=404)

    return JsonResponse({"status": "success", "message": f"Product {product.name} removed from wishlist"})