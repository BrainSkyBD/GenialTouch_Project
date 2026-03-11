# views.py

from django.shortcuts import render, redirect
from django.db.models import Q, Count, Avg, Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.http import JsonResponse
from django.template.loader import render_to_string

from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable, SiteFeature
from products.models import Product, Category, Brand, AttributeValue, ProductImage
from reviews.models import Review

import time
from django.http import JsonResponse
from django.db.models import Q, Count, Avg, Min, Max, Prefetch

from django.core.cache import cache
from django.db.models import Exists, OuterRef

from core.email_send_views import send_email_function


# def home(request):
#     """
#     Optimized home view keeping your exact frontend
#     """
    
    
#     # Get data (with optimizations)
#     start_time = time.time()
    
    
    
#     # Get featured categories
#     featured_categories = Category.objects.filter(
#         is_active=True, 
#         is_featured=True
#     ).only('id', 'name', 'slug', 'image')[:8]
    
#     # Products for different sections with optimization
#     deals = Product.objects.filter(
#         is_active=True, 
#         is_featured=True
#     ).select_related('brand').prefetch_related(
#         Prefetch(
#             'images',
#             queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
#         )
#     ).only(
#         'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
#     ).order_by('-created_at')[:8]
    
#     new_arrivals = Product.objects.filter(
#         is_active=True
#     ).select_related('brand').prefetch_related(
#         Prefetch(
#             'images',
#             queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
#         )
#     ).only(
#         'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
#     ).order_by('-created_at')[:8]
    
#     # Get products for featured categories
#     category_products = []
#     for category in featured_categories:
#         products = Product.objects.filter(
#             categories=category,
#             is_active=True
#         ).select_related('brand').prefetch_related(
#             Prefetch(
#                 'images',
#                 queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
#             )
#         ).only(
#             'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
#         ).distinct().order_by('-created_at')[:10]
        
#         if products.exists():
#             category_products.append({
#                 'category': category,
#                 'products': products
#             })
    
#     # Marketing content
#     banners = Banner.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')
#     promotions = Promotion.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:2]
#     home_ads = HomeAd.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:5]
    
#     # Calculate deal end date
#     from datetime import datetime, timedelta
#     deal_end_date = datetime.now() + timedelta(days=1)
    
#     top_categories = Category.objects.filter(
#         parent__isnull=True, 
#         is_active=True, 
#         is_featured=True
#     ).only('id', 'name', 'slug', 'image')
    
#     # Log performance
#     load_time = time.time() - start_time
#     print(f"Home page loaded in {load_time:.2f} seconds")



#     # Get all active site features
#     site_features = SiteFeature.objects.filter(is_active=True).select_related()
    
#     # Process features for template
#     processed_features = []
#     for feature in site_features:
#         feature_data = {
#             'title': feature.title,
#             'description': feature.get_display_description(),
#             'icon': feature.icon,
#             'min_order_amount': feature.min_order_amount,
#             'return_days': feature.return_days,
#         }
#         processed_features.append(feature_data)
    
    
    
#     context = {
#         'featured_categories': featured_categories,
#         'category_products': category_products,
#         'deals': deals,
#         'new_arrivals': new_arrivals,
#         'banners': banners,
#         'promotions': promotions,
#         'home_ads': home_ads,
#         'deal_end_date': deal_end_date,
#         'top_categories': top_categories,

#         'site_features': processed_features,
#     }
    
#     return render(request, 'index.html', context)


# views.py - Updated home view with minimal data


def search_suggestions(request):
    """
    Optimized search suggestions with proper image URLs
    Uses dictionary lookup for maximum speed
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    # Get products first (one query)
    products = list(Product.objects.filter(
        Q(name__icontains=query) & 
        Q(is_active=True)
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price'
    )[:5])
    
    if not products:
        return JsonResponse({'products': []})
    
    # Get product IDs
    product_ids = [p.id for p in products]
    
    # Get all images for these products (second query)
    images = ProductImage.objects.filter(
        product_id__in=product_ids
    ).filter(
        Q(is_featured=True) | Q(is_featured=False)  # Get featured first, then any
    ).order_by('product_id', '-is_featured', 'display_order').only(
        'id', 'image', 'product_id', 'is_featured'
    )
    
    # Create a dictionary with the best image for each product
    image_dict = {}
    for img in images:
        if img.product_id not in image_dict:
            # Take the first image we find for each product
            # (ordered by is_featured and display_order)
            image_dict[img.product_id] = img.image.url
    
    # Build response
    products_data = []
    for product in products:
        current_price = product.discount_price if product.discount_price else product.price
        
        products_data.append({
            'name': product.name,
            'price': str(current_price),
            'image': image_dict.get(product.id, '/static/img/no-image.jpg'),
            'url': f'/products/{product.slug}/'
        })
    
    return JsonResponse({
        'products': products_data
    })



def product_name_search(request):
    """
    Search products by name only - for the "See all results" functionality
    Reuses the same product_list.html template
    """
    # Get search query
    query = request.GET.get('q', '').strip()
    
    # If no query, redirect to product list
    if not query:
        return redirect('product_list')
    
    # Check if it's an AJAX request for infinite scroll
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get other filter parameters (except we'll ignore them for the search part)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '')
    
    # Base queryset - ONLY filter by product name
    products = Product.objects.filter(
        is_active=True,
        name__icontains=query  # Only name search, no description or SKU
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('display_order', 'id')
        ),
        Prefetch(
            'categories',
            queryset=Category.objects.only('id', 'name', 'slug', 'parent_id')
        ),
        Prefetch(
            'reviews',
            queryset=Review.objects.only('product_id', 'rating', 'created_at')
        )
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price', 'brand__name',
        'brand__slug', 'brand__id', 'created_at', 'view_count', 'description', 'is_featured', 'sku'
    ).distinct()
    
    # Get brands for filtering (based on name-only search results)
    all_context_brands = Brand.objects.filter(
        product__in=products.values('id'),
        is_active=True
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count')
    
    # Get attributes for filtering (based on name-only search results)
    all_context_attributes = AttributeValue.objects.filter(
        product__in=products.values('id')
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).select_related('attribute').order_by('attribute__name', 'value')
    
    # Group attributes by type
    attribute_groups = {}
    for attr in all_context_attributes:
        attr_name = attr.attribute.name
        if attr_name not in attribute_groups:
            attribute_groups[attr_name] = []
        attribute_groups[attr_name].append({
            'id': attr.id,
            'value': attr.value,
            'product_count': attr.product_count,
            'is_available': True  # All are available in this context
        })
    
    # Get price range for the filter
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Apply sorting
    if sort == 'price_asc':
        from django.db.models import Case, When, F, FloatField
        products = products.annotate(
            actual_price=Case(
                When(discount_price__isnull=False, discount_price__gt=0, 
                     then=F('discount_price')),
                default=F('price'),
                output_field=FloatField()
            )
        ).order_by('actual_price')
    elif sort == 'price_desc':
        from django.db.models import Case, When, F, FloatField
        products = products.annotate(
            actual_price=Case(
                When(discount_price__isnull=False, discount_price__gt=0, 
                     then=F('discount_price')),
                default=F('price'),
                output_field=FloatField()
            )
        ).order_by('-actual_price')
    elif sort == 'rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'popular':
        products = products.order_by('-view_count')
    else:
        products = products.order_by('-created_at')
    
    # Pagination for infinite scroll
    per_page = 12
    paginator = Paginator(products, per_page)
    
    try:
        products_page = paginator.page(page)
    except:
        products_page = paginator.page(1)
    
    # If it's an AJAX request, return JSON
    if is_ajax:
        products_data = []
        for product in products_page:
            # Get main image
            main_image = product.images.filter(is_featured=True).first()
            if not main_image and product.images.exists():
                main_image = product.images.first()
            
            # Calculate discount percentage
            discount_percentage = 0
            if product.discount_price and product.price and product.price > 0:
                discount_percentage = ((product.price - product.discount_price) / product.price) * 100
                discount_percentage = round(discount_percentage)
            
            products_data.append({
                'id': product.id,
                'name': product.name,
                'slug': product.slug,
                'price': str(product.price),
                'discount_price': str(product.discount_price) if product.discount_price else None,
                'discount_percentage': discount_percentage,
                'brand_name': product.brand.name if product.brand else '',
                'image_url': main_image.image.url if main_image else '/static/img/no-image.jpg',
                'url': product.get_absolute_url(),
                'avg_rating': round(product.avg_rating, 1) if hasattr(product, 'avg_rating') and product.avg_rating else 0,
                'review_count': product.review_count if hasattr(product, 'review_count') else 0,
            })
        
        return JsonResponse({
            'success': True,
            'products': products_data,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None,
            'total_products': paginator.count,
        })
    
    # For normal request, prepare context
    total_products = paginator.count
    
    # Page title
    page_title = f"Search results for '{query}'"
    
    
    
    # Get categories for sidebar - show top-level categories
    sidebar_categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).only('id', 'name', 'slug').order_by('display_order', 'name')
    
    context = {
        'products': products_page,
        'query': query,
        'sidebar_categories': sidebar_categories,
        'selected_category': None,
        'selected_brand_slug': None,
        'all_context_brands': all_context_brands,
        'available_brand_slugs': list(all_context_brands.values_list('slug', flat=True)),
        'selected_brands': [],
        'min_price': None,
        'max_price': None,
        'price_range': price_range,
        'selected_rating': None,
        'attribute_groups': attribute_groups,
        'available_attribute_ids': list(all_context_attributes.values_list('id', flat=True)),
        'selected_attributes': [],
        'sort_option': sort,
        'subcategory_list': None,
        'category': None,
        'total_products': total_products,
        'page_title': page_title,
        'is_featured_filter': False,
        'is_new_arrivals': sort == 'newest',
        'is_ajax': is_ajax,
        'active_filter_count': 0,
        'is_name_search': True,  # Flag to indicate this is a name-only search
    }
    
    return render(request, 'shop/product_list.html', context)



def get_featured_categories(limit=8):
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.id, c.name, c.slug, c.image
            FROM products_category c
            WHERE c.is_active = true 
            AND c.is_featured = true
            AND EXISTS (
                SELECT 1 FROM products_product_categories pc
                JOIN products_product p ON p.id = pc.product_id
                WHERE pc.category_id = c.id 
                AND p.is_active = true
            )
            LIMIT %s
        """, [limit])
        
        # Convert to dict for template
        columns = ['id', 'name', 'slug', 'image']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]



def home(request):
    """
    Home view with minimal initial data - rest loads via AJAX
    """
    start_time = time.time()
    
    # ONLY LOAD ESSENTIAL DATA FOR ABOVE THE FOLD
    # Top categories (limited to 16 max)
    top_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True, 
        is_featured=True
    ).only('id', 'name', 'slug', 'image')[:16]
    
    # Banners (essential for hero section)
    banners = Banner.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')
    
    # Site features
    site_features = []
    feature_data = SiteFeature.objects.filter(is_active=True).select_related()
    for feature in feature_data:
        site_features.append({
            'title': feature.title,
            'description': feature.get_display_description(),
            'icon': feature.icon,
            'min_order_amount': feature.min_order_amount,
            'return_days': feature.return_days,
        })
    
    # Minimal promotions for sidebar (first 2 only)
    promotions = Promotion.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:2]
    
    # Deal end date
    from datetime import datetime, timedelta
    deal_end_date = datetime.now() + timedelta(days=1)
    
    load_time = time.time() - start_time
    print(f"Home page initial load: {load_time:.2f} seconds")
    

    # Products for different sections with optimization
    # deals = Product.objects.filter(
    #     is_active=True, 
    #     is_featured=True
    # ).select_related('brand').prefetch_related(
    #     Prefetch(
    #         'images',
    #         queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
    #     )
    # ).only(
    #     'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
    # ).order_by('-created_at')[:8]


    featured_categories = get_featured_categories()

    context = {
        'top_categories': top_categories,
        'banners': banners,
        'promotions': promotions,
        'site_features': site_features,
        'deal_end_date': deal_end_date,
        # "deals":deals,
        "featured_categories": featured_categories,
    }
    
    return render(request, 'index.html', context)


def load_deals_section(request):
    """Load deals section via AJAX"""
    from django.template.loader import render_to_string
    
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
    
    from datetime import datetime, timedelta
    deal_end_date = datetime.now() + timedelta(days=1)
    
    html = render_to_string('partials/deals_section.html', {
        'deals': deals,
        'deal_end_date': deal_end_date,
    })
    
    return JsonResponse({'html': html})


# def load_category_products_section(request):
#     """Load category products section via AJAX"""
#     from django.template.loader import render_to_string
    
#     # Get featured categories
#     featured_categories = Category.objects.filter(
#         is_active=True, 
#         is_featured=True
#     ).only('id', 'name', 'slug', 'image')[:8]
    
#     # Get products for categories
#     category_products = []
#     for category in featured_categories:
#         products = Product.objects.filter(
#             categories=category,
#             is_active=True
#         ).select_related('brand').prefetch_related(
#             Prefetch(
#                 'images',
#                 queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
#             )
#         ).only(
#             'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
#         ).distinct().order_by('-created_at')[:10]
        
#         if products.exists():
#             category_products.append({
#                 'category': category,
#                 'products': products
#             })
    
#     html = render_to_string('partials/category_products_section.html', {
#         'category_products': category_products,
#     })
    
#     return JsonResponse({'html': html})


def load_category_products_section(request, category_slug):
    """Load deals section via AJAX"""
    from django.template.loader import render_to_string
    
    products = Product.objects.filter(
                    categories__slug=category_slug,
                    is_active=True
                ).select_related('brand').prefetch_related(
                    Prefetch(
                        'images',
                        queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
                    )
                ).only(
                    'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
                ).distinct().order_by('-created_at')[:10]
    
    html = render_to_string('partials/category_products_section.html', {
        'products': products,
    })
    
    return JsonResponse({'html': html})


def load_new_arrivals_section(request):
    """Load new arrivals section via AJAX"""
    from django.template.loader import render_to_string
    
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
    
    html = render_to_string('partials/new_arrivals_section.html', {
        'new_arrivals': new_arrivals,
    })
    
    return JsonResponse({'html': html})


def load_home_ads_section(request):
    """Load home ads section via AJAX"""
    from django.template.loader import render_to_string
    
    section = request.GET.get('section', 'first')
    home_ads = HomeAd.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')
    
    if section == 'first':
        ads = home_ads[:3]
        html = render_to_string('partials/home_ads_first.html', {'home_ads': ads})
    else:
        ads = home_ads[3:5]
        html = render_to_string('partials/home_ads_second.html', {'home_ads': ads})
    
    return JsonResponse({'html': html})



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