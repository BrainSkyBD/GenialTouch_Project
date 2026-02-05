# views.py
from django.shortcuts import render
from .models import Banner, Promotion, HomeAd
from .models import Banner, Promotion, HomeAd
from django.db.models import Q

from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from products.models import Product, Category, Brand, AttributeValue, ProductImage
from reviews.models import Review



from django.shortcuts import render
from django.db.models import Prefetch
from django.core.cache import cache
from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable
from products.models import Category, Product, ProductImage
import time

from django.shortcuts import render
from django.db.models import Prefetch
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable
from products.models import Category, Product, ProductImage
import time

from django.shortcuts import render, redirect
from django.db.models import Prefetch
from django.core.cache import cache
from django.http import JsonResponse
from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable
from products.models import Category, Product, ProductImage
import time


def home(request):
    """
    Optimized home view keeping your exact frontend
    """
    # Get active currency
    try:
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '$'
    except:
        currency_symbol = '$'
    
    # Get data (with optimizations)
    start_time = time.time()
    
    # Main categories (those without parents)
    categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True
    ).only('id', 'name', 'slug', 'image').prefetch_related(
        Prefetch(
            'children',
            queryset=Category.objects.filter(is_active=True).only('id', 'name', 'slug', 'image')
        )
    )
    
    # Get featured categories
    featured_categories = Category.objects.filter(
        is_active=True, 
        is_featured=True
    ).only('id', 'name', 'slug', 'image')[:8]
    
    # Products for different sections with optimization
    deals = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
        )
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
    ).order_by('-created_at')[:8]
    
    new_arrivals = Product.objects.filter(
        is_active=True
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
        )
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
    ).order_by('-created_at')[:8]
    
    # Get products for featured categories
    category_products = []
    for category in featured_categories:
        products = Product.objects.filter(
            categories=category,
            is_active=True
        ).select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
            )
        ).only(
            'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
        ).distinct().order_by('-created_at')[:10]
        
        if products.exists():
            category_products.append({
                'category': category,
                'products': products
            })
    
    # Marketing content
    banners = Banner.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')
    promotions = Promotion.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:2]
    home_ads = HomeAd.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:5]
    
    # Calculate deal end date
    from datetime import datetime, timedelta
    deal_end_date = datetime.now() + timedelta(days=1)
    
    top_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True, 
        is_featured=True
    ).only('id', 'name', 'slug', 'image')
    
    # Log performance
    load_time = time.time() - start_time
    print(f"Home page loaded in {load_time:.2f} seconds")
    
    context = {
        'categories': categories,
        'featured_categories': featured_categories,
        'category_products': category_products,
        'deals': deals,
        'new_arrivals': new_arrivals,
        'banners': banners,
        'promotions': promotions,
        'home_ads': home_ads,
        'deal_end_date': deal_end_date,
        'top_categories': top_categories,
        'currency_symbol': currency_symbol,
    }
    
    return render(request, 'index.html', context)


def view_all_deals(request):
    """
    Redirect to product_list page with deals filter
    """
    return redirect('product_list') + '?featured=true'


def view_all_category(request, category_id):
    """
    Redirect to category page
    """
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        return redirect('products_by_category', slug=category.slug)
    except Category.DoesNotExist:
        return redirect('product_list')


def view_all_new_arrivals(request):
    """
    Redirect to product_list page with new arrivals filter
    """
    return redirect('product_list') + '?sort=newest'

def load_more_products(request):
    """
    AJAX endpoint for loading more products with infinite scroll
    """
    product_type = request.GET.get('type', 'new_arrivals')
    page = int(request.GET.get('page', 2))
    per_page = 8
    
    try:
        # Base query
        products = Product.objects.filter(is_active=True)
        
        # Apply filters
        if product_type == 'deals':
            products = products.filter(is_featured=True)
        elif product_type == 'new_arrivals':
            products = products.order_by('-created_at')
        
        # Optimize query
        products = products.select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'product_id').order_by('id')
            )
        ).only(
            'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
        )
        
        # Paginate
        paginator = Paginator(products, per_page)
        
        try:
            products_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            products_page = paginator.page(1)
        
        # Prepare response
        products_data = []
        for product in products_page:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': str(product.price),
                'discount_price': str(product.discount_price) if product.discount_price else None,
                'discount_percentage': product.get_discount_percentage(),
                'brand_name': product.brand.name if product.brand else '',
                'image_url': product.images.first().image.url if product.images.exists() else '/static/img/no-image.jpg',
                'url': product.get_absolute_url(),
            })
        
        response_data = {
            'success': True,
            'products': products_data,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None,
        }
        
    except Exception as e:
        response_data = {
            'success': False,
            'message': str(e)
        }
    
    return JsonResponse(response_data)


