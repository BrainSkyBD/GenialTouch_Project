# admin.py
from django.contrib import admin
from .models import Banner, Promotion, HomeAd
from .models import CurrencySettingsTable

from django.contrib import admin
from .models import SiteFeature


from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import BrandProfile, BrandFooter

@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = [
        'brand_name', 
        'is_active', 
        'website_author',
        'logo_preview',
        'created_at',
        'updated_at'
    ]
    
    list_filter = ['is_active', 'created_at', 'established_year']
    search_fields = ['brand_name', 'website_author', 'contact_email', 'brand_tagline']
    readonly_fields = ['created_at', 'updated_at', 'logo_preview', 'favicon_preview']
    
    fieldsets = (
        # ===== BASIC INFO =====
        ('🏷️ Basic Brand Information', {
            'fields': (
                ('brand_name', 'brand_tagline'),
                'brand_description',
                'brand_story',
            ),
        }),
        
        # ===== LOGO SECTION =====
        ('🖼️ Logo Management (With Sizes)', {
            'fields': (
                ('logo_primary', 'logo_primary_width', 'logo_primary_height'),
                ('logo_alternative',),
                ('logo_horizontal', 'logo_horizontal_width', 'logo_horizontal_height'),
                ('logo_small', 'logo_small_width', 'logo_small_height'),
                'logo_alt_text',
                'logo_preview',
            ),
            'description': 'Upload different logo variations with their dimensions. Recommended sizes are shown.',
        }),
        
        # ===== FAVICONS =====
        ('🔖 Favicons', {
            'fields': (
                ('favicon_16x16', 'favicon_32x32', 'favicon_48x48'),
                'favicon_apple',
                'favicon_preview',
            ),
            'description': 'Upload favicon in different sizes for various devices',
        }),
        
        # ===== AUTHOR INFO =====
        ('👤 Author/Owner Information', {
            'fields': (
                'website_author',
                'author_designation',
                ('author_image', 'author_image_width', 'author_image_height'),
                'author_bio',
                'author_email',
                'author_social_links',
            ),
        }),
        
        # ===== CONTACT INFO =====
        ('📞 Contact Information', {
            'fields': (
                ('contact_email', 'contact_phone', 'contact_phone_country'),
                'address',
                ('address_latitude', 'address_longitude'),
            ),
        }),
        
        # ===== SEO SECTION =====
        ('🔍 SEO Settings', {
            'fields': (
                ('meta_title', 'meta_description'),
                'meta_keywords',
                ('canonical_url', 'sitemap_url'),
                'robots_txt',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== SOCIAL MEDIA =====
        ('🌐 Social Media', {
            'fields': (
                'social_links',
                'social_media_handles',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== OPEN GRAPH =====
        ('📱 Open Graph (Social Sharing)', {
            'fields': (
                ('og_title', 'og_description'),
                ('og_image', 'og_image_width', 'og_image_height'),
                ('og_type', 'og_site_name'),
            ),
            'classes': ('collapse',),
        }),
        
        # ===== TWITTER CARDS =====
        ('🐦 Twitter Cards', {
            'fields': (
                ('twitter_card_type',),
                ('twitter_site', 'twitter_creator'),
                ('twitter_image', 'twitter_image_width', 'twitter_image_height'),
            ),
            'classes': ('collapse',),
        }),
        
        # ===== BRAND COLORS =====
        ('🎨 Brand Colors', {
            'fields': (
                'brand_colors',
                ('primary_color', 'secondary_color', 'accent_color'),
                ('text_color', 'background_color'),
                'color_preview',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== TYPOGRAPHY =====
        ('✍️ Typography', {
            'fields': (
                ('primary_font', 'secondary_font'),
                'heading_font',
                'google_fonts_url',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== BRAND GUIDELINES =====
        ('📋 Brand Guidelines', {
            'fields': (
                'brand_guidelines',
                'brand_voice',
                'brand_personality',
                'target_audience',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== LEGAL INFO =====
        ('⚖️ Legal Information', {
            'fields': (
                ('copyright_text', 'established_year'),
                ('company_type', 'registration_number'),
                'tax_id',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== EMAIL SETTINGS =====
        ('✉️ Email Settings', {
            'fields': (
                ('email_from_name', 'email_from_email'),
                'email_reply_to',
                'email_footer_text',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== ANALYTICS =====
        ('📊 Analytics & Tracking', {
            'fields': (
                ('google_analytics_id', 'google_tag_manager_id'),
                'facebook_pixel_id',
                'custom_analytics_code',
            ),
            'classes': ('collapse',),
        }),
        
        # ===== SYSTEM =====
        ('⚙️ System Settings', {
            'fields': (
                'is_active',
                ('created_at', 'updated_at'),
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )
    
    def logo_preview(self, obj):
        if obj.logo_primary:
            return format_html(
                '<div style="display: flex; align-items: center; gap: 10px;">'
                '<img src="{}" style="max-height: 50px; max-width: 100px; border-radius: 4px; border: 1px solid #ddd;" />'
                '<span style="font-size: 12px; color: #666;">{}x{}px</span>'
                '</div>',
                obj.logo_primary.url,
                obj.logo_primary_width,
                obj.logo_primary_height
            )
        return "No Logo"
    logo_preview.short_description = "Logo Preview"
    
    def favicon_preview(self, obj):
        if obj.favicon_32x32:
            return format_html(
                '<img src="{}" style="max-height: 32px; max-width: 32px; border: 1px solid #ddd; padding: 2px;" />',
                obj.favicon_32x32.url
            )
        return "No Favicon"
    favicon_preview.short_description = "Favicon Preview"
    
    def color_preview(self, obj):
        if obj.primary_color:
            return format_html(
                '<div style="display: flex; gap: 8px; flex-wrap: wrap;">'
                '<div style="background: {}; width: 40px; height: 40px; border-radius: 4px; border: 1px solid #ddd;"></div>'
                '<div style="background: {}; width: 40px; height: 40px; border-radius: 4px; border: 1px solid #ddd;"></div>'
                '<div style="background: {}; width: 40px; height: 40px; border-radius: 4px; border: 1px solid #ddd;"></div>'
                '</div>',
                obj.primary_color,
                obj.secondary_color or '#ffffff',
                obj.accent_color or '#ffffff'
            )
        return "No Colors Set"
    color_preview.short_description = "Color Preview"
    
    def save_model(self, request, obj, form, change):
        if obj.is_active:
            BrandProfile.objects.filter(is_active=True).exclude(pk=obj.pk).update(is_active=False)
        obj.updated_by = request.user.get_full_name() or request.user.username
        super().save_model(request, obj, form, change)

@admin.register(BrandFooter)
class BrandFooterAdmin(admin.ModelAdmin):
    list_display = ['brand', 'show_powered_by', 'newsletter_enabled']
    search_fields = ['brand__brand_name']
    readonly_fields = ['footer_logo_preview']
    
    def footer_logo_preview(self, obj):
        if obj.footer_logo:
            return format_html(
                '<img src="{}" style="max-height: 40px; max-width: 150px;" />',
                obj.footer_logo.url
            )
        return "No Logo"
    footer_logo_preview.short_description = "Footer Logo"
    

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




@admin.register(SiteFeature)
class SiteFeatureAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'icon', 'is_active', 'order')
        }),
        ('Special Settings', {
            'fields': ('min_order_amount', 'return_days'),
            'classes': ('wide',),
            'description': 'These fields are only applicable for specific features'
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Make special fields optional
        form.base_fields['min_order_amount'].required = False
        form.base_fields['return_days'].required = False
        return form