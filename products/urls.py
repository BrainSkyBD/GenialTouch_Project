from django.urls import path
from . import views

urlpatterns = [
    path('get-variant/', views.get_product_variant, name='get_product_variant'),
    path('get-variation-price/', views.get_product_variation_price, name='get_product_variation_price'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),


    # path('category/<slug:slug>/', views.product_list, name='products_by_category'),
    # path('brand/<slug:slug>/', views.product_list, name='products_by_brand'),

    path('', views.product_list, name='product_list'),
    path('category/<slug:slug>/', views.products_by_category, name='products_by_category'),
    path('brand/<slug:slug>/', views.products_by_brand, name='products_by_brand'),

    # path('load-more/', views.load_more_products, name='load_more_products'),

    path('products/load-more/', views.load_more_products, name='load_more_products'),


    path('categories/', views.category_list, name='category_list'),
    path('brands/', views.brand_list, name='brand_list'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),

    # AJAX endpoints
    path('ajax/frequently-bought/', views.get_frequently_bought, name='get_frequently_bought'),
    path('ajax/related-products/', views.get_related_products, name='get_related_products'),
    path('ajax/tab-content/', views.get_tab_content, name='get_tab_content'),
    path('ajax/variation-price/', views.get_product_variation_price, name='get_product_variation_price'),
    path('ajax/quick-add-to-cart/', views.quick_add_to_cart, name='quick_add_to_cart'),

    path('ajax/reviews-content/', views.get_reviews_content, name='get_reviews_content'),
    path('product/<int:product_id>/review/submit/', views.submit_review, name='submit_review'),
    path('ajax/review/helpfulness/', views.review_helpfulness, name='review_helpfulness'),
    path('ajax/reviews/load-more/', views.load_more_reviews, name='load_more_reviews'),
    
    

    
]