# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import BrandInfo, TrustBadge, SocialShareSetting

@admin.register(BrandInfo)
class BrandInfoAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'brand_phone', 'brand_email', 'active_theme', 'updated_at']
    list_filter = ['active_theme', 'show_brand_section']
    search_fields = ['brand_name', 'brand_description', 'brand_email']
    
    fieldsets = (
        ('Brand Information', {
            'fields': ('brand_name', 'brand_tagline', 'brand_description')
        }),
        ('Brand Logo & Images', {
            'fields': ('brand_logo', 'brand_logo_light', 'brand_favicon', 'brand_social_share_image'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('brand_email', 'brand_phone', 'brand_phone_secondary', 
                      'brand_whatsapp', 'brand_address', 'brand_map_embed')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'twitter_url',
                      'linkedin_url', 'pinterest_url', 'tiktok_url'),
            'classes': ('collapse',)
        }),
        ('Theme & Colors', {
            'fields': ('active_theme', 'primary_color', 'secondary_color', 'accent_color',
                      'navbar_color', 'navbar_text_color', 'footer_color', 'footer_text_color',
                      'logo_size', 'logo_width', 'logo_height')
        }),
        ('SEO & Meta Data', {
            'fields': ('default_meta_title', 'default_meta_description', 'default_meta_keywords',
                      'meta_author'),
            'classes': ('collapse',)
        }),
        ('Copyright & Legal', {
            'fields': ('copyright_text', 'privacy_policy_url', 'terms_conditions_url',
                      'return_policy_url', 'shipping_policy_url', 'refund_policy_url',
                      'cookie_policy_url'),
            'classes': ('collapse',)
        }),
        ('Business Information', {
            'fields': ('business_registration_number', 'tax_id', 'year_established', 
                      'business_type'),
            'classes': ('collapse',)
        }),
        ('Brand Settings', {
            'fields': ('show_brand_section', 'show_trust_badges', 'show_social_icons',
                      'show_newsletter')
        }),
        ('Custom Code', {
            'fields': ('custom_css', 'custom_js'),
            'classes': ('collapse',)
        }),
        ('Advanced Settings', {
            'fields': ('enable_cache', 'cache_duration')
        }),
        ('Tracking', {
            'fields': ('updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request):
        # Restrict to only one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'is_active', 'order']
    list_filter = ['is_active', 'brand']
    search_fields = ['title', 'description']
    ordering = ['order']

@admin.register(SocialShareSetting)
class SocialShareSettingAdmin(admin.ModelAdmin):
    list_display = ['brand', 'og_type', 'twitter_card']
    search_fields = ['brand__brand_name']
    
    fieldsets = (
        ('Open Graph Settings', {
            'fields': ('og_title', 'og_description', 'og_image', 'og_type', 'og_locale')
        }),
        ('Twitter Card Settings', {
            'fields': ('twitter_card', 'twitter_site', 'twitter_creator')
        }),
        ('Additional Meta Tags', {
            'fields': ('meta_robots', 'meta_revisit_after', 'meta_rating')
        })
    )


