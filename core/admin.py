# admin.py
from django.contrib import admin
from .models import Banner, Promotion, HomeAd
from .models import CurrencySettingsTable


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    ordering = ('order',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    ordering = ('order',)

@admin.register(HomeAd)
class HomeAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'url')
    ordering = ('order',)






@admin.register(CurrencySettingsTable)
class CurrencySettingsTableAdmin(admin.ModelAdmin):
    list_display = ['currency_code', 'currency_symbol', 'is_active', 'updated_at']
    list_editable = ['is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['currency_code', 'currency_symbol']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Currency Information', {
            'fields': ('currency_code', 'currency_symbol')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of active currency
        if obj and obj.is_active:
            return False
        return super().has_delete_permission(request, obj)