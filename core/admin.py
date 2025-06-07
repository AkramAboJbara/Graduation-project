from django.contrib import admin

from chatbot.models import Review
from .models import User, Category, Product, Cart, CartItem, Order, OrderItem
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address')}),
    )
    
admin.site.register(Review)

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Price Range'
    parameter_name = 'price_range' 

    def lookups(self, request, model_admin):
        return [
            ('0-100', '0 - 100'),
            ('100-500', '100 - 500'),
            ('500+', '500+'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-100':
            return queryset.filter(price__gte=0, price__lte=100)
        elif self.value() == '100-500':
            return queryset.filter(price__gt=100, price__lte=500)
        elif self.value() == '500+':
            return queryset.filter(price__gt=500)
        return queryset

class StockRangeFilter(admin.SimpleListFilter):
    title = 'Stock Level'
    parameter_name = 'stock_range'

    def lookups(self, request, model_admin):
        return [
            ('low', 'Low Stock (0 - 10)'),
            ('medium', 'Medium Stock (10 - 50)'),
            ('high', 'High Stock (50+)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock__gte=0, stock__lte=10)
        elif self.value() == 'medium':
            return queryset.filter(stock__gt=10, stock__lte=50)
        elif self.value() == 'high':
            return queryset.filter(stock__gt=50)
        return queryset







class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('category', PriceRangeFilter, StockRangeFilter) 
  
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
