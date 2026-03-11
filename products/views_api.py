from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q, Prefetch, Avg, Count, Min, Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Product, Category, Brand
from .serializers import ProductListSerializer, ProductDetailSerializer

class ProductListView(generics.ListAPIView):
    """
    API endpoint for product listing with filtering, searching, and sorting
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name', 'view_count']
    
    def get_queryset(self):
        """
        Optimized queryset with filtering - NO annotations that conflict with model fields
        """
        queryset = Product.objects.filter(
            is_active=True
        ).select_related(
            'brand'
        ).prefetch_related(
            'images',
            'reviews'
        ).distinct()  # Remove duplicates
        
        # Apply filters from query params
        params = self.request.query_params
        
        # Category filter
        category_slug = params.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
                descendant_ids = category.get_descendant_ids()
                queryset = queryset.filter(categories__id__in=descendant_ids)
            except Category.DoesNotExist:
                queryset = queryset.none()
        
        # Brand filter
        brand_slugs = params.getlist('brand')
        if brand_slugs:
            queryset = queryset.filter(brand__slug__in=brand_slugs)
        
        # Price range filter
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        
        if min_price:
            try:
                min_price_val = float(min_price)
                queryset = queryset.filter(
                    Q(price__gte=min_price_val) |
                    Q(discount_price__gte=min_price_val)
                )
            except (ValueError, TypeError):
                pass
        
        if max_price:
            try:
                max_price_val = float(max_price)
                queryset = queryset.filter(
                    Q(price__lte=max_price_val) |
                    Q(discount_price__lte=max_price_val)
                )
            except (ValueError, TypeError):
                pass
        
        # Rating filter - using subquery instead of annotation
        rating = params.get('rating')
        if rating:
            try:
                rating_val = float(rating)
                from reviews.models import Review
                # Get product IDs with average rating >= rating_val
                product_ids = Review.objects.filter(
                    is_approved=True
                ).values('product').annotate(
                    avg_rating=Avg('rating')
                ).filter(avg_rating__gte=rating_val).values_list('product', flat=True)
                
                queryset = queryset.filter(id__in=product_ids)
            except (ValueError, TypeError, ImportError):
                pass
        
        # Featured filter
        featured = params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # Attribute filter
        attribute_values = params.getlist('attribute')
        if attribute_values:
            queryset = queryset.filter(attributes__id__in=attribute_values).distinct()
        
        return queryset
    
    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductDetailView(generics.RetrieveAPIView):
    """
    API endpoint for single product details
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        # Increment view count
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        
        return super().retrieve(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_filter_options(request):
    """
    Get available filter options (brands, price range, attributes) for current context
    """
    # Get base queryset based on category
    queryset = Product.objects.filter(is_active=True)
    
    category_slug = request.query_params.get('category')
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, is_active=True)
            descendant_ids = category.get_descendant_ids()
            queryset = queryset.filter(categories__id__in=descendant_ids)
        except Category.DoesNotExist:
            pass
    
    # Get brands with counts
    brands = Brand.objects.filter(
        product__in=queryset.values('id'),
        is_active=True
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).order_by('-product_count')
    
    brand_data = [
        {
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug,
            'logo': request.build_absolute_uri(brand.logo.url) if brand.logo else None,
            'product_count': brand.product_count
        }
        for brand in brands
    ]
    
    # Get price range
    price_range = queryset.aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    # Get attributes with counts
    from .models import AttributeValue
    attributes = AttributeValue.objects.filter(
        product__in=queryset.values('id')
    ).annotate(
        product_count=Count('product')
    ).filter(product_count__gt=0).select_related('attribute').order_by('attribute__name', 'value')
    
    attribute_groups = {}
    for attr in attributes:
        attr_name = attr.attribute.name
        if attr_name not in attribute_groups:
            attribute_groups[attr_name] = []
        attribute_groups[attr_name].append({
            'id': attr.id,
            'value': attr.value,
            'product_count': attr.product_count
        })
    
    return Response({
        'brands': brand_data,
        'price_range': {
            'min': float(price_range['min_price'] or 0),
            'max': float(price_range['max_price'] or 0)
        },
        'attributes': attribute_groups
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def get_related_products(request, product_id):
    """
    Get related products for a given product
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Get first category
        category = product.categories.filter(is_active=True).first()
        
        if category:
            related = Product.objects.filter(
                categories=category,
                is_active=True
            ).exclude(id=product.id).select_related('brand')[:8]
            
            serializer = ProductListSerializer(related, many=True, context={'request': request})
            return Response(serializer.data)
        
        return Response([])
        
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=404)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_frequently_bought(request, product_id):
    """
    Get frequently bought together products
    """
    try:
        from orders.models import OrderItem
        
        frequently_bought = Product.objects.filter(
            orderitem__order__items__product_id=product_id,
            is_active=True
        ).exclude(id=product_id).distinct()[:4]
        
        serializer = ProductListSerializer(frequently_bought, many=True, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        return Response([])