from django.contrib import admin
from .models import Order, Product


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer_name', 'order_date', 'total_amount', 'order_status', 'gift', 'total_amount_sum_notified')
    list_filter = ('order_date', 'order_status', 'gift', 'total_amount_sum_notified')
    search_fields = ('order_id', 'customer_name', 'order_status')  # Add other fields you want to search by
    ordering = ('-order_date',)  # Sort by order_date in descending order


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',  'image')
    search_fields = ('name', )  # Add other fields you want to search by


admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
