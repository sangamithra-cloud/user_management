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
    path('admin/', admin.site.urls),   #built-in admin route
    path('',views.index, name='index'),                           # /
    path('signup/', views.user_signup, name='user_signup'),        # /signup/
    path('verify-otp/', views.verify_otp, name='verify_otp'),     # /verify-otp/
    path('login/', views.login_view, name='user_login'),           # /login/
    path('logout/', views.logout_view, name='logout'),            # /logout/
    path('home/', views.home, name='home'),                        # /home/
    path('forgot-password/', views.forgot_password, name='forgot_password'), # /forgot-password/
    path('reset-password/', views.reset_password, name='reset_password'),    # /reset-password/

    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),       # View/Search users
    path('admin-dashboard/users/<int:user_id>/', views.edit_user, name='edit_user'),   # Edit user details
    path('admin-dashboard/users/<int:user_id>/block/', views.block_user, name='block_user'),
 # Block/Unblock user

]