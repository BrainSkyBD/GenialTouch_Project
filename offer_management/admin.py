from django.contrib import admin
from django.utils import timezone
from .models import PromoCode, PromoCodeUsage

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'minimum_purchase_amount', 
                   'valid_from', 'valid_to', 'is_active', 'used_count', 'usage_limit', 
                   'is_valid_now']
    list_filter = ['is_active', 'discount_type', 'applies_to_all_products', 'first_order_only']
    search_fields = ['code', 'description']
    filter_horizontal = ['products', 'countries']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount Configuration', {
            'fields': ('discount_type', 'discount_value', 'minimum_purchase_amount', 
                      'maximum_discount_amount')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'per_user_limit', 'used_count')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_to')
        }),
        ('Restrictions', {
            'fields': ('applies_to_all_products', 'products', 
                      'applies_to_all_countries', 'countries',
                      'first_order_only')
        }),
    )
    
    def is_valid_now(self, obj):
        now = timezone.now()
        return obj.valid_from <= now <= obj.valid_to and obj.is_active
    is_valid_now.boolean = True
    is_valid_now.short_description = 'Currently Valid'

class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ['promo_code', 'order', 'user', 'discount_amount', 'used_at']
    list_filter = ['used_at']
    search_fields = ['promo_code__code', 'order__order_number', 'user__email']
    readonly_fields = ['used_at']

admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(PromoCodeUsage, PromoCodeUsageAdmin)