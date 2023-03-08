from django.contrib import admin
from .models import UserDetail, Address,Product, Category, Cart, CartItem, Order, Coupon, Wishlist, Banner

admin.site.register(UserDetail)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(Wishlist)
admin.site.register(Banner)