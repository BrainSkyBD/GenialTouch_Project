# branding_management/context_processors.py
from .models import BrandInfo
from django.templatetags.static import static
from django.conf import settings
import os

def brand_info_context(request):
    """
    Context processor to make brand info available globally
    """
    try:
        brand_info = BrandInfo.get_brand_info()
    except:
        brand_info = None
    
    context = {
        'brand_info': brand_info,
    }
    
    if brand_info:
        # Get the active theme folder name
        theme_folder = brand_info.active_theme
        context['theme_folder'] = theme_folder
        
        # Brand Basic Information
        context.update({
            'brand_name': brand_info.brand_name,
            'brand_tagline': brand_info.brand_tagline or 'Your Trusted Shopping Partner',
            'brand_description': brand_info.brand_description,
            'brand_logo': brand_info.brand_logo,
            'brand_logo_light': brand_info.brand_logo_light,
            'brand_favicon': brand_info.brand_favicon,
            'brand_social_share_image': brand_info.brand_social_share_image,
            
            # Contact Information
            'brand_email': brand_info.brand_email,
            'brand_phone': brand_info.brand_phone,
            'brand_phone_secondary': brand_info.brand_phone_secondary,
            'brand_whatsapp': brand_info.brand_whatsapp,
            'brand_address': brand_info.brand_address,
            'brand_map_embed': brand_info.brand_map_embed,
            
            # Social Media URLs
            'facebook_url': brand_info.facebook_url,
            'instagram_url': brand_info.instagram_url,
            'youtube_url': brand_info.youtube_url,
            'twitter_url': brand_info.twitter_url,
            'linkedin_url': brand_info.linkedin_url,
            'pinterest_url': brand_info.pinterest_url,
            'tiktok_url': brand_info.tiktok_url,
            
            # Theme Settings
            'active_theme': brand_info.active_theme,
            'primary_color': brand_info.primary_color,
            'secondary_color': brand_info.secondary_color,
            'accent_color': brand_info.accent_color,
            'navbar_color': brand_info.navbar_color,
            'navbar_text_color': brand_info.navbar_text_color,
            'footer_color': brand_info.footer_color,
            'footer_text_color': brand_info.footer_text_color,
            
            # Logo Settings
            'logo_size': brand_info.logo_size,
            'logo_width': brand_info.logo_width or '74%',
            'logo_height': brand_info.logo_height,
            
            # SEO and Meta Data
            'default_meta_title': brand_info.default_meta_title,
            'default_meta_description': brand_info.default_meta_description,
            'default_meta_keywords': brand_info.default_meta_keywords,
            'meta_author': brand_info.meta_author,
            
            # Copyright and Legal
            'copyright_text': brand_info.copyright_text,
            'privacy_policy_url': brand_info.privacy_policy_url,
            'terms_conditions_url': brand_info.terms_conditions_url,
            'return_policy_url': brand_info.return_policy_url,
            'shipping_policy_url': brand_info.shipping_policy_url,
            'refund_policy_url': brand_info.refund_policy_url,
            'cookie_policy_url': brand_info.cookie_policy_url,
            
            # Business Information
            'business_registration_number': brand_info.business_registration_number,
            'tax_id': brand_info.tax_id,
            'year_established': brand_info.year_established,
            'business_type': brand_info.business_type,
            
            # Additional Settings
            'show_brand_section': brand_info.show_brand_section,
            'show_trust_badges': brand_info.show_trust_badges,
            'show_social_icons': brand_info.show_social_icons,
            'show_newsletter': brand_info.show_newsletter,
            
            # Custom CSS/JS
            'custom_css': brand_info.custom_css,
            'custom_js': brand_info.custom_js,
            
            # Advanced Settings
            'enable_cache': brand_info.enable_cache,
            'cache_duration': brand_info.cache_duration,
            
            # Additional URLs
            'track_order_url': brand_info.track_order_url,
            'help_center_url': brand_info.help_center_url,
            'language': brand_info.language,
            'currency': brand_info.currency,
            
            # Get social links
            'social_links': brand_info.get_social_links(),
            'contact_info': brand_info.get_contact_info(),
            'policy_urls': brand_info.get_policy_urls(),
            'trust_badges': brand_info.trust_badges.filter(is_active=True).order_by('order') if brand_info.show_trust_badges else [],
        })
    else:
        # DEFAULT THEME DATA (theme-01-default)
        context.update({
            'theme_folder': 'theme-01-default',
            'brand_name': 'SHINRAI',
            'brand_tagline': 'Your Trusted Shopping Partner',
            'brand_description': 'Bringing authentic, halal-certified Japanese products to your doorstep with trust and care.',
            'primary_color': '#0f2a5c',
            'secondary_color': '#e8536a',
            'accent_color': '#f5b400',
            'navbar_color': '#ffffff',
            'navbar_text_color': '#16213e',
            'footer_color': '#0a1d40',
            'footer_text_color': '#c6d0ea',
            'logo_size': '160px',
            'logo_width': '74%',
            'active_theme': 'theme-01-default',
            'copyright_text': '© 2026 GenialTouch. All rights reserved.',
            'default_meta_title': 'GenialTouch - Your Trusted Shopping Partner',
            'default_meta_description': 'Shop authentic, halal-certified products at GenialTouch. Quality products, fast delivery, and trusted service.',
            'default_meta_keywords': 'GenialTouch, online shopping, halal products, e-commerce',
            'meta_author': 'GenialTouch',
            'language': 'English',
            'currency': 'BDT',
            'social_links': [],
            'trust_badges': [],
            'contact_info': {},
            'policy_urls': {},
            'brand_logo': None,
            'brand_favicon': None,
        })
    
    return context