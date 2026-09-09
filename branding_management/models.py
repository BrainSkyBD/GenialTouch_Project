# branding_management/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.cache import cache
import json
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class BrandInfo(models.Model):
    """
    Main model for managing brand information, theme settings, and SEO data
    """
    
    # Brand Basic Information
    brand_name = models.CharField(max_length=200, default='GenialTouch', verbose_name=_('Brand Name'))
    brand_tagline = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('Brand Tagline'))
    brand_description = models.TextField(verbose_name=_('Brand Description'), 
                                         help_text=_('Detailed description of your brand'))
    
    # Brand Logo and Images
    brand_logo = models.ImageField(upload_to='brand/logos/', verbose_name=_('Brand Logo'),
                                   help_text=_('Main brand logo (recommended: 200x60px)'))
    brand_logo_light = models.ImageField(upload_to='brand/logos/', blank=True, null=True,
                                         verbose_name=_('Light Logo'),
                                         help_text=_('Logo for dark backgrounds (recommended: 200x60px)'))
    brand_favicon = models.ImageField(upload_to='brand/favicons/', verbose_name=_('Favicon'),
                                      help_text=_('Website favicon (recommended: 32x32px)'))
    brand_social_share_image = models.ImageField(upload_to='brand/social/', blank=True, null=True,
                                                 verbose_name=_('Social Share Image'),
                                                 help_text=_('Default image for social sharing (1200x630px)'))
    
    # Contact Information
    brand_email = models.EmailField(verbose_name=_('Email Address'))
    brand_phone = models.CharField(max_length=50, verbose_name=_('Phone Number'))
    brand_phone_secondary = models.CharField(max_length=50, blank=True, null=True, 
                                            verbose_name=_('Secondary Phone'))
    brand_whatsapp = models.CharField(max_length=50, blank=True, null=True,
                                     verbose_name=_('WhatsApp Number'))
    brand_address = models.TextField(verbose_name=_('Address'))
    brand_map_embed = models.TextField(blank=True, null=True, verbose_name=_('Google Maps Embed Code'),
                                       help_text=_('Paste Google Maps embed iframe code'))
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True, verbose_name=_('Facebook'))
    instagram_url = models.URLField(blank=True, null=True, verbose_name=_('Instagram'))
    youtube_url = models.URLField(blank=True, null=True, verbose_name=_('YouTube'))
    twitter_url = models.URLField(blank=True, null=True, verbose_name=_('Twitter/X'))
    linkedin_url = models.URLField(blank=True, null=True, verbose_name=_('LinkedIn'))
    pinterest_url = models.URLField(blank=True, null=True, verbose_name=_('Pinterest'))
    tiktok_url = models.URLField(blank=True, null=True, verbose_name=_('TikTok'))
    
    # Theme Settings
    THEME_CHOICES = [
        ('theme-01-default', 'Theme 01 - Default'),
        ('theme-02-Modern', 'Theme 02 - Modern'),
    ]
    active_theme = models.CharField(max_length=20, choices=THEME_CHOICES, 
                                   default='theme-01-default', verbose_name=_('Active Theme'))
    
    primary_color = models.CharField(max_length=20, default='#2b2b2b', 
                                    verbose_name=_('Primary Color'),
                                    help_text=_('Main brand color (hex code)'))
    secondary_color = models.CharField(max_length=20, default='#e74c3c',
                                      verbose_name=_('Secondary Color'),
                                      help_text=_('Secondary brand color (hex code)'))
    accent_color = models.CharField(max_length=20, default='#f39c12',
                                   verbose_name=_('Accent Color'),
                                   help_text=_('Accent color for highlights (hex code)'))
    
    navbar_color = models.CharField(max_length=20, default='#ffffff',
                                    verbose_name=_('Navbar Color'),
                                    help_text=_('Background color for navbar'))
    navbar_text_color = models.CharField(max_length=20, default='#2b2b2b',
                                        verbose_name=_('Navbar Text Color'))
    footer_color = models.CharField(max_length=20, default='#2b2b2b',
                                   verbose_name=_('Footer Color'),
                                   help_text=_('Background color for footer'))
    footer_text_color = models.CharField(max_length=20, default='#ffffff',
                                        verbose_name=_('Footer Text Color'))
    
    # Logo Settings
    logo_size = models.CharField(max_length=20, default='160px',
                                 verbose_name=_('Logo Size'),
                                 help_text=_('e.g., 160px, 200px, 100%'))
    logo_width = models.CharField(max_length=20, blank=True, null=True,
                                  verbose_name=_('Logo Width'),
                                  help_text=_('Specific width for logo'))
    logo_height = models.CharField(max_length=20, blank=True, null=True,
                                   verbose_name=_('Logo Height'))
    
    # SEO and Meta Data
    default_meta_title = models.CharField(max_length=200, default='GenialTouch',
                                         verbose_name=_('Default Meta Title'))
    default_meta_description = models.TextField(default='Your trusted online store',
                                               verbose_name=_('Default Meta Description'))
    default_meta_keywords = models.CharField(max_length=500, 
                                            default='GenialTouch, online store, e-commerce',
                                            verbose_name=_('Default Meta Keywords'))
    meta_author = models.CharField(max_length=100, default='GenialTouch',
                                  verbose_name=_('Meta Author'))
    
    # Copyright and Legal
    copyright_text = models.CharField(max_length=200, default='© 2024 GenialTouch. All rights reserved.',
                                     verbose_name=_('Copyright Text'))
    privacy_policy_url = models.URLField(blank=True, null=True, verbose_name=_('Privacy Policy URL'))
    terms_conditions_url = models.URLField(blank=True, null=True, verbose_name=_('Terms & Conditions URL'))
    return_policy_url = models.URLField(blank=True, null=True, verbose_name=_('Return Policy URL'))
    shipping_policy_url = models.URLField(blank=True, null=True, verbose_name=_('Shipping Policy URL'))
    refund_policy_url = models.URLField(blank=True, null=True, verbose_name=_('Refund Policy URL'))
    cookie_policy_url = models.URLField(blank=True, null=True, verbose_name=_('Cookie Policy URL'))
    
    # Business Information
    business_registration_number = models.CharField(max_length=100, blank=True, null=True,
                                                   verbose_name=_('Business Registration Number'))
    tax_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Tax ID/VAT Number'))
    year_established = models.IntegerField(blank=True, null=True, verbose_name=_('Year Established'))
    business_type = models.CharField(max_length=100, blank=True, null=True,
                                     verbose_name=_('Business Type'))
    
    # Additional Brand Settings
    show_brand_section = models.BooleanField(default=True, verbose_name=_('Show Brand Section'))
    show_trust_badges = models.BooleanField(default=True, verbose_name=_('Show Trust Badges'))
    show_social_icons = models.BooleanField(default=True, verbose_name=_('Show Social Icons'))
    show_newsletter = models.BooleanField(default=True, verbose_name=_('Show Newsletter Section'))
    
    # Custom CSS/JS
    custom_css = models.TextField(blank=True, null=True, verbose_name=_('Custom CSS'),
                                  help_text=_('Add custom CSS for additional styling'))
    custom_js = models.TextField(blank=True, null=True, verbose_name=_('Custom JavaScript'),
                                 help_text=_('Add custom JavaScript for additional functionality'))
    
    # Advanced Settings
    enable_cache = models.BooleanField(default=True, verbose_name=_('Enable Cache'))
    cache_duration = models.IntegerField(default=3600, verbose_name=_('Cache Duration (seconds)'),
                                         help_text=_('How long to cache the brand info'))
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Updated By'))
                                
    track_order_url = models.URLField(blank=True, null=True, verbose_name=_('Track Order URL'))
    help_center_url = models.URLField(blank=True, null=True, verbose_name=_('Help Center URL'))
    language = models.CharField(max_length=50, default='English', verbose_name=_('Default Language'))
    currency = models.CharField(max_length=10, default='BDT', verbose_name=_('Default Currency'))
    
    class Meta:
        verbose_name = _('Brand Information')
        verbose_name_plural = _('Brand Information')
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.brand_name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Clear cache on save
        if self.enable_cache:
            cache.delete('brand_info_data')
    
    @classmethod
    def get_brand_info(cls):
        """
        Get brand info with caching
        """
        cache_key = 'brand_info_data'
        brand_info = cache.get(cache_key)
        
        if brand_info is None:
            try:
                brand_info = cls.objects.first()
                if brand_info and brand_info.enable_cache:
                    cache.set(cache_key, brand_info, brand_info.cache_duration)
            except:
                brand_info = None
        
        return brand_info
    
    def get_social_links(self):
        """Return a list of active social media links"""
        social_links = []
        social_media = [
            ('Facebook', self.facebook_url, 'fa-facebook'),
            ('Instagram', self.instagram_url, 'fa-instagram'),
            ('YouTube', self.youtube_url, 'fa-youtube'),
            ('Twitter', self.twitter_url, 'fa-twitter'),
            ('LinkedIn', self.linkedin_url, 'fa-linkedin'),
            ('Pinterest', self.pinterest_url, 'fa-pinterest'),
            ('TikTok', self.tiktok_url, 'fa-tiktok'),
        ]
        
        for name, url, icon in social_media:
            if url:
                social_links.append({'name': name, 'url': url, 'icon': icon})
        
        return social_links
    
    def get_contact_info(self):
        """Return organized contact information"""
        return {
            'email': self.brand_email,
            'phone': self.brand_phone,
            'phone_secondary': self.brand_phone_secondary,
            'whatsapp': self.brand_whatsapp,
            'address': self.brand_address,
            'map_embed': self.brand_map_embed
        }
    
    def get_policy_urls(self):
        """Return all policy URLs"""
        return {
            'privacy': self.privacy_policy_url,
            'terms': self.terms_conditions_url,
            'return': self.return_policy_url,
            'shipping': self.shipping_policy_url,
            'refund': self.refund_policy_url,
            'cookie': self.cookie_policy_url
        }


