from django.contrib import admin
from .models import User, Category, Product, Cart, ShoppingCart, Order, OrderItem
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address')}),
    )
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(ShoppingCart)
admin.site.register(Order)
admin.site.register(OrderItem)
