from django.contrib import admin
from .models import Brand, Category, Attribute, AttributeValue, Product, ProductImage, ProductAttribute, ProductVariation



# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1

# class ProductAttributeInline(admin.TabularInline):
#     model = ProductAttribute
#     extra = 1

# class ProductVariationInline(admin.TabularInline):
#     model = ProductVariation
#     extra = 1

# @admin.register(Product)
# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('name', 'brand', 'price', 'is_active', 'is_featured')
#     list_filter = ('brand', 'categories', 'is_active', 'is_featured')
#     search_fields = ('name', 'description', 'sku')
#     prepopulated_fields = {'slug': ('name',)}
#     inlines = [ProductImageInline, ProductAttributeInline, ProductVariationInline]

#     actions = ['duplicate_product']
    
#     def duplicate_product(self, request, queryset):
#         for product in queryset:
#             # Create a copy of the product
#             product.pk = None
#             product.slug = f"{product.slug}-copy"
#             product.sku = f"{product.sku}-copy"
#             product.name = f"{product.name} (Copy)"
#             product.save()
            
#             # Copy categories
#             product.categories.set(product.categories.all())
            
#             # Copy images
#             for image in product.images.all():
#                 image.pk = None
#                 image.product = product
#                 image.save()
            
#             # Copy attributes
#             for attr in product.productattribute_set.all():
#                 attr.pk = None
#                 attr.product = product
#                 attr.save()
            
#             # Copy variations
#             for variation in product.variations.all():
#                 variation.pk = None
#                 variation.product = product
#                 variation.save()
#                 variation.attributes.set(variation.attributes.all())
                
#         self.message_user(request, f"Successfully duplicated {len(queryset)} product(s).")
    
#     duplicate_product.short_description = "Duplicate selected products"

from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Category, Attribute, AttributeValue, Product, ProductImage, ProductAttribute, ProductVariation

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image_preview', 'image', 'alt_text', 'is_featured', 'display_order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.id and obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />',
                obj.thumbnail.url
            )
        return format_html(
            '<div style="width:80px;height:80px;background:#f8f9fa;display:flex;align-items:center;justify-content:center;border-radius:4px;border:1px dashed #ddd;color:#6c757d;">No image</div>'
        )
    image_preview.short_description = 'Preview'

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_tag', 'name', 'brand', 'price', 'is_active', 'is_featured', 'stock_status')
    list_display_links = ('image_tag', 'name')
    list_filter = ('brand', 'categories', 'is_active', 'is_featured')
    search_fields = ('name', 'description', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductAttributeInline, ProductVariationInline]
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'brand', 'categories', 'description', 'product_keywords')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'is_active', 'is_featured')
        }),
        ('Safety & Caution', {  # New section
            'fields': ('caution',),
            'classes': ('wide',),
            'description': 'Add safety warnings, precautions, and usage guidelines for this product.'
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'main_image_preview')
    
    def image_tag(self, obj):
        main_image = obj.get_main_image()
        if main_image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                main_image.thumbnail.url
            )
        return format_html(
            '<div style="width:50px;height:50px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;border-radius:4px;">📷</div>'
        )
    image_tag.short_description = 'Image'
    
    def stock_status(self, obj):
        total_stock = obj.get_total_stock()
        if total_stock > 10:
            color = 'green'
            status = f'In Stock ({total_stock})'
        elif total_stock > 0:
            color = 'orange'
            status = f'Low Stock ({total_stock})'
        else:
            color = 'red'
            status = 'Out of Stock'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    stock_status.short_description = 'Stock Status'
    
    def main_image_preview(self, obj):
        main_image = obj.get_main_image()
        if main_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px; border-radius: 8px; border: 1px solid #ddd;" />',
                main_image.medium.url
            )
        return "No image uploaded"
    main_image_preview.short_description = 'Main Image Preview'
    
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

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'parent', 'is_active')
#     list_filter = ('parent', 'is_active')
#     search_fields = ('name', 'description')
#     prepopulated_fields = {'slug': ('name',)}

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'parent', 'is_active', 'is_featured', 'display_order')
    list_display_links = ('image_preview', 'name')
    list_filter = ('parent', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order', 'is_active', 'is_featured')
    list_per_page = 25
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'parent', 'description')
        }),
        ('Images', {
            'fields': ('image_preview_detail', 'image', 'banner')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_featured', 'display_order')
        }),
    )
    readonly_fields = ('image_preview_detail',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return format_html('<div style="width:50px;height:50px;background:#f0f0f0;border-radius:4px;"></div>')
    image_preview.short_description = 'Image'
    
    def image_preview_detail(self, obj):
        if obj.image:
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<strong>Category Image:</strong><br>'
                '<img src="{}" style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 1px solid #ddd;" />'
                '</div>',
                obj.image.url
            )
        return "No image uploaded"
    image_preview_detail.short_description = 'Current Image'

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'is_active', 'product_count')
    list_display_links = ('logo_preview', 'name')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Logo', {
            'fields': ('logo_preview_detail', 'logo')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('logo_preview_detail', 'product_count')
    
    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: contain; border-radius: 4px;" />',
                obj.logo.url
            )
        return format_html('<div style="width:50px;height:50px;background:#f0f0f0;border-radius:4px;"></div>')
    logo_preview.short_description = 'Logo'
    
    def logo_preview_detail(self, obj):
        if obj.logo:
            return format_html(
                '<div style="margin-bottom: 10px;">'
                '<strong>Brand Logo:</strong><br>'
                '<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: contain; border: 1px solid #ddd; border-radius: 8px;" />'
                '</div>',
                obj.logo.url
            )
        return "No logo uploaded"
    logo_preview_detail.short_description = 'Current Logo'
    
    def product_count(self, obj):
        count = obj.product_set.count()
        return format_html(
            '<span style="background: #007bff; color: white; padding: 3px 10px; border-radius: 12px;">{}</span>',
            count
        )
    product_count.short_description = 'Products'

admin.site.register(Attribute)
admin.site.register(AttributeValue)

# admin.site.register(ProductAttribute)
# admin.site.register(ProductVariation)

