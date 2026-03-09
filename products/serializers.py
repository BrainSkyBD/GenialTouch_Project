from rest_framework import serializers
from .models import Product, Category, Brand, ProductImage, ProductVariation, AttributeValue

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'image', 'is_active']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description']

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image_url', 'thumbnail_url', 'alt_text', 'is_featured', 'display_order']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

class AttributeValueSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name')
    
    class Meta:
        model = AttributeValue
        fields = ['id', 'attribute_name', 'value']

class ProductVariationSerializer(serializers.ModelSerializer):
    attributes = AttributeValueSerializer(many=True, read_only=True)
    price_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariation
        fields = ['id', 'sku', 'price', 'price_display', 'stock', 'is_active', 'attributes']
    
    def get_price_display(self, obj):
        return str(obj.get_price())

class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    brand_slug = serializers.CharField(source='brand.slug', read_only=True)
    main_image = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    original_price_display = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand_name', 'brand_slug',
            'price_display', 'original_price_display', 'discount_percentage',
            'main_image', 'is_in_stock', 'average_rating', 'review_count',
            'is_featured', 'created_at'
        ]
    
    def get_main_image(self, obj):
        request = self.context.get('request')
        main_image = obj.get_main_image()
        if main_image and main_image.image and request:
            return request.build_absolute_uri(main_image.image.url)
        return None
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()
    
    def get_price_display(self, obj):
        return str(obj.get_price())
    
    def get_original_price_display(self, obj):
        return str(obj.price) if obj.discount_price else None
    
    def get_is_in_stock(self, obj):
        return obj.is_in_stock()

class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    attributes = serializers.SerializerMethodField()
    price_display = serializers.SerializerMethodField()
    original_price_display = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'description',
            'brand', 'categories', 'images',
            'price_display', 'original_price_display', 'discount_percentage',
            'variations', 'attributes', 'total_stock',
            'average_rating', 'review_count',
            'is_featured', 'is_active',
            'created_at', 'updated_at', 'view_count'
        ]
    
    def get_price_display(self, obj):
        return str(obj.get_price())
    
    def get_original_price_display(self, obj):
        return str(obj.price) if obj.discount_price else None
    
    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()
    
    def get_total_stock(self, obj):
        return obj.get_total_stock()
    
    def get_attributes(self, obj):
        """Group attributes by their type"""
        attributes = {}
        for product_attr in obj.productattribute_set.all():
            attr_name = product_attr.attribute_value.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = []
            attributes[attr_name].append({
                'id': product_attr.attribute_value.id,
                'value': product_attr.attribute_value.value
            })
        return attributes