def load_category_products(request):
    """
    AJAX endpoint for loading category products
    """
    category_id = request.GET.get('category_id')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        
        # Get products
        products = Product.objects.filter(
            categories=category,
            is_active=True
        ).select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'product_id').order_by('id')
            )
        ).only(
            'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
        ).distinct().order_by('-created_at')
        
        # Paginate
        paginator = Paginator(products, per_page)
        
        try:
            products_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            products_page = paginator.page(1)
        
        # Prepare response
        products_data = []
        for product in products_page:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': str(product.price),
                'discount_price': str(product.discount_price) if product.discount_price else None,
                'discount_percentage': product.get_discount_percentage(),
                'brand_name': product.brand.name if product.brand else '',
                'image_url': product.images.first().image.url if product.images.exists() else '/static/img/no-image.jpg',
                'url': product.get_absolute_url(),
            })
        
        response_data = {
            'success': True,
            'products': products_data,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None,
            'category_name': category.name,
        }
        
    except Exception as e:
        response_data = {
            'success': False,
            'message': str(e)
        }
    
    return JsonResponse(response_data)

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

# from django.db.models import Prefetch

# def home(request):
    
#     # Top categories
#     top_categories = Category.objects.filter(
#         parent__isnull=True, 
#         is_active=True, 
#         is_featured=True
#     )[:9]
    
#     # Get deals with optimized queries
#     deals = Product.objects.filter(
#         is_active=True, 
#         is_featured=True
#     ).select_related('brand').prefetch_related(
#         Prefetch(
#             'images',
#             queryset=ProductImage.objects.all(),
#             to_attr='all_images'
#         )
#     ).order_by('-created_at')[:8]
    
#     # Get new arrivals
#     new_arrivals = Product.objects.filter(
#         is_active=True
#     ).select_related('brand').prefetch_related(
#         Prefetch(
#             'images',
#             queryset=ProductImage.objects.all()
#         )
#     ).order_by('-created_at')[:8]
    
#     # Optimize category products queries
#     category_products = []
#     featured_categories = Category.objects.filter(
#         is_active=True, 
#         is_featured=True
#     )[:3]
    
#     for category in featured_categories:
#         products = Product.objects.filter(
#             categories=category,
#             is_active=True
#         ).select_related('brand').prefetch_related(
#             Prefetch(
#                 'images',
#                 queryset=ProductImage.objects.all()
#             )
#         ).distinct().order_by('-created_at')[:10]
        
#         if products.exists():
#             category_products.append({
#                 'category': category,
#                 'products': products
#             })
    
#     # Get banners, promotions, ads
#     banners = Banner.objects.filter(is_active=True).order_by('order')
#     promotions = Promotion.objects.filter(is_active=True).order_by('order')[:2]
#     home_ads = HomeAd.objects.filter(is_active=True).order_by('order')[:5]
    
#     # Calculate deal end date
#     from datetime import datetime, timedelta
#     deal_end_date = datetime.now() + timedelta(days=1)
    
#     context = {
#         'categories': Category.objects.filter(parent__isnull=True, is_active=True)[:5],
#         'featured_categories': featured_categories,
#         'category_products': category_products,
#         'deals': deals,
#         'new_arrivals': new_arrivals,
#         'banners': banners,
#         'promotions': promotions,
#         'home_ads': home_ads,
#         'deal_end_date': deal_end_date,
#         'top_categories': top_categories,
#     }
    
#     return render(request, 'index.html', context)



def return_and_refund_policy(request):
    return render(request, "policies/return_and_refund_policy.html")

def terms_and_conditions(request):
    return render(request, "policies/terms_and_conditions.html")

def Replacement_Policy(request):
    return render(request, "policies/Replacement_Policy.html")