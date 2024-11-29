from django.contrib import admin
from .models import Product, Order, CustomUser,Cart,OrderItem
from .forms import CustomUserCreationForm
# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','price','image','description')



class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    list_display = ['username', 'email', 'address', 'phone']
    fieldsets = (
        (None, {'fields': ('username', 'password', 'email', 'address', 'phone')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'address', 'phone'),
        }),
    )     
class CartAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','total_price'] 

class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','total_price','livre','disponible','order_date']        
admin.site.register(Cart,CartAdmin)    
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(OrderItem,OrderItemAdmin)
