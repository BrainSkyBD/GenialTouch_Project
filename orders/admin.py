from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Country, District, Thana, TaxConfiguration, 
    PaymentMethod, Order, OrderItem, OrderTrackingTableNew
)


from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import io
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from .models import Order, OrderItem, OrderTrackingTableNew
from orders.views import generate_pdf_invoice




class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'district_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    list_per_page = 20
    
    def district_count(self, obj):
        return obj.district_set.count()
    district_count.short_description = 'Districts'


class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'shipping_cost', 'thana_count', 'is_active')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'country__name')
    list_select_related = ('country',)
    list_per_page = 20
    
    def thana_count(self, obj):
        return obj.thana_set.count()
    thana_count.short_description = 'Thanas'


class ThanaAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'country', 'is_active')
    list_filter = ('district__country', 'district', 'is_active')
    search_fields = ('name', 'district__name', 'district__country__name')
    list_select_related = ('district__country',)
    list_per_page = 20
    
    def country(self, obj):
        return obj.district.country.name
    country.short_description = 'Country'


class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'applies_to_all', 'country_count', 'created_at')
    list_filter = ('is_active', 'applies_to_all')
    search_fields = ('name',)
    filter_horizontal = ('countries',)
    list_per_page = 20
    
    def country_count(self, obj):
        if obj.applies_to_all:
            return "All"
        return obj.countries.count()
    country_count.short_description = 'Countries'


