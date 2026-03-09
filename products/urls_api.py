from django.urls import path
from . import views_api

urlpatterns = [
    # Product listing and filtering
    path('products/', views_api.ProductListView.as_view(), name='api_product_list'),
    path('products/<slug:slug>/', views_api.ProductDetailView.as_view(), name='api_product_detail'),
    
    # Filter options
    path('filters/', views_api.get_filter_options, name='api_filter_options'),
    
    # Related products
    path('products/<int:product_id>/related/', views_api.get_related_products, name='api_related_products'),
    path('products/<int:product_id>/frequently-bought/', views_api.get_frequently_bought, name='api_frequently_bought'),
]