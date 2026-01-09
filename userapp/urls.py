
from django.urls import path
from userapp.views import index, user_signup, verify_otp, login_view, logout_view, home, forgot_password, reset_password

urlpatterns = [
    path('', index, name='index'),                  # /
    path('signup/', user_signup, name='user_signup'),   # /signup/
    path('verify-otp/', verify_otp, name='verify_otp'), # /verify-otp/
    path('login/', login_view, name='user_login'),     # /login/
    path('logout/', logout_view, name='logout'),        # /logout/
    path('home/', home, name='home'),                  # /home/
    path('forgot-password/', forgot_password, name='forgot_password'), # /forgot-password/
    path('reset-password/', reset_password, name='reset_password'),    # /reset-password/
]
