from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Brand, ProductVariation

from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from products.models import Product, Category, Brand, AttributeValue
from reviews.models import Review
from django.db.models import Q, Count, Avg, Max
from decimal import Decimal
import json

# views.py - add this new view
from django.http import JsonResponse
# views.py
from django.shortcuts import render
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from .models import Product, Category, Brand, AttributeValue, Attribute, ProductImage
from django.db.models import Q
from django.http import JsonResponse
from orders.models import PaymentMethod, Order, OrderItem, Country, District, TaxConfiguration


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import time
from django.db.models import Prefetch


from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg, Min, Max
from django.core.paginator import Paginator
from django.http import JsonResponse
import time
import json
# Add this to your views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# def product_list(request):
#     # Get all filter parameters
#     query = request.GET.get('q', '')
#     category_slug = request.GET.get('category', '')
#     brand_slugs = request.GET.getlist('brand')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     rating = request.GET.get('rating')
#     attribute_values = request.GET.getlist('attribute')
#     page = request.GET.get('page', 1)
    
#     # Base queryset
#     products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
#         'categories', 'images', 'reviews', 'attributes'
#     )
    
#     # Apply filters
#     if query:
#         products = products.filter(
#             Q(name__icontains=query) | 
#             Q(description__icontains=query) |
#             Q(sku__icontains=query)
#         )
    
#     if category_slug:
#         category = Category.objects.get(slug=category_slug)
#         products = products.filter(categories=category)
    
#     if brand_slugs:
#         products = products.filter(brand__slug__in=brand_slugs)
    
#     if min_price:
#         products = products.filter(Q(price__gte=min_price) | Q(discount_price__gte=min_price))
    
#     if max_price:
#         products = products.filter(Q(price__lte=max_price) | Q(discount_price__lte=min_price))
    
#     if rating:
#         # Get products with average rating >= selected value
#         product_ids = Review.objects.values('product').annotate(
#             avg_rating=Avg('rating')
#         ).filter(avg_rating__gte=rating).values_list('product', flat=True)
#         products = products.filter(id__in=product_ids)
    
#     if attribute_values:
#         products = products.filter(attributes__id__in=attribute_values).distinct()
    
#     # Get top 10 brands (by product count) for the brand filter
#     top_brands = Brand.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).order_by('-product_count')[:10]
    
#     # Get all active categories for sidebar
#     categories = Category.objects.filter(is_active=True)
    
#     # Get all attributes with values for filtering
#     attributes = AttributeValue.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).select_related('attribute')
    
#     # Group attributes by their type
#     attribute_groups = {}
#     for attr in attributes:
#         if attr.attribute.name not in attribute_groups:
#             attribute_groups[attr.attribute.name] = []
#         attribute_groups[attr.attribute.name].append(attr)

#     # Sorting
#     sort = request.GET.get('sort', '')
#     if sort == 'price_asc':
#         products = products.order_by('price')
#     elif sort == 'price_desc':
#         products = products.order_by('-price')
#     elif sort == 'rating':
#         products = products.annotate(
#             avg_rating=Avg('reviews__rating')
#         ).order_by('-avg_rating')
#     elif sort == 'newest':
#         products = products.order_by('-created_at')
#     elif sort == 'popular':
#         products = products.annotate(
#             review_count=Count('reviews')
#         ).order_by('-review_count')
    
#     # Pagination
#     paginator = Paginator(products, 12)  # Show 12 products per page
#     products = paginator.get_page(page)
    
#     context = {
#         'products': products,
#         'query': query,
#         'categories': categories,
#         'selected_category': category_slug,
#         'top_brands': top_brands,
#         'selected_brands': brand_slugs,
#         'min_price': min_price,
#         'max_price': max_price,
#         'selected_rating': rating,
#         'attribute_groups': attribute_groups,
#         'selected_attributes': attribute_values,
#     }
    
#     return render(request, 'shop/product_list.html', context)




# def product_list(request):
#     return _product_list_base(request)


# def products_by_category(request, slug):
#     return _product_list_base(request, category_slug=slug)


# def products_by_brand(request, slug):
#     return _product_list_base(request, brand_slug=slug)


# def _product_list_base(request, category_slug=None, brand_slug=None):
#     start_time = time.time()
    
