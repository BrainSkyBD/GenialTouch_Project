from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.db.models import Sum, Avg, Count
from imagekit.models import ProcessedImageField, ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit, SmartResize
from imagekit.processors import ResizeToFit, ResizeToFill, Transpose
from imagekit import ImageSpec
from PIL import Image



class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    logo = ProcessedImageField(
        upload_to='brands/',
        processors=[ResizeToFill(200, 200)],  # Resize to 200x200
        format='WEBP',
        options={'quality': 85},
        blank=True
    )
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
    
    # Regular image - will be converted to WebP automatically
    image = ProcessedImageField(
        upload_to='categories/image/',
        processors=[ResizeToFill(400, 400)],  # Square 400x400
        format='WEBP',
        options={'quality': 85},
        blank=True
    )
    
    # Banner image - different dimensions
    banner = ProcessedImageField(
        upload_to='categories/banner/',
        processors=[ResizeToFit(1200, 400)],  # Wide banner 1200x400
        format='WEBP',
        options={'quality': 85},
        blank=True,
        null=True
    )
    
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
            'image_url': main_image.thumbnail.url if main_image else '/static/img/no-image.jpg',
            'url': self.get_absolute_url(),
            'is_in_stock': self.is_in_stock(),
            'sku': self.sku,
            'short_description': self.description[:100] + '...' if len(self.description) > 100 else self.description,
        }

    
    def get_main_image_url(self):
        """Optimized method to get main image URL without extra queries"""
        # Try to get from prefetched images first
        if hasattr(self, 'images'):
            for image in self.images.all():
                if image.is_featured:
                    return image.thumbnail.url  # Changed to use thumbnail
            if self.images.first():
                return self.images.first().thumbnail.url
        return '/static/img/no-image.jpg'
    
    def get_price_display(self):
        """Get price display without extra queries"""
        if self.discount_price:
            return self.discount_price
        return self.price
    
    def get_short_description(self):
        """Get short description without slicing in template"""
        if len(self.description) > 100:
            return self.description[:100] + '...'
        return self.description
    
    def get_specifications(self):
        """Get product specifications with optimized query"""
        from django.db.models import Prefetch
        
        return ProductAttribute.objects.filter(
            product=self
        ).select_related(
            'attribute_value__attribute'
        )
    
    @property
    def review_list(self):
        """Get approved reviews for this product"""
        try:
            from reviews.models import Review
            return Review.objects.filter(product=self, is_approved=True)
        except:
            return []
    
    @property
    def average_rating(self):
        """Calculate average rating"""
        try:
            from reviews.models import Review
            reviews = Review.objects.filter(product=self, is_approved=True)
            if reviews.exists():
                return reviews.aggregate(models.Avg('rating'))['rating__avg']
            return 0
        except:
            return 0
    
    @property
    def review_count(self):
        """Count of approved reviews"""
        try:
            from reviews.models import Review
            return Review.objects.filter(product=self, is_approved=True).count()
        except:
            return 0
    
    @property
    def avg_rating(self):
        """Return average approved rating rounded to 1 decimal"""
        try:
            from reviews.models import Review
            result = Review.objects.filter(
                product=self,
                is_approved=True
            ).aggregate(avg=Avg('rating'))['avg']

            return round(result, 1) if result else 0
        except Exception:
            return 0





# First, create a custom processor to handle color properly
class PreserveColorProcessor:
    def process(self, img):
        # Convert RGBA to RGB if needed (removes alpha channel)
        if img.mode in ('RGBA', 'LA'):
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on white background
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else img)
            img = background
        elif img.mode == 'P':
            img = img.convert('RGB')
        return img


    


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    
    # Original image - converted to WebP and resized
    # image = ProcessedImageField(
    #     upload_to='products/',
    #     # processors=[ResizeToFit(1200, 1200)],  # Max size 1200x1200, maintains aspect ratio
    #     format='WEBP',
    #     options={'quality': 85}
    # )

    
    image = ProcessedImageField(
        upload_to='products/',
        processors=[
            PreserveColorProcessor(),  # Add this processor first
            ResizeToFit(1200, 1200),   # Then resize
            Transpose(),               # Auto-rotate based on EXIF
        ],
        format='WEBP',
        options={'quality': 85}
    )
    
    # Image specifications - generated on the fly
    thumbnail = ImageSpecField(
        source='image',
        # processors=[SmartResize(400, 400)],  # Square 400x400 thumbnail
        format='WEBP',
        options={'quality': 80}
    )
    
    small = ImageSpecField(
        source='image',
        # processors=[SmartResize(200, 200)],  # Small 200x200
        format='WEBP',
        options={'quality': 75}
    )
    
    medium = ImageSpecField(
        source='image',
        # processors=[SmartResize(800, 800)],  # Medium 800x800
        format='WEBP',
        options={'quality': 85}
    )
    
    # Optional: For gallery with exact dimensions
    gallery = ImageSpecField(
        source='image',
        processors=[ResizeToFill(800, 600)],  # Fixed 800x600 for gallery
        format='WEBP',
        options={'quality': 85}
    )
    
    alt_text = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'id']
        indexes = [
            models.Index(fields=['product', 'is_featured', 'display_order']),
            models.Index(fields=['product', 'display_order']),
        ]
    
    def __str__(self):
        return f"Image of {self.product.name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'image_url': self.image.url,
            'thumbnail_url': self.thumbnail.url,  # Added thumbnail URL
            'medium_url': self.medium.url,        # Added medium URL
            'alt_text': self.alt_text,
            'is_featured': self.is_featured,
        }
    
    # Optional: Add a property for backward compatibility
    @property
    def image_url(self):
        return self.image.url


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