class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_icon', 'is_active', 'order_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    readonly_fields = ('preview_icon',)
    list_per_page = 20
    
    def display_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" style="border-radius: 5px;" />', obj.icon.url)
        return "No Icon"
    display_icon.short_description = 'Icon'
    
    def preview_icon(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 5px;" />', obj.icon.url)
        return "No Icon"
    preview_icon.short_description = 'Icon Preview'
    
    def order_count(self, obj):
        return Order.objects.filter(payment_method=obj).count()
    order_count.short_description = 'Orders'


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     readonly_fields = ('product', 'variation', 'quantity', 'price', 'get_total', 'created_at')
#     fields = ('product', 'variation', 'quantity', 'price', 'get_total')
#     extra = 0
#     can_delete = False
#     max_num = 0  # Prevent adding new items
    
#     def get_total(self, obj):
#         return f"${obj.get_total()}" if obj.get_total() else "-"
#     get_total.short_description = 'Total'
    
#     def has_add_permission(self, request, obj=None):
#         return False


class OrderTrackingTableNewInline(admin.TabularInline):
    model = OrderTrackingTableNew
    readonly_fields = ('status', 'note', 'created_at')
    fields = ('status', 'note', 'created_at')
    extra = 0
    max_num = 10
    
    def has_change_permission(self, request, obj=None):
        return False


# class OrderAdmin(admin.ModelAdmin):
#     list_display = (
#         'order_number', 'get_full_name', 'email', 'phone_number', 
#         'country', 'district', 'status', 'grand_total', 'created_at', 
#         'payment_method'
#     )
#     list_filter = ('status', 'country', 'district', 'created_at', 'payment_method', 'birth_month')
#     search_fields = (
#         'order_number', 'first_name', 'last_name', 'email', 
#         'phone_number', 'full_address'
#     )
#     readonly_fields = (
#         'order_number', 'user', 'get_full_name', 'email', 'phone_number', 
#         'full_address', 'country', 'district', 'thana', 'postal_code', 
#         'order_note', 'order_total', 'tax', 'tax_rate', 'tax_amount', 
#         'grand_total', 'ip_address', 'created_at', 'updated_at',
#         'shipping_cost', 'payment_method', 'payment_details',
#         'get_formatted_address'
#     )
#     # fieldsets = (
#     #     ('Order Information', {
#     #         'fields': ('order_number', 'user', 'status', 'is_ordered', 'created_at', 'updated_at')
#     #     }),
#     #     ('Customer Information', {
#     #         'fields': ('get_full_name', 'email', 'phone_number')
#     #     }),
#     #     ('Shipping Information', {
#     #         'fields': (
#     #             'get_formatted_address', 'full_address', 'country', 
#     #             'district', 'thana', 'postal_code', 'shipping_cost'
#     #         )
#     #     }),
#     #     ('Order Details', {
#     #         'fields': (
#     #             'order_note', 'order_total', 'tax', 'tax_rate', 
#     #             'tax_amount', 'grand_total'
#     #         )
#     #     }),
#     #     ('Payment Information', {
#     #         'fields': ('payment_method', 'payment_details')
#     #     }),
#     #     ('Technical Information', {
#     #         'fields': ('ip_address',)
#     #     }),
#     # )
#     fieldsets = (
#         ('Order Information', {
#             'fields': ('order_number', 'status', 'user', 'created_at')
#         }),
#         ('Customer Information', {
#             'fields': ('first_name', 'last_name', 'email', 'phone_number', 
#                       'birth_date', 'birth_month')
#         }),
#         ('Shipping Information', {
#             'fields': ('full_address', 'country', 'district', 'thana', 'postal_code')
#         }),
#         ('Payment Information', {
#             'fields': ('payment_method', 'order_total', 'shipping_cost', 
#                       'tax_rate', 'tax_amount', 'grand_total')
#         }),
#         ('Additional Information', {
#             'fields': ('order_note', 'ip_address', 'is_ordered')
#         }),
#     )
#     inlines = [OrderItemInline, OrderTrackingTableNewInline]
#     list_per_page = 20
#     actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']
    
#     def get_full_name(self, obj):
#         return obj.get_full_name()
#     get_full_name.short_description = 'Customer Name'
    
#     def get_formatted_address(self, obj):
#         return format_html(
#             '<div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 4px solid #007bff;">'
#             '<strong>Full Address:</strong><br>{}<br><br>'
#             '<strong>Location Details:</strong><br>'
#             '<small>Country: {}<br>'
#             'District: {}<br>'
#             'Thana: {}<br>'
#             'Postal Code: {}</small></div>',
#             obj.full_address,
#             obj.country.name if obj.country else '-',
#             obj.district.name if obj.district else '-',
#             obj.thana.name if obj.thana else '-',
#             obj.postal_code if obj.postal_code else '-'
#         )
#     get_formatted_address.short_description = 'Address Details'
    
#     def mark_as_processing(self, request, queryset):
#         queryset.update(status='processing')
#         for order in queryset:
#             OrderTrackingTableNew.objects.create(order=order, status='processing', note='Status changed by admin')
#         self.message_user(request, f"{queryset.count()} orders marked as processing.")
#     mark_as_processing.short_description = "Mark selected orders as Processing"
    
#     def mark_as_shipped(self, request, queryset):
#         queryset.update(status='shipped')
#         for order in queryset:
#             OrderTrackingTableNew.objects.create(order=order, status='shipped', note='Status changed by admin')
#         self.message_user(request, f"{queryset.count()} orders marked as shipped.")
#     mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
#     def mark_as_delivered(self, request, queryset):
#         queryset.update(status='delivered')
#         for order in queryset:
#             OrderTrackingTableNew.objects.create(order=order, status='delivered', note='Status changed by admin')
#         self.message_user(request, f"{queryset.count()} orders marked as delivered.")
#     mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
#     def mark_as_cancelled(self, request, queryset):
#         queryset.update(status='cancelled')
#         for order in queryset:
#             OrderTrackingTableNew.objects.create(order=order, status='cancelled', note='Status changed by admin')
#         self.message_user(request, f"{queryset.count()} orders marked as cancelled.")
#     mark_as_cancelled.short_description = "Mark selected orders as Cancelled"
    
#     def get_readonly_fields(self, request, obj=None):
#         # Make all fields readonly if order is already delivered or cancelled
#         if obj and obj.status in ['delivered', 'cancelled', 'refunded']:
#             return [field.name for field in self.model._meta.fields]
#         return self.readonly_fields
    
#     def has_add_permission(self, request):
#         # Disable adding orders from admin
#         return False
    
#     def has_delete_permission(self, request, obj=None):
#         # Allow deletion only for superusers
#         return request.user.is_superuser


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variation', 'quantity', 'price', 'get_total', 'created_at')
    list_filter = ('order__status', 'created_at')
    search_fields = ('order__order_number', 'product__name')
    readonly_fields = ('order', 'product', 'variation', 'quantity', 'price', 'created_at', 'updated_at')
    list_select_related = ('order', 'product', 'variation')
    list_per_page = 20
    
    def get_total(self, obj):
        return f"${obj.get_total()}" if obj.get_total() else "-"
    get_total.short_description = 'Total'
    
    def has_add_permission(self, request):
        return False


class OrderTrackingTableNewAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'note_preview', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'note')
    readonly_fields = ('order', 'status', 'note', 'created_at')
    list_select_related = ('order',)
    list_per_page = 20
    
    def note_preview(self, obj):
        if obj.note:
            return obj.note[:50] + ('...' if len(obj.note) > 50 else '')
        return '-'
    note_preview.short_description = 'Note'
    
    def has_add_permission(self, request):
        # Only allow adding via inline in Order admin
        return False
    
    def has_change_permission(self, request, obj=None):
        # Disable editing of tracking records
        return False


