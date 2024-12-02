from django.urls import path
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from. import views
from django.conf.urls import handler404, handler500, handler403, handler400

urlpatterns = [
    path('', views.home, name='home'),
    path('order/<int:product_id>/', views.place_order, name='place_order'),
    path('orders/', views.view_orders, name='view_orders'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/download/<int:order_id>/', views.download_order_pdf, name='download_order_pdf'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='shop/login.html'), name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/signup/', views.signup, name='signup'),
    path('products/', views.product_list, name='product_list'),
    path('cart-content/', views.get_cart_content, name='get_cart_content'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/cart/', views.order_from_cart, name='order_from_cart'),
    path('cgu/', lambda request: render(request, 'shop/cgu.html'), name='cgu'),
]
if settings.DEBUG :
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.conf.urls import handler404, handler500, handler403, handler400

# Spécifie les vues des pages d'erreur
handler404 = 'myapp.views.custom_404'
handler500 = 'myapp.views.custom_500'
handler403 = 'myapp.views.custom_403'
handler400 = 'myapp.views.custom_400'