#     # Get all filter parameters from GET request
#     query = request.GET.get('q', '')
#     category_slug_get = request.GET.get('category', '')
#     brand_slugs = request.GET.getlist('brand')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     rating = request.GET.get('rating')
#     attribute_values = request.GET.getlist('attribute')
#     page = request.GET.get('page', 1)
#     sort = request.GET.get('sort', '')
#     featured = request.GET.get('featured', '')
    
#     # Base queryset with optimizations
#     products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
#         Prefetch(
#             'images',
#             queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
#         ),
#         'categories',
#         Prefetch(
#             'reviews',
#             queryset=Review.objects.only('product_id', 'rating')
#         )
#     ).only(
#         'id', 'name', 'slug', 'price', 'discount_price', 'brand__name',
#         'brand__slug', 'created_at', 'view_count'
#     )
    
#     # Featured filter (for deals)
#     if featured.lower() == 'true':
#         products = products.filter(is_featured=True)
    
#     # Apply URL-based filters (from category/brand slug in URL)
#     subcategory_list = None
#     category = None
    
#     # Category from URL parameter (category_slug)
#     if category_slug:
#         try:
#             category = Category.objects.get(slug=category_slug, is_active=True)
#             # Get all descendant category IDs
#             descendant_ids = category.get_descendant_ids()
#             products = products.filter(categories__id__in=descendant_ids)
#             subcategory_list = Category.objects.filter(parent=category, is_active=True).only('id', 'name', 'slug')
#         except Category.DoesNotExist:
#             pass
    
#     # Brand from URL parameter (brand_slug)
#     if brand_slug:
#         try:
#             brand = Brand.objects.get(slug=brand_slug)
#             products = products.filter(brand=brand)
#         except Brand.DoesNotExist:
#             pass
    
#     # Apply GET parameter filters (from search/filter form)
#     if query:
#         products = products.filter(
#             Q(name__icontains=query) | 
#             Q(description__icontains=query) |
#             Q(sku__icontains=query)
#         )
    
#     if category_slug_get:
#         try:
#             category = Category.objects.get(slug=category_slug_get, is_active=True)
#             # Get all descendant category IDs
#             descendant_ids = category.get_descendant_ids()
#             products = products.filter(categories__id__in=descendant_ids)
#             subcategory_list = Category.objects.filter(parent=category, is_active=True).only('id', 'name', 'slug')
#         except Category.DoesNotExist:
#             pass
    
#     if brand_slugs:
#         products = products.filter(brand__slug__in=brand_slugs)
    
#     if min_price:
#         try:
#             min_price = float(min_price)
#             products = products.filter(
#                 Q(price__gte=min_price) | Q(discount_price__gte=min_price)
#             )
#         except (ValueError, TypeError):
#             pass
    
#     if max_price:
#         try:
#             max_price = float(max_price)
#             products = products.filter(
#                 Q(price__lte=max_price) | Q(discount_price__lte=max_price)
#             )
#         except (ValueError, TypeError):
#             pass
    
#     if rating:
#         try:
#             rating = float(rating)
#             # Get products with average rating >= selected value
#             product_ids = Review.objects.values('product').annotate(
#                 avg_rating=Avg('rating')
#             ).filter(avg_rating__gte=rating).values_list('product', flat=True)
#             products = products.filter(id__in=product_ids)
#         except (ValueError, TypeError):
#             pass
    
#     if attribute_values:
#         products = products.filter(attributes__id__in=attribute_values).distinct()
    
#     # Get top 10 brands (by product count) for the brand filter
#     top_brands = Brand.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).order_by('-product_count')[:10]
    
#     # Get all active categories for sidebar (optimized)
#     categories = Category.objects.filter(is_active=True).only('id', 'name', 'slug', 'parent_id')
    
#     # Get all attributes with values for filtering
#     attributes = AttributeValue.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).select_related('attribute')
    
#     # Group attributes by their type
#     attribute_groups = {}
#     for attr in attributes:
#         if attr.attribute.name not in attribute_groups:
#             attribute_groups[attr.attribute.name] = []
#         attribute_groups[attr.attribute.name].append(attr)
    
#     # Determine the currently selected category (from URL or GET param)
#     selected_category = category_slug or category_slug_get
    
#     # Sorting
#     if sort == 'price_asc':
#         products = products.order_by('price')
#     elif sort == 'price_desc':
#         products = products.order_by('-price')
#     elif sort == 'rating':
#         products = products.annotate(
#             avg_rating=Avg('reviews__rating')
#         ).order_by('-avg_rating')
#     elif sort == 'newest':
#         products = products.order_by('-created_at')
#     elif sort == 'popular':
#         products = products.annotate(
#             review_count=Count('reviews')
#         ).order_by('-review_count')
#     else:
#         # Default sorting
#         products = products.order_by('-created_at')
    
