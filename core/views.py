# views.py
from django.shortcuts import render
from .models import Banner, Promotion, HomeAd
from .models import Banner, Promotion, HomeAd
from django.db.models import Q

from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from products.models import Product, Category, Brand, AttributeValue, ProductImage
from reviews.models import Review



# def home(request):
#     # Main categories (those without parents)
#     categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children')
    
#     # Get featured categories (you might want to add a 'is_featured' field to Category model)
#     featured_categories = Category.objects.filter(is_active=True, is_featured=True)[:8]
    
#     # Products for different sections
#     deals = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:8]
#     new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    
#     # Get products for featured categories
#     category_products = []
#     for category in featured_categories:
#         products = Product.objects.filter(
#             categories=category,
#             is_active=True
#         ).distinct().order_by('-created_at')[:10]
#         if products.exists():
#             category_products.append({
#                 'category': category,
#                 'products': products
#             })
    
#     # Marketing content
#     banners = Banner.objects.filter(is_active=True).order_by('order')
#     promotions = Promotion.objects.filter(is_active=True).order_by('order')[:2]
#     home_ads = HomeAd.objects.filter(is_active=True).order_by('order')[:5]
    
#     # Calculate deal end date (24 hours from now)
#     from datetime import datetime, timedelta
#     deal_end_date = datetime.now() + timedelta(days=1)
#     # top_categories = Category.objects.filter(is_active=True)[:9]
#     top_categories = Category.objects.filter(parent__isnull=True, is_active=True, is_featured=True)


#     context = {
#         'categories': categories,
#         'featured_categories': featured_categories,
#         'category_products': category_products,
#         'deals': deals,
#         'new_arrivals': new_arrivals,
#         'banners': banners,
#         'promotions': promotions,
#         'home_ads': home_ads,
#         'deal_end_date': deal_end_date,
#         'top_categories':top_categories,
#     }
    
#     return render(request, 'index.html', context)

from django.db.models import Prefetch
from core.models import CurrencySettingsTable

def home(request):
    # Get active currency
    currency = CurrencySettingsTable.objects.filter(is_active=True).first()
    
    # Top categories
    top_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True, 
        is_featured=True
    )[:9]
    
    # Get deals with optimized queries
    deals = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.all(),
            to_attr='all_images'
        )
    ).order_by('-created_at')[:8]
    
    # Get new arrivals
    new_arrivals = Product.objects.filter(
        is_active=True
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.all()
        )
    ).order_by('-created_at')[:8]
    
    # Optimize category products queries
    category_products = []
    featured_categories = Category.objects.filter(
        is_active=True, 
        is_featured=True
    )[:3]
    
    for category in featured_categories:
        products = Product.objects.filter(
            categories=category,
            is_active=True
        ).select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.all()
            )
        ).distinct().order_by('-created_at')[:10]
        
        if products.exists():
            category_products.append({
                'category': category,
                'products': products
            })
    
    # Get banners, promotions, ads
    banners = Banner.objects.filter(is_active=True).order_by('order')
    promotions = Promotion.objects.filter(is_active=True).order_by('order')[:2]
    home_ads = HomeAd.objects.filter(is_active=True).order_by('order')[:5]
    
    # Calculate deal end date
    from datetime import datetime, timedelta
    deal_end_date = datetime.now() + timedelta(days=1)
    
    context = {
        'categories': Category.objects.filter(parent__isnull=True, is_active=True)[:5],
        'featured_categories': featured_categories,
        'category_products': category_products,
        'deals': deals,
        'new_arrivals': new_arrivals,
        'banners': banners,
        'promotions': promotions,
        'home_ads': home_ads,
        'deal_end_date': deal_end_date,
        'top_categories': top_categories,
        'currency_symbol': currency.currency_symbol if currency else '$',
    }
    
    return render(request, 'index.html', context)



def return_and_refund_policy(request):
    return render(request, "policies/return_and_refund_policy.html")

def terms_and_conditions(request):
    return render(request, "policies/terms_and_conditions.html")

def Replacement_Policy(request):
    return render(request, "policies/Replacement_Policy.html")