# Register all models
admin.site.register(Country, CountryAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Thana, ThanaAdmin)
admin.site.register(TaxConfiguration, TaxConfigurationAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
# admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(OrderTrackingTableNew, OrderTrackingTableNewAdmin)

# Custom admin site title
admin.site.site_header = "E-commerce Admin"
admin.site.site_title = "E-commerce Admin Portal"
admin.site.index_title = "Welcome to E-commerce Admin"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product_with_variation', 'quantity', 'price', 'get_total']
    readonly_fields = ['product_with_variation', 'quantity', 'price', 'get_total']
    can_delete = False
    
    def product_with_variation(self, obj):
        if obj.product:
            # Get the admin change URL for the product
            from django.urls import reverse
            product_admin_url = reverse('admin:products_product_change', args=[obj.product.id])
            
            # Get the main product image
            main_image = obj.product.get_main_image()
            
            # Product name
            product_name = obj.product.name
            if len(product_name) > 35:
                product_name = product_name[:32] + "..."
            
            # Image HTML with link
            if main_image and main_image.image:
                image_html = format_html(
                    '<a href="{}" target="_blank" style="text-decoration: none;">'
                    '<img src="{}" width="60" height="60" style="object-fit: cover; border-radius: 8px; border: 1px solid #e9ecef; cursor: pointer; transition: opacity 0.2s;" '
                    'onmouseover="this.style.opacity=\'0.8\'" onmouseout="this.style.opacity=\'1\'" />'
                    '</a>',
                    product_admin_url,
                    main_image.thumbnail.url
                )
            else:
                image_html = format_html(
                    '<a href="{}" target="_blank" style="text-decoration: none;">'
                    '<div style="width:60px;height:60px;background:#f1f3f5;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#868e96;font-size:10px;cursor:pointer;">📷</div>'
                    '</a>',
                    product_admin_url
                )
            
            # Variation details
            variation_html = ""
            if obj.variation:
                attributes = obj.variation.attributes.all()
                if attributes:
                    attr_list = [f"{attr.attribute.name}: {attr.value}" for attr in attributes]
                    variation_html = format_html(
                        '<div style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed #e9ecef;">'
                        '<div style="font-size: 11px; color: #495057; display: flex; flex-wrap: wrap; gap: 8px;">'
                        '{}'
                        '</div>'
                        '</div>',
                        ' • '.join(attr_list)
                    )
            
            # Return complete info with clickable product name
            return format_html(
                '<div style="display: flex; gap: 12px; padding: 8px 0;">'
                '<div style="flex-shrink: 0;">{}</div>'
                '<div style="flex-grow: 1;">'
                '<div style="display: flex; justify-content: space-between; align-items: start;">'
                '<div><a href="{}" target="_blank" style="text-decoration: none; color: inherit;" '
                'onmouseover="this.style.textDecoration=\'underline\'" onmouseout="this.style.textDecoration=\'none\'">'
                '<strong>{}</strong></a> <span style="color: #6c757d; font-size: 11px;">(#{})</span></div>'
                '<div style="font-size: 11px; background: #e9ecef; padding: 2px 8px; border-radius: 12px; color: #495057;">{}</div>'
                '</div>'
                '<div style="font-size: 11px; color: #6c757d; margin-top: 4px;">SKU: {}</div>'
                '{}</div>'
                '</div>',
                image_html,
                product_admin_url,
                product_name,
                obj.product.id,
                obj.variation.sku if obj.variation else 'Base Product',
                obj.product.sku,
                variation_html
            )
        return format_html(
            '<div style="color: #dc3545; padding: 8px;">Product deleted</div>'
        )
    product_with_variation.short_description = 'Product Details'
    
    def get_total(self, obj):
        total = obj.get_total()
        if total:
            return format_html(
                '<span style="font-weight: 600; color: #28a745; background: #f0f9f0; padding: 4px 10px; border-radius: 20px; display: inline-block;">${}</span>',
                total
            )
        return format_html(
            '<span style="color: #6c757d;">-</span>'
        )
    get_total.short_description = 'Total' 

# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ['order_number', 'get_full_name', 'grand_total', 'status', 'created_at', 'download_invoice_button']
#     list_filter = ['status', 'created_at', 'country', 'payment_method']
#     search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone_number']
#     readonly_fields = ['order_number', 'created_at', 'updated_at', 'status_updated_at']
#     inlines = [OrderItemInline]
#     actions = ['download_invoice_action', 'mark_as_delivered', 'mark_as_shipped']
    
#     fieldsets = (
#         ('Order Information', {
#             'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
#         }),
#         ('Customer Information', {
#             'fields': ('first_name', 'last_name', 'email', 'phone_number', 
#                       'birth_date', 'birth_month')
#         }),
#         ('Shipping Address', {
#             'fields': ('full_address', 'country', 'district', 'thana', 'postal_code')
#         }),
#         ('Order Details', {
#             'fields': ('order_note', 'order_total', 'tax_rate', 'tax_amount', 
#                       'shipping_cost', 'grand_total')
#         }),
#         ('Payment Information', {
#             'fields': ('payment_method', 'payment_details')
#         }),
#         ('Tracking Information', {
#             'fields': ('status_updated_at', 'estimated_delivery_date', 'carrier')
#         }),
#         ('Status Timestamps', {
#             'fields': ('pending_at', 'processing_at', 'confirmed_at', 'packed_at',
#                       'shipped_at', 'out_for_delivery_at', 'delivered_at',
#                       'cancelled_at', 'refunded_at'),
#             'classes': ('collapse',)
#         }),
#     )
    
#     def download_invoice_button(self, obj):
#         try:
#             return format_html(
#                 '<a class="button" href="{}" target="_blank">Download Invoice</a>',
#                 reverse('admin_download_invoice', args=[obj.order_number])
#             )
#         except:
#             return None
#     download_invoice_button.short_description = 'Invoice'
#     download_invoice_button.allow_tags = True
    
#     def download_invoice_action(self, request, queryset):
#         if len(queryset) == 1:
#             order = queryset.first()
#             return generate_pdf_invoice(order)
#         else:
#             self.message_user(request, "Please select only one order to download invoice.")
#     download_invoice_action.short_description = "Download invoice for selected order"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'get_full_name', 'grand_total', 'status', 'created_at', 'download_invoice_button']
    list_filter = ['status', 'created_at', 'country', 'payment_method']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone_number']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'status_updated_at', 'order_items_summary']
    inlines = [OrderItemInline]
    actions = ['download_invoice_action', 'mark_as_delivered', 'mark_as_shipped']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Customer Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 
                      'birth_date', 'birth_month')
        }),
        ('Shipping Address', {
            'fields': ('full_address', 'country', 'district', 'thana', 'postal_code')
        }),
        ('Order Details', {
            'fields': ('order_note', 'order_items_summary', 'order_total', 'tax_rate', 'tax_amount', 
                      'shipping_cost', 'grand_total')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_details')
        }),
        ('Tracking Information', {
            'fields': ('status_updated_at', 'estimated_delivery_date', 'carrier')
        }),
        ('Status Timestamps', {
            'fields': ('pending_at', 'processing_at', 'confirmed_at', 'packed_at',
                      'shipped_at', 'out_for_delivery_at', 'delivered_at',
                      'cancelled_at', 'refunded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def order_items_summary(self, obj):
        items = obj.items.all()
        if not items:
            return "No items in this order"
        
        total_items = sum(item.quantity for item in items)
        unique_products = items.values('product').distinct().count()
        
        return format_html(
            '<div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">'
            '<strong>Summary:</strong> {} items from {} unique products<br>'
            '<small>See table below for details</small>'
            '</div>',
            total_items,
            unique_products
        )
    order_items_summary.short_description = 'Order Items Summary'
    
    def download_invoice_button(self, obj):
        try:
            return format_html(
                '<a class="button" href="{}" target="_blank" style="background: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;">Download Invoice</a>',
                reverse('admin_download_invoice', args=[obj.order_number])
            )
        except:
            return None
    download_invoice_button.short_description = 'Invoice'
    
    def download_invoice_action(self, request, queryset):
        if len(queryset) == 1:
            order = queryset.first()
            return generate_pdf_invoice(order)
        else:
            self.message_user(request, "Please select only one order to download invoice.")
    download_invoice_action.short_description = "Download invoice for selected order"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        for order in queryset:
            OrderTrackingTableNew.objects.create(
                order=order, 
                status='delivered', 
                note='Status changed by admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        for order in queryset:
            OrderTrackingTableNew.objects.create(
                order=order, 
                status='shipped', 
                note='Status changed by admin'
            )
        self.message_user(request, f"{queryset.count()} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as Shipped"