#     # Get total count before pagination for display
#     total_products = products.count()
    
#     # Pagination
#     paginator = Paginator(products, 12)  # Show 12 products per page
#     try:
#         products_page = paginator.get_page(page)
#     except:
#         products_page = paginator.get_page(1)
    
#     # Page title based on filters
#     page_title = "All Products"
#     if category:
#         page_title = f"{category.name} - Products"
#     elif featured.lower() == 'true':
#         page_title = "Deals of the Day"
#     elif sort == 'newest':
#         page_title = "New Arrivals"
    
#     # Get active currency for display
#     from core.models import CurrencySettingsTable
#     try:
#         active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
#         currency_symbol = active_currency.currency_symbol if active_currency else '$'
#     except:
#         currency_symbol = '$'
    
#     context = {
#         'products': products_page,
#         'query': query,
#         'categories': categories,
#         'selected_category': selected_category,
#         'selected_brand_slug': brand_slug,
#         'top_brands': top_brands,
#         'selected_brands': brand_slugs,
#         'min_price': min_price,
#         'max_price': max_price,
#         'selected_rating': rating,
#         'attribute_groups': attribute_groups,
#         'selected_attributes': attribute_values,
#         'sort_option': sort,
#         'subcategory_list': subcategory_list,
#         'category': category,
#         'total_products': total_products,
#         'page_title': page_title,
#         'currency_symbol': currency_symbol,
#         'is_featured_filter': featured.lower() == 'true',
#         'is_new_arrivals': sort == 'newest',
#     }
    
#     # Log performance
#     load_time = time.time() - start_time
#     print(f"Product list loaded in {load_time:.2f} seconds")
    
#     return render(request, 'shop/product_list.html', context)





def product_list(request):
    return _product_list_base(request)


def products_by_category(request, slug):
    return _product_list_base(request, category_slug=slug)


def products_by_brand(request, slug):
    return _product_list_base(request, brand_slug=slug)


