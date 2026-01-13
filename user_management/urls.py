"""
URL configuration for user_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
from userapp import views
from django.contrib import admin


urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('admin/', admin.site.urls),   #built-in admin route
    path('',views.index, name='index'),                           # /
    path('signup/', views.user_signup, name='user_signup'),        # /signup/
    path('verify-otp/', views.verify_otp, name='verify_otp'),     # /verify-otp/
    path('login/', views.login_view, name='user_login'),           # /login/
    path('logout/', views.logout_view, name='logout'),            # /logout/
    path('resend-otp/', views.resend_otp, name='resend_otp'),      # /resend-otp/
    path('forgot-password/', views.forgot_password, name='forgot_password'), # /forgot-password/
    path('reset-password/', views.reset_password, name='reset_password'),    # /reset-password/

    #admin can edit and block user routes
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),       # View/Search users
    path('admin-dashboard/users/<int:user_id>/', views.edit_user, name='edit_user'),   # Edit user details
    path('admin-dashboard/users/<int:user_id>/block/', views.block_user, name='block_user'),# Block/Unblock user
   
   # ADMIN  Product management routes
    path('admin-dashboard/products/add/', views.add_product, name='add_product'),   # Add product
    path('admin-dashboard/products/', views.view_all_product, name='view_products'),  # View all products
    path('admin-dashboard/products/<int:product_id>/', views.view_product, name='view_product'), # View product details
    path('admin-dashboard/products/<int:product_id>/edit/', views.edit_product, name='edit_product'), # Edit product
    path('admin-dashboard/products/<int:product_id>/delete/', views.delete_product, name='delete_product'), # Delete product

    # User routes
    path("user/products/", views.user_view_products, name="user_view_products"),  # View products

]