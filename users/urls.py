from django.contrib import admin
from django.urls import path
from . import views
from users import views as user_views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('home/', views.home,name='home'),
    path('',views.user_login,name='root'),
    path('sell/',views.sell_product,name='sell_product'),
    path('my-products/',views.user_products,name='user_products'),
    path('delete-product/<int:product_id>',views.delete_product,name='delete_product'),
    path('logout/',views.user_logout,name='logout'),
    path('cart/',views.view_cart,name='view_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/add/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/checkout/<int:seller_id>/',views.checkout_seller,name='checkout_seller'),
    path('payment/execute/',views.execute_payment,name='execute_payment'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