def _product_list_base(request, category_slug=None, brand_slug=None):
    # Check if it's an AJAX request for infinite scroll
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Get all filter parameters
    query = request.GET.get('q', '')
    category_slug_get = request.GET.get('category', '')
    brand_slugs = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    attribute_values = request.GET.getlist('attribute')
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '')
    featured = request.GET.get('featured', '')
    
    # Base queryset with optimizations
    products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
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
    )
    
    # Featured filter (for deals)
    if featured.lower() == 'true':
        products = products.filter(is_featured=True)
    
    # Category handling
    subcategory_list = None
    category = None
    current_category = None
    
    # Category from URL parameter
    if category_slug:
        try:
            category = get_object_or_404(Category, slug=category_slug, is_active=True)
            current_category = category
            # Get all descendant category IDs
            descendant_ids = category.get_descendant_ids()
            products = products.filter(categories__id__in=descendant_ids)
            subcategory_list = Category.objects.filter(
                parent=category, 
                is_active=True
            ).only('id', 'name', 'slug', 'image').order_by('display_order', 'name')
        except Category.DoesNotExist:
            pass
    
    # Category from GET parameter
    if category_slug_get:
        try:
            category = get_object_or_404(Category, slug=category_slug_get, is_active=True)
            current_category = category
            descendant_ids = category.get_descendant_ids()
            products = products.filter(categories__id__in=descendant_ids)
            subcategory_list = Category.objects.filter(
                parent=category, 
                is_active=True
            ).only('id', 'name', 'slug', 'image').order_by('display_order', 'name')
        except Category.DoesNotExist:
            pass
    
    # Brand from URL parameter
    if brand_slug:
        try:
            brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
            products = products.filter(brand=brand)
        except Brand.DoesNotExist:
            pass
    
    # Apply filters
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)
    
    # Price filter - handle both price and discount_price
    if min_price:
        try:
            min_price_val = float(min_price)
            # Complex query to handle both price and discount_price
            products = products.filter(
                Q(price__gte=min_price_val) |
                Q(discount_price__gte=min_price_val) |
                Q(price__gte=min_price_val, discount_price__isnull=True)
            )
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price_val = float(max_price)
            # Complex query to handle both price and discount_price
            products = products.filter(
                Q(price__lte=max_price_val) |
                Q(discount_price__lte=max_price_val) |
                Q(price__lte=max_price_val, discount_price__isnull=True)
            )
        except (ValueError, TypeError):
            pass
    
    if rating:
        try:
            rating_val = float(rating)
            # Get products with average rating >= selected rating
            products_with_rating = Review.objects.values('product').annotate(
                avg_rating=Avg('rating')
            ).filter(avg_rating__gte=rating_val).values_list('product', flat=True)
            products = products.filter(id__in=products_with_rating)
        except (ValueError, TypeError):
            pass
    
    if attribute_values:
        products = products.filter(attributes__id__in=attribute_values).distinct()
    
    # Get price range for the filter
    price_range = products.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # BASE CONTEXT: Get products for determining available options
    # This is the initial filtered set BEFORE brand/attribute/price filters
    base_context_products = Product.objects.filter(is_active=True)
    
    # Apply the same category filter to base context
    if current_category:
        descendant_ids = current_category.get_descendant_ids()
        base_context_products = base_context_products.filter(categories__id__in=descendant_ids)
    
    # Apply search query to base context
    if query:
        base_context_products = base_context_products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    # Apply featured filter to base context
    if featured.lower() == 'true':
        base_context_products = base_context_products.filter(is_featured=True)
    
    # Get ALL brands for the current context (category + search + featured)
    all_context_brands = Brand.objects.filter(
        product__in=base_context_products.values('id'),
        is_active=True
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count')
    
    # Get brands for the CURRENT filtered products (to know which are available)
    if products.exists():
        available_brands = Brand.objects.filter(
            product__in=products.values('id')
        ).annotate(
            product_count=Count('product')
        ).filter(product_count__gt=0).order_by('-product_count')
        available_brand_slugs = set(available_brands.values_list('slug', flat=True))
    else:
        available_brand_slugs = set()
    
    # Get ALL attributes for the current context (category + search + featured)
    all_context_attributes = AttributeValue.objects.filter(
        product__in=base_context_products.values('id')
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).select_related('attribute').order_by('attribute__name', 'value')
    
    # Get attributes for the CURRENT filtered products (to know which are available)
    if products.exists():
        available_attributes = AttributeValue.objects.filter(
            product__in=products.values('id')
        ).annotate(
            product_count=Count('product')
        ).filter(product_count__gt=0).select_related('attribute').order_by('attribute__name', 'value')
        available_attribute_ids = set(available_attributes.values_list('id', flat=True))
    else:
        available_attribute_ids = set()
    
    # Group ALL context attributes by their type
    attribute_groups = {}
    for attr in all_context_attributes:
        attr_name = attr.attribute.name
        if attr_name not in attribute_groups:
            attribute_groups[attr_name] = []
        
        # Add attribute with availability info
        attr_dict = {
            'id': attr.id,
            'value': attr.value,
            'product_count': attr.product_count,
            'is_available': attr.id in available_attribute_ids
        }
        attribute_groups[attr_name].append(attr_dict)
    
    # Get categories for sidebar - show subcategories if a category is selected
    if current_category:
        # Show subcategories of current category
        sidebar_categories = Category.objects.filter(
            parent=current_category,
            is_active=True
        ).only('id', 'name', 'slug').order_by('display_order', 'name')
        
        # If no subcategories, show top-level categories with their children
        if not sidebar_categories.exists():
            # Show all top-level categories with their children
            sidebar_categories = Category.objects.filter(
                parent__isnull=True,
                is_active=True
            ).only('id', 'name', 'slug').order_by('display_order', 'name')
    else:
        # Show main categories (no parent)
        sidebar_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).only('id', 'name', 'slug').order_by('display_order', 'name')
    
    # Determine selected category
    selected_category = category_slug or category_slug_get
    
     # Sorting
    if sort == 'price_asc':
        # Sort by actual price (minimum of price and discount_price)
        # Use Case/When to handle null discount_price
        from django.db.models import Case, When, F, Value, FloatField
        
        products = products.annotate(
            actual_price=Case(
                When(discount_price__isnull=False, discount_price__gt=0, 
                     then=F('discount_price')),
                default=F('price'),
                output_field=FloatField()
            )
        ).order_by('actual_price')
        
    elif sort == 'price_desc':
        # Sort by actual price (minimum of price and discount_price) descending
        from django.db.models import Case, When, F, Value, FloatField
        
        products = products.annotate(
            actual_price=Case(
                When(discount_price__isnull=False, discount_price__gt=0, 
                     then=F('discount_price')),
                default=F('price'),
                output_field=FloatField()
            )
        ).order_by('-actual_price')
        
    elif sort == 'rating':
        # Annotate with average rating and review count
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

    # Calculate average ratings for products (if not already done in rating sort)
    if sort != 'rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
    
    
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
            
            # Get average rating
            avg_rating = product.avg_rating or 0
            review_count = product.review_count or 0
            
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
                'avg_rating': round(avg_rating, 1) if avg_rating else 0,
                'review_count': review_count,
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
    page_title = "All Products"
    if current_category:
        page_title = f"{current_category.name} - Products"
    elif featured.lower() == 'true':
        page_title = "Deals of the Day"
    elif sort == 'newest':
        page_title = "New Arrivals"
    elif brand_slug:
        try:
            brand = Brand.objects.get(slug=brand_slug)
            page_title = f"{brand.name} - Products"
        except:
            pass
    
    # Get active currency
    try:
        from core.models import CurrencySettingsTable
        active_currency = CurrencySettingsTable.objects.filter(is_active=True).first()
        currency_symbol = active_currency.currency_symbol if active_currency else '$'
    except:
        currency_symbol = '$'
    
    # Count active filters for display
    active_filter_count = len(brand_slugs) + len(attribute_values)
    if min_price or max_price:
        active_filter_count += 1
    if rating:
        active_filter_count += 1
    
    context = {
        'products': products_page,
        'query': query,
        'sidebar_categories': sidebar_categories,
        'selected_category': selected_category,
        'selected_brand_slug': brand_slug,
        'all_context_brands': all_context_brands,
        'available_brand_slugs': list(available_brand_slugs),
        'selected_brands': brand_slugs,
        'min_price': min_price,
        'max_price': max_price,
        'price_range': price_range,
        'selected_rating': rating,
        'attribute_groups': attribute_groups,
        'available_attribute_ids': list(available_attribute_ids),
        'selected_attributes': attribute_values,
        'sort_option': sort,
        'subcategory_list': subcategory_list,
        'category': current_category,
        'total_products': total_products,
        'page_title': page_title,
        'currency_symbol': currency_symbol,
        'is_featured_filter': featured.lower() == 'true',
        'is_new_arrivals': sort == 'newest',
        'is_ajax': is_ajax,
        'active_filter_count': active_filter_count,
    }
    
    return render(request, 'shop/product_list.html', context)


