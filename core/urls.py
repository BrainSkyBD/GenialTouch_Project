from django.urls import path
from django.views.generic import TemplateView
from products import views as product_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),

    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),

    path('load-deals-section/', views.load_deals_section, name='load_deals_section'),
    path('load-category-products-section/<str:category_slug>', views.load_category_products_section, name='load_category_products_section'),
    path('load-new-arrivals-section/', views.load_new_arrivals_section, name='load_new_arrivals_section'),
    path('load-home-ads-section/', views.load_home_ads_section, name='load_home_ads_section'),

    path('load-more-products/', views.load_more_products, name='load_more_products'),
    path('load-category-products/', views.load_category_products, name='load_category_products'),

    # Redirect URLs for Load More buttons
    path('deals/', views.view_all_deals, name='view_all_deals'),
    path('category/<int:category_id>/all/', views.view_all_category, name='view_all_category'),
    path('new-arrivals/', views.view_all_new_arrivals, name='view_all_new_arrivals'),


    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),

    #policies
    path('return-and-refund_policy/', views.return_and_refund_policy, name='return_and_refund_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('Replacement-Policy/', views.Replacement_Policy, name='Replacement_Policy'),
]