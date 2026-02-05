from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Sum, Avg, Count


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'name']),
            models.Index(fields=['slug']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'logo': self.logo.url if self.logo else None,
        }


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/image/', blank=True)
    banner = models.ImageField(upload_to='categories/banner/', blank=True, default=None, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active', 'is_featured']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
            models.Index(fields=['display_order']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products_by_category', args=[self.slug])
    
    def get_descendants(self):
        """Get all descendant categories including self"""
        descendants = [self]
        for child in self.children.all():
            descendants.extend(child.get_descendants())
        return descendants
    
    def get_descendant_ids(self):
        """Get all descendant category IDs including self"""
        return [cat.id for cat in self.get_descendants()]
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'image': self.image.url if self.image else None,
            'url': self.get_absolute_url(),
        }


class Attribute(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    
    class Meta:
        indexes = [
            models.Index(fields=['attribute', 'value']),
        ]
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    categories = models.ManyToManyField(Category)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    attributes = models.ManyToManyField(AttributeValue, through='ProductAttribute')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['price']),
            models.Index(fields=['brand']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])
    
    def get_price(self):
        return self.discount_price if self.discount_price else self.price
    
    def is_in_stock(self):
        return any(variation.stock > 0 for variation in self.variations.all())
    
    def get_discount_percentage(self):
        if self.discount_price and self.price:
            discount = ((self.price - self.discount_price) / self.price) * 100
            return round(discount)
        return 0
    
    def get_total_stock(self):
        return self.variations.aggregate(total_stock=Sum('stock'))['total_stock'] or 0
    
    def get_main_image(self):
        """Get the featured image or first image"""
        featured = self.images.filter(is_featured=True).first()
        if featured:
            return featured
        return self.images.first()
    
    def to_dict(self):
        """Convert product to dictionary for AJAX responses"""
        main_image = self.get_main_image()
        
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'price': str(self.price),
            'discount_price': str(self.discount_price) if self.discount_price else None,
            'discount_percentage': self.get_discount_percentage(),
            'brand': self.brand.to_dict() if self.brand else None,
            'image_url': main_image.image.url if main_image else '/static/img/no-image.jpg',
            'url': self.get_absolute_url(),
            'is_in_stock': self.is_in_stock(),
            'sku': self.sku,
            'short_description': self.description[:100] + '...' if len(self.description) > 100 else self.description,
        }


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['product', 'is_featured']),
            models.Index(fields=['product', 'display_order']),
        ]
    
    def __str__(self):
        return f"Image of {self.product.name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image.url,
            'alt_text': self.alt_text,
            'is_featured': self.is_featured,
        }


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('product', 'attribute_value')
        indexes = [
            models.Index(fields=['product', 'attribute_value']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute_value}"


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    attributes = models.ManyToManyField(AttributeValue)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {', '.join(str(attr) for attr in self.attributes.all())}"
    
    def get_price(self):
        return self.price if self.price else self.product.get_price()