@csrf_exempt
def load_more_products(request):
    """Handle AJAX requests for infinite scroll"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            filters = data.get('filters', {})
            page = data.get('page', 1)
            
            # Recreate the filtered queryset
            products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
                Prefetch(
                    'images',
                    queryset=ProductImage.objects.only('image', 'product_id', 'is_featured').order_by('id')
                ),
                Prefetch(
                    'categories',
                    queryset=Category.objects.only('id', 'name', 'slug')
                ),
                Prefetch(
                    'reviews',
                    queryset=Review.objects.only('product_id', 'rating', 'created_at')
                )
            ).only(
                'id', 'name', 'slug', 'price', 'discount_price', 'brand__name',
                'brand__slug', 'created_at', 'view_count', 'description'
            )
            
            # Apply filters from AJAX request
            # Category filter
            if filters.get('category'):
                try:
                    category = Category.objects.get(slug=filters['category'], is_active=True)
                    descendant_ids = category.get_descendant_ids()
                    products = products.filter(categories__id__in=descendant_ids)
                except Category.DoesNotExist:
                    pass
            
            # Brand filter
            if filters.get('brands'):
                products = products.filter(brand__slug__in=filters['brands'])
            
            # Search query
            if filters.get('q'):
                query = filters['q']
                products = products.filter(
                    Q(name__icontains=query) | 
                    Q(description__icontains=query) |
                    Q(sku__icontains=query)
                )
            
            # Price filter
            if filters.get('min_price'):
                try:
                    min_price_val = float(filters['min_price'])
                    products = products.filter(
                        Q(price__gte=min_price_val) | 
                        Q(discount_price__gte=min_price_val) |
                        Q(price__isnull=False, discount_price__isnull=True, price__gte=min_price_val) |
                        Q(discount_price__isnull=False, price__gte=min_price_val)
                    )
                except (ValueError, TypeError):
                    pass
            
            if filters.get('max_price'):
                try:
                    max_price_val = float(filters['max_price'])
                    products = products.filter(
                        Q(price__lte=max_price_val) | 
                        Q(discount_price__lte=max_price_val) |
                        Q(price__isnull=False, discount_price__isnull=True, price__lte=max_price_val) |
                        Q(discount_price__isnull=False, price__lte=max_price_val)
                    )
                except (ValueError, TypeError):
                    pass
            
            # Rating filter
            if filters.get('rating'):
                try:
                    rating_val = float(filters['rating'])
                    product_ids = Review.objects.values('product').annotate(
                        avg_rating=Avg('rating')
                    ).filter(avg_rating__gte=rating_val).values_list('product', flat=True)
                    products = products.filter(id__in=product_ids)
                except (ValueError, TypeError):
                    pass
            
            # Attribute filter
            if filters.get('attributes'):
                products = products.filter(attributes__id__in=filters['attributes']).distinct()
            
            # Featured filter
            if filters.get('featured', '').lower() == 'true':
                products = products.filter(is_featured=True)
            
            # Sorting
            sort_option = filters.get('sort', '')
            if sort_option == 'price_asc':
                products = products.annotate(
                    actual_price=Min('discount_price', 'price')
                ).order_by('actual_price')
            elif sort_option == 'price_desc':
                products = products.annotate(
                    actual_price=Min('discount_price', 'price')
                ).order_by('-actual_price')
            elif sort_option == 'rating':
                products = products.annotate(
                    avg_rating=Avg('reviews__rating')
                ).order_by('-avg_rating')
            elif sort_option == 'newest':
                products = products.order_by('-created_at')
            elif sort_option == 'popular':
                products = products.order_by('-view_count')
            else:
                products = products.order_by('-created_at')
            
            # Pagination
            per_page = 12
            paginator = Paginator(products, per_page)
            
            try:
                products_page = paginator.page(page)
            except:
                products_page = paginator.page(1)
            
            # Prepare product data
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
                
                # Get average rating
                avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
                
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
                    'avg_rating': round(avg_rating, 1) if avg_rating else 0,
                    'review_count': product.reviews.count(),
                })
            
            return JsonResponse({
                'success': True,
                'products': products_data,
                'has_next': products_page.has_next(),
                'next_page': products_page.next_page_number() if products_page.has_next() else None,
                'total_products': paginator.count,
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# def product_list(request):
#     return _product_list_base(request)

# def products_by_category(request, slug):
#     return _product_list_base(request, category_slug=slug)

# def products_by_brand(request, slug):
#     return _product_list_base(request, brand_slug=slug)

# def _product_list_base(request, category_slug=None, brand_slug=None):
#     # Get all filter parameters from GET request
#     query = request.GET.get('q', '')
#     category_slug_get = request.GET.get('category', '')
#     brand_slugs = request.GET.getlist('brand')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')
#     rating = request.GET.get('rating')
#     attribute_values = request.GET.getlist('attribute')
#     page = request.GET.get('page', 1)
#     sort = request.GET.get('sort', '')
    
#     # Base queryset
#     products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
#         'categories', 'images', 'reviews', 'attributes'
#     )
    
#     # Apply URL-based filters (from category/brand slug in URL)
#     subcategory_list = None
#     category = None
#     if category_slug:
#         # category = get_object_or_404(Category, slug=category_slug, is_active=True)
#         # products = products.filter(categories=category)
#         # if category:
#         #     subcategory_list = Category.objects.filter(parent=category)

        
#         category = get_object_or_404(Category, slug=category_slug, is_active=True)
#         # Get all descendant category IDs
#         descendant_ids = category.get_descendant_ids()
#         products = products.filter(categories__id__in=descendant_ids)
#         subcategory_list = Category.objects.filter(parent=category, is_active=True)
    
#     if brand_slug:
#         brand = get_object_or_404(Brand, slug=brand_slug)
#         products = products.filter(brand=brand)
    
#     # Apply GET parameter filters (from search/filter form)
#     if query:
#         products = products.filter(
#             Q(name__icontains=query) | 
#             Q(description__icontains=query) |
#             Q(sku__icontains=query)
#         )
    
#     if category_slug_get:
#         # category = get_object_or_404(Category, slug=category_slug_get, is_active=True)
#         # products = products.filter(categories=category)

#         category = get_object_or_404(Category, slug=category_slug_get, is_active=True)
#         # Get all descendant category IDs
#         descendant_ids = category.get_descendant_ids()
#         products = products.filter(categories__id__in=descendant_ids)
#         subcategory_list = Category.objects.filter(parent=category, is_active=True)
    
#     if brand_slugs:
#         products = products.filter(brand__slug__in=brand_slugs)
    
#     if min_price:
#         try:
#             min_price = float(min_price)
#             products = products.filter(
#                 Q(price__gte=min_price) | Q(discount_price__gte=min_price)
#             )
#         except (ValueError, TypeError):
#             pass
    
#     if max_price:
#         try:
#             max_price = float(max_price)
#             products = products.filter(
#                 Q(price__lte=max_price) | Q(discount_price__lte=max_price)
#             )
#         except (ValueError, TypeError):
#             pass
    
#     if rating:
#         try:
#             rating = float(rating)
#             # Get products with average rating >= selected value
#             product_ids = Review.objects.values('product').annotate(
#                 avg_rating=Avg('rating')
#             ).filter(avg_rating__gte=rating).values_list('product', flat=True)
#             products = products.filter(id__in=product_ids)
#         except (ValueError, TypeError):
#             pass
    
#     if attribute_values:
#         products = products.filter(attributes__id__in=attribute_values).distinct()
    
#     # Get top 10 brands (by product count) for the brand filter
#     top_brands = Brand.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).order_by('-product_count')[:10]
    
#     # Get all active categories for sidebar
#     categories = Category.objects.filter(is_active=True)
    
#     # Get all attributes with values for filtering
#     attributes = AttributeValue.objects.annotate(
#         product_count=Count('product')
#     ).filter(product_count__gt=0).select_related('attribute')
    
#     # Group attributes by their type
#     attribute_groups = {}
#     for attr in attributes:
#         if attr.attribute.name not in attribute_groups:
#             attribute_groups[attr.attribute.name] = []
#         attribute_groups[attr.attribute.name].append(attr)
    
#     # Determine the currently selected category (from URL or GET param)
#     selected_category = category_slug or category_slug_get
    
#     # Sorting
#     if sort == 'price_asc':
#         products = products.order_by('price')
#     elif sort == 'price_desc':
#         products = products.order_by('-price')
#     elif sort == 'rating':
#         products = products.annotate(
#             avg_rating=Avg('reviews__rating')
#         ).order_by('-avg_rating')
#     elif sort == 'newest':
#         products = products.order_by('-created_at')
#     elif sort == 'popular':
#         products = products.annotate(
#             review_count=Count('reviews')
#         ).order_by('-review_count')
#     else:
#         # Default sorting
#         products = products.order_by('-created_at')
    
#     # Pagination
#     paginator = Paginator(products, 12)  # Show 12 products per page
#     try:
#         products_page = paginator.get_page(page)
#     except:
#         products_page = paginator.get_page(1)
    
#     context = {
#         'products': products_page,
#         'query': query,
#         'categories': categories,
#         'selected_category': selected_category,
#         'selected_brand_slug': brand_slug,
#         'top_brands': top_brands,
#         'selected_brands': brand_slugs,
#         'min_price': min_price,
#         'max_price': max_price,
#         'selected_rating': rating,
#         'attribute_groups': attribute_groups,
#         'selected_attributes': attribute_values,
#         'sort_option': sort,
#         'subcategory_list':subcategory_list,
#         'category':category,
#     }
    
#     return render(request, 'shop/product_list.html', context)



# def product_detail(request, slug):
#     product = get_object_or_404(
#         Product.objects.select_related('brand')
#                       .prefetch_related('images', 'categories', 'variations__attributes__attribute'),
#         slug=slug,
#         is_active=True
#     )
    
#     # Get available variations
#     variations = {}
#     for variation in product.variations.filter(is_active=True, stock__gt=0):
#         for attr in variation.attributes.all():
#             if attr.attribute.name not in variations:
#                 variations[attr.attribute.name] = []
#             if attr.value not in variations[attr.attribute.name]:
#                 variations[attr.attribute.name].append(attr.value)
    
#     # Get related products (same categories)
#     related_products = Product.objects.filter(
#         categories__in=product.categories.all(),
#         is_active=True
#     ).exclude(id=product.id).distinct()[:8]
    
#     # Get frequently bought together (through order items)
#     from orders.models import OrderItem  # Import your OrderItem model
#     frequently_bought = Product.objects.filter(
#         orderitem__order__items__product=product
#     ).exclude(id=product.id).distinct().annotate(
#         freq_count=Count('id')
#     ).order_by('-freq_count')[:4]

#     if product.brand:
#         same_brand_products = product.brand.product_set.exclude(id=product.id)[:2]
#     else:
#         same_brand_products = None

#     payment_methods = PaymentMethod.objects.filter(is_active=True)

#     countries = Country.objects.filter(is_active=True)

#     context = {
#         'product': product,
#         'variations': variations,
#         'related_products': related_products,
#         'frequently_bought_together': frequently_bought,
#         'same_brand_products': same_brand_products,
#         'payment_methods': payment_methods,
#         'countries': countries,
#     }
#     return render(request, 'shop/product_detail.html', context)

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('brand')
                      .prefetch_related('images', 'categories', 'variations__attributes__attribute'),
        slug=slug,
        is_active=True
    )
    
    # Get available variations
    variations = {}
    for variation in product.variations.filter(is_active=True, stock__gt=0):
        for attr in variation.attributes.all():
            if attr.attribute.name not in variations:
                variations[attr.attribute.name] = []
            if attr.value not in variations[attr.attribute.name]:
                variations[attr.attribute.name].append(attr.value)
    
    # Get related products (same categories)
    related_products = Product.objects.filter(
        categories__in=product.categories.all(),
        is_active=True
    ).exclude(id=product.id).distinct()[:8]
    
    # Get frequently bought together (through order items)
    from orders.models import OrderItem  # Import your OrderItem model
    frequently_bought = Product.objects.filter(
        orderitem__order__items__product=product
    ).exclude(id=product.id).distinct().annotate(
        freq_count=Count('id')
    ).order_by('-freq_count')[:4]

    if product.brand:
        same_brand_products = product.brand.product_set.exclude(id=product.id)[:2]
    else:
        same_brand_products = None

    payment_methods = PaymentMethod.objects.filter(is_active=True)
    countries = Country.objects.filter(is_active=True)

    # Days range for birth date dropdown
    days_range = range(1, 32)  # 1 to 31

    context = {
        'product': product,
        'variations': variations,
        'related_products': related_products,
        'frequently_bought_together': frequently_bought,
        'same_brand_products': same_brand_products,
        'payment_methods': payment_methods,
        'countries': countries,
        'days_range':days_range
    }
    return render(request, 'shop/product_detail.html', context)




    
def get_product_variation_price(request):
    print("get_product_variation_price")
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        attributes = json.loads(request.POST.get('attributes'))
        
        try:
            product = Product.objects.get(id=product_id)
            variations = product.variations.filter(is_active=True)
            
            # Filter variations based on selected attributes
            for attr_name, attr_value in attributes.items():
                variations = variations.filter(attributes__value=attr_value)
            
            if variations.exists():
                variation = variations.first()
                return JsonResponse({
                    'price': str(variation.get_price()),
                    'original_price': str(variation.price) if variation.price else str(product.price),
                    'stock': variation.stock
                })
            
            return JsonResponse({
                'price': str(product.get_price()),
                'original_price': str(product.price),
                'stock': 0
            })
            
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

def add_to_cart(request, product_id):
    if request.method == 'POST':
        # Handle adding to cart logic here
        # Get selected variations, quantity, etc.
        pass

def get_product_variant(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        selected_attrs = json.loads(request.POST.get('attributes'))
        
        try:
            product = Product.objects.get(id=product_id)
            variations = product.variations.filter(is_active=True)
            
            # Filter variations that match all selected attributes
            for attr_name, attr_value in selected_attrs.items():
                variations = variations.filter(
                    attributes__attribute__name=attr_name,
                    attributes__value=attr_value
                )
            
            if variations.exists():
                variant = variations.first()
                return JsonResponse({
                    'variant': {
                        'id': variant.id,
                        'price': str(variant.get_price()),
                        'stock': variant.stock,
                        'sku': variant.sku
                    }
                })
            
            return JsonResponse({'error': 'No matching variant found'}, status=404)
        
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)



def category_list(request):
    categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')
    return render(request, 'products/category_list.html', {'categories': categories})

def brand_list(request):
    brands = Brand.objects.filter(is_active=True)
    return render(request, 'products/brand_list.html', {'brands': brands})