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
from .models import Product, Category, Brand, AttributeValue, Attribute
from django.db.models import Q
from django.http import JsonResponse
from orders.models import PaymentMethod, Order, OrderItem, Country, District, TaxConfiguration




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






def product_list(request):
    return _product_list_base(request)

def products_by_category(request, slug):
    return _product_list_base(request, category_slug=slug)

def products_by_brand(request, slug):
    return _product_list_base(request, brand_slug=slug)

def _product_list_base(request, category_slug=None, brand_slug=None):
    # Get all filter parameters from GET request
    query = request.GET.get('q', '')
    category_slug_get = request.GET.get('category', '')
    brand_slugs = request.GET.getlist('brand')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')
    attribute_values = request.GET.getlist('attribute')
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '')
    
    # Base queryset
    products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related(
        'categories', 'images', 'reviews', 'attributes'
    )
    
    # Apply URL-based filters (from category/brand slug in URL)
    subcategory_list = None
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = products.filter(categories=category)
        if category:
            subcategory_list = Category.objects.filter(parent=category)
    
    if brand_slug:
        brand = get_object_or_404(Brand, slug=brand_slug)
        products = products.filter(brand=brand)
    
    # Apply GET parameter filters (from search/filter form)
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )
    
    if category_slug_get:
        category = get_object_or_404(Category, slug=category_slug_get, is_active=True)
        products = products.filter(categories=category)
    
    if brand_slugs:
        products = products.filter(brand__slug__in=brand_slugs)
    
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(
                Q(price__gte=min_price) | Q(discount_price__gte=min_price)
            )
        except (ValueError, TypeError):
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(
                Q(price__lte=max_price) | Q(discount_price__lte=max_price)
            )
        except (ValueError, TypeError):
            pass
    
    if rating:
        try:
            rating = float(rating)
            # Get products with average rating >= selected value
            product_ids = Review.objects.values('product').annotate(
                avg_rating=Avg('rating')
            ).filter(avg_rating__gte=rating).values_list('product', flat=True)
            products = products.filter(id__in=product_ids)
        except (ValueError, TypeError):
            pass
    
    if attribute_values:
        products = products.filter(attributes__id__in=attribute_values).distinct()
    
    # Get top 10 brands (by product count) for the brand filter
    top_brands = Brand.objects.annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count')[:10]
    
    # Get all active categories for sidebar
    categories = Category.objects.filter(is_active=True)
    
    # Get all attributes with values for filtering
    attributes = AttributeValue.objects.annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).select_related('attribute')
    
    # Group attributes by their type
    attribute_groups = {}
    for attr in attributes:
        if attr.attribute.name not in attribute_groups:
            attribute_groups[attr.attribute.name] = []
        attribute_groups[attr.attribute.name].append(attr)
    
    # Determine the currently selected category (from URL or GET param)
    selected_category = category_slug or category_slug_get
    
    # Sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.annotate(
            avg_rating=Avg('reviews__rating')
        ).order_by('-avg_rating')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'popular':
        products = products.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')
    else:
        # Default sorting
        products = products.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    try:
        products_page = paginator.get_page(page)
    except:
        products_page = paginator.get_page(1)
    
    context = {
        'products': products_page,
        'query': query,
        'categories': categories,
        'selected_category': selected_category,
        'selected_brand_slug': brand_slug,
        'top_brands': top_brands,
        'selected_brands': brand_slugs,
        'min_price': min_price,
        'max_price': max_price,
        'selected_rating': rating,
        'attribute_groups': attribute_groups,
        'selected_attributes': attribute_values,
        'sort_option': sort,
        'subcategory_list':subcategory_list,
        'category':category,
    }
    
    return render(request, 'shop/product_list.html', context)



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

    context = {
        'product': product,
        'variations': variations,
        'related_products': related_products,
        'frequently_bought_together': frequently_bought,
        'same_brand_products': same_brand_products,
        'payment_methods': payment_methods,
        'countries': countries,
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