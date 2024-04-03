from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import *  

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_description','slug')
    search_fields = ('category_name',)
    list_display_links = ('category_name', 'category_description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'price', 'availability','slug')
    list_filter = ('price', 'availability', 'category')
    search_fields = ('product_name',)
    list_editable = ('price', 'availability')
    list_display_links = ('product_name', 'category')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_price', 'order_date',)
    list_filter = ('quantity', 'order_date')
    search_fields = ('product__product_name',)
    list_display_links = ('product',)

@admin.register(CustomUser)
class CustomUserAdmin1(admin.ModelAdmin):
    list_display = ('email','first_name','last_name','is_admin')

 
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'email', 'message')

    def get_fields(self, request, obj=None):
        # Show the 'message' field only to admin users
        if request.user.is_superuser:
            return ('name', 'mobile', 'email', 'message')
            
        else:
            return ('name', 'mobile', 'email', 'message')

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_active', 'date_joined', 'last_login', 'is_staff')

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register the custom admin for the default User model
admin.site.register(User, CustomUserAdmin)

