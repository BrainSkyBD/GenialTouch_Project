from django.contrib import admin
from .models import Brand, Category, Attribute, AttributeValue, Product, ProductImage, ProductAttribute, ProductVariation

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'is_active', 'is_featured')
    list_filter = ('brand', 'categories', 'is_active', 'is_featured')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeInline, ProductVariationInline]

    actions = ['duplicate_product']
    
    def duplicate_product(self, request, queryset):
        for product in queryset:
            # Create a copy of the product
            product.pk = None
            product.slug = f"{product.slug}-copy"
            product.sku = f"{product.sku}-copy"
            product.name = f"{product.name} (Copy)"
            product.save()
            
            # Copy categories
            product.categories.set(product.categories.all())
            
            # Copy images
            for image in product.images.all():
                image.pk = None
                image.product = product
                image.save()
            
            # Copy attributes
            for attr in product.productattribute_set.all():
                attr.pk = None
                attr.product = product
                attr.save()
            
            # Copy variations
            for variation in product.variations.all():
                variation.pk = None
                variation.product = product
                variation.save()
                variation.attributes.set(variation.attributes.all())
                
        self.message_user(request, f"Successfully duplicated {len(queryset)} product(s).")
    
    duplicate_product.short_description = "Duplicate selected products"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('parent', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Attribute)
admin.site.register(AttributeValue)

# admin.site.register(ProductAttribute)
# admin.site.register(ProductVariation)

