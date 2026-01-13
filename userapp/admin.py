from django.contrib import admin
from .models import User, OTPVerification, Product, Cart, CartItem, Wishlist    
admin.site.register(User)
admin.site.register(OTPVerification)
admin.site.register(Product)        
admin.site.register(Cart)
admin.site.register(CartItem)   
admin.site.register(Wishlist)
