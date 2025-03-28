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
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
