from django.urls import path
from . import views

urlpatterns = [
    path('get-variant/', views.get_product_variant, name='get_product_variant'),
    path('get-variation-price/', views.get_product_variation_price, name='get_product_variation_price'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),


    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.product_list, name='products_by_category'),
    path('brand/<slug:slug>/', views.product_list, name='products_by_brand'),
    path('categories/', views.category_list, name='category_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    
]