class TrustBadge(models.Model):
    """
    Model for managing trust badges/features displayed on the website
    """
    brand = models.ForeignKey(BrandInfo, on_delete=models.CASCADE, related_name='trust_badges')
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    icon_class = models.CharField(max_length=50, default='fa-check-circle', 
                                 verbose_name=_('Icon Class'),
                                 help_text=_('FontAwesome icon class e.g., fa-check-circle'))
    image = models.ImageField(upload_to='brand/trust_badges/', blank=True, null=True,
                             verbose_name=_('Icon Image'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Trust Badge')
        verbose_name_plural = _('Trust Badges')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.brand.brand_name} - {self.title}"


class SocialShareSetting(models.Model):
    """
    Model for managing social media sharing settings (for SEO and social media)
    """
    brand = models.OneToOneField(BrandInfo, on_delete=models.CASCADE, related_name='social_share')
    
    # Open Graph (Facebook, WhatsApp, LinkedIn)
    og_title = models.CharField(max_length=200, blank=True, null=True,
                               verbose_name=_('OG Title'))
    og_description = models.TextField(blank=True, null=True,
                                     verbose_name=_('OG Description'))
    og_image = models.ImageField(upload_to='brand/og/', blank=True, null=True,
                                verbose_name=_('OG Image (1200x630)'))
    og_type = models.CharField(max_length=50, default='website',
                              verbose_name=_('OG Type'))
    og_locale = models.CharField(max_length=10, default='en_US',
                                verbose_name=_('OG Locale'))
    
    # Twitter Card
    twitter_card = models.CharField(max_length=50, default='summary_large_image',
                                   verbose_name=_('Twitter Card Type'))
    twitter_site = models.CharField(max_length=100, blank=True, null=True,
                                   verbose_name=_('Twitter Site @username'))
    twitter_creator = models.CharField(max_length=100, blank=True, null=True,
                                      verbose_name=_('Twitter Creator @username'))
    
    # Additional Meta Tags
    meta_robots = models.CharField(max_length=200, default='index, follow',
                                  verbose_name=_('Meta Robots'))
    meta_revisit_after = models.CharField(max_length=50, default='7 days',
                                         verbose_name=_('Meta Revisit After'))
    meta_rating = models.CharField(max_length=50, default='General',
                                  verbose_name=_('Meta Rating'))
    
    class Meta:
        verbose_name = _('Social Share Setting')
        verbose_name_plural = _('Social Share Settings')
    
    def __str__(self):
        return f"Social Settings - {self.brand.brand_name}"
    
    def get_og_tags(self, request=None, product=None, page_title=None, page_description=None, page_image=None):
        """
        Generate OG meta tags dynamically
        """
        context = {
            'title': page_title or self.og_title or self.brand.default_meta_title,
            'description': page_description or self.og_description or self.brand.default_meta_description,
            'image': page_image or (self.og_image.url if self.og_image else None),
            'url': request.build_absolute_uri() if request else '',
        }
        
        if product:
            context.update({
                'title': f"{product.name} - {self.brand.brand_name}",
                'description': product.description[:160] if product.description else context['description'],
                'image': product.images.first().image.url if product.images.exists() else context['image'],
                'price': product.discount_price or product.price,
                'currency': 'BDT',
                'availability': 'instock' if product.is_in_stock else 'outofstock',
                'brand': product.brand.name if product.brand else self.brand.brand_name,
            })
        
        return context
    
    def get_twitter_tags(self, request=None, product=None):
        """
        Generate Twitter card meta tags dynamically
        """
        context = {
            'card': self.twitter_card,
            'site': self.twitter_site,
            'creator': self.twitter_creator,
        }
        
        if product:
            context.update({
                'title': f"{product.name} - {self.brand.brand_name}",
                'description': product.description[:160] if product.description else self.brand.default_meta_description,
                'image': product.images.first().image.url if product.images.exists() else None,
            })
        
        return context


