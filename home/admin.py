from django.contrib import admin
from .models import Product, UserActivity

# Admin class for Product model
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')  # Fields to display in the list
    search_fields = ('name', 'category')  # Fields to search in the admin
    list_filter = ('category', 'created_at')  # Fields to filter by in the admin
    ordering = ('created_at',)  # Ordering by creation date, newest first

# Admin class for UserActivity model
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'action', 'timestamp')  # Fields to display in the list
    search_fields = ('user__username', 'product__name', 'action')  # Fields to search in the admin
    list_filter = ('action', 'timestamp')  # Fields to filter by in the admin
    ordering = ('-timestamp',)  # Ordering by timestamp, newest first

# Register the models and their respective admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(UserActivity, UserActivityAdmin)
