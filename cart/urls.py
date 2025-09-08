from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<str:cart_key>/', views.update_cart, name='update_cart'),
]