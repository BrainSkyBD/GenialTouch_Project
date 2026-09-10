# core/views.py
from django.shortcuts import render, redirect
from django.db.models import Q, Count, Avg, Prefetch, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.http import JsonResponse
from django.template.loader import render_to_string

from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable, SiteFeature
from products.models import Product, Category, Brand, AttributeValue, ProductImage
from reviews.models import Review

import time
from datetime import datetime, timedelta

from branding_management.models import BrandInfo, TrustBadge
# core/views.py

from django.shortcuts import render, redirect
from django.db.models import Q, Count, Avg, Prefetch, Min, Max
from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import JsonResponse
from django.template.loader import render_to_string

from core.models import Banner, Promotion, HomeAd, CurrencySettingsTable, SiteFeature
from products.models import Product, Category, Brand, AttributeValue, ProductImage
from reviews.models import Review

import time
from datetime import datetime, timedelta
from core.utils import get_theme_template
from branding_management.models import BrandInfo, TrustBadge

def search_suggestions(request):
    """Optimized search suggestions with proper image URLs"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'products': []})
    
    products = list(Product.objects.filter(
        Q(name__icontains=query) & 
        Q(is_active=True)
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price'
    )[:5])
    
    if not products:
        return JsonResponse({'products': []})
    
    product_ids = [p.id for p in products]
    
    images = ProductImage.objects.filter(
        product_id__in=product_ids
    ).order_by('product_id', '-is_featured', 'display_order').only(
        'id', 'image', 'product_id', 'is_featured'
    )
    
    image_dict = {}
    for img in images:
        if img.product_id not in image_dict:
            image_dict[img.product_id] = img.image.url
    
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
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('product_list')
    
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '')
    
    products = Product.objects.filter(
        is_active=True,
        name__icontains=query
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
    
    all_context_brands = Brand.objects.filter(
        product__in=products.values('id'),
        is_active=True
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count')
    
    all_context_attributes = AttributeValue.objects.filter(
        product__in=products.values('id')
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).select_related('attribute').order_by('attribute__name', 'value')
    
    attribute_groups = {}
    for attr in all_context_attributes:
        attr_name = attr.attribute.name
        if attr_name not in attribute_groups:
            attribute_groups[attr_name] = []
        attribute_groups[attr_name].append({
            'id': attr.id,
            'value': attr.value,
            'product_count': attr.product_count,
            'is_available': True
        })
    
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
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
    
    per_page = 12
    paginator = Paginator(products, per_page)
    
    try:
        products_page = paginator.page(page)
    except:
        products_page = paginator.page(1)
    
    if is_ajax:
        products_data = []
        for product in products_page:
            main_image = product.images.filter(is_featured=True).first()
            if not main_image and product.images.exists():
                main_image = product.images.first()
            
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
    
    total_products = paginator.count
    page_title = f"Search results for '{query}'"
    
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
        'is_name_search': True,
    }
    
    return render(request, get_theme_template('shop/product_list.html'), context)


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
        
        columns = ['id', 'name', 'slug', 'image']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]





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
        columns = ['id', 'name', 'slug', 'image']
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def home(request):
    """
    Home view with dynamic theme support
    """
    start_time = time.time()
    
    # Get brand info
    brand_info = BrandInfo.get_brand_info()
    theme_folder = brand_info.active_theme if brand_info else 'theme-01-default'
    
    # Get top categories
    top_categories = Category.objects.filter(
        parent__isnull=True, 
        is_active=True, 
        is_featured=True
    ).only('id', 'name', 'slug', 'image')[:16]
    
    # ✅ Get 3 main categories for promo cards + product sections
    main_categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    ).only('id', 'name', 'slug', 'image').order_by('display_order', 'name')[:3]
    
    # Banners
    banners = Banner.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')
    
    # Site features
    site_features = []
    feature_data = SiteFeature.objects.filter(is_active=True)
    for feature in feature_data:
        site_features.append({
            'title': feature.title,
            'description': feature.get_display_description(),
            'icon': feature.icon,
            'min_order_amount': feature.min_order_amount,
            'return_days': feature.return_days,
        })
    
    # Promotions
    promotions = Promotion.objects.filter(is_active=True).only('image', 'url', 'title').order_by('order')[:2]
    
    # Deal end date
    deal_end_date = datetime.now() + timedelta(days=1)
    
    featured_categories = get_featured_categories()
    
    # Active currency
    try:
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '৳'
    except:
        currency_symbol = '৳'
    
    # Trust badges
    trust_badges = []
    if brand_info:
        trust_badges = brand_info.trust_badges.filter(is_active=True).order_by('order')
    
    # ✅ DEALS PRODUCTS (Dynamic from is_featured=True)
    deals_products = Product.objects.filter(
        is_active=True, 
        is_featured=True
    ).select_related('brand').prefetch_related(
        Prefetch(
            'images',
            queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('display_order', 'id')
        )
    ).only(
        'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
    ).order_by('-created_at')[:8]
    
    # ✅ CATEGORY PRODUCTS (Dynamic)
    category_products_data = []
    for category in main_categories:
        # Get descendant category IDs
        descendant_ids = category.get_descendant_ids()
        
        products = Product.objects.filter(
            categories__id__in=descendant_ids,
            is_active=True
        ).select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('display_order', 'id')
            )
        ).only(
            'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
        ).distinct().order_by('-created_at')[:10]
        
        if products.exists():
            category_products_data.append({
                'category': category,
                'products': products,
            })
    
    load_time = time.time() - start_time
    print(f"Home page loaded in {load_time:.2f} seconds")
    
    context = {
        'top_categories': top_categories,
        'main_categories': main_categories,
        'banners': banners,
        'promotions': promotions,
        'site_features': site_features,
        'deal_end_date': deal_end_date,
        'featured_categories': featured_categories,
        'theme_folder': theme_folder,
        'currency_symbol': currency_symbol,
        'trust_badges': trust_badges,
        'deals_products': deals_products,
        'category_products_data': category_products_data,
        'brand_info': brand_info,
    }
    
    template_name = f'{theme_folder}/home.html'
    return render(request, template_name, context)

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
    
    deal_end_date = datetime.now() + timedelta(days=1)
    
    try:
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '৳'
    except:
        currency_symbol = '৳'
    
    html = render_to_string('partials/deals_section.html', {
        'deals': deals,
        'deal_end_date': deal_end_date,
        'currency_symbol': currency_symbol,
    })
    
    return JsonResponse({'html': html})


def load_category_products_section(request, category_slug):
    """Load category products section via AJAX"""
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
    
    try:
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '৳'
    except:
        currency_symbol = '৳'
    
    html = render_to_string('partials/category_products_section.html', {
        'products': products,
        'currency_symbol': currency_symbol,
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
    
    try:
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '৳'
    except:
        currency_symbol = '৳'
    
    html = render_to_string('partials/new_arrivals_section.html', {
        'new_arrivals': new_arrivals,
        'currency_symbol': currency_symbol,
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
    return redirect('product_list') + '?featured=true'


def view_all_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        return redirect('products_by_category', slug=category.slug)
    except Category.DoesNotExist:
        return redirect('product_list')


def view_all_new_arrivals(request):
    return redirect('product_list') + '?sort=newest'


def load_more_products(request):
    product_type = request.GET.get('type', 'new_arrivals')
    page = int(request.GET.get('page', 2))
    per_page = 8
    
    try:
        products = Product.objects.filter(is_active=True)
        
        if product_type == 'deals':
            products = products.filter(is_featured=True)
        elif product_type == 'new_arrivals':
            products = products.order_by('-created_at')
        
        products = products.select_related('brand').prefetch_related(
            Prefetch(
                'images',
                queryset=ProductImage.objects.only('image', 'product_id').order_by('id')
            )
        ).only(
            'id', 'name', 'slug', 'price', 'discount_price', 'brand__name'
        )
        
        paginator = Paginator(products, per_page)
        
        try:
            products_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            products_page = paginator.page(1)
        
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
        
        return JsonResponse({
            'success': True,
            'products': products_data,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def load_category_products(request):
    category_id = request.GET.get('category_id')
    page = int(request.GET.get('page', 1))
    per_page = 10
    
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        
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
        
        paginator = Paginator(products, per_page)
        
        try:
            products_page = paginator.page(page)
        except (PageNotAnInteger, EmptyPage):
            products_page = paginator.page(1)
        
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
        
        return JsonResponse({
            'success': True,
            'products': products_data,
            'has_next': products_page.has_next(),
            'next_page': products_page.next_page_number() if products_page.has_next() else None,
            'category_name': category.name,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def return_and_refund_policy(request):
    return render(request, "policies/return_and_refund_policy.html")


def terms_and_conditions(request):
    return render(request, "policies/terms_and_conditions.html")


def Replacement_Policy(request):
    return render(request, "policies/Replacement_Policy.html")


def test_func(request):
    return render(request, 'test/test.html')