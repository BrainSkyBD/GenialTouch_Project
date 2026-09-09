# branding_management/templatetags/brand_extras.py
from django import template
from django.utils.html import mark_safe
from django.templatetags.static import static
from django.urls import reverse
import json

register = template.Library()

# Import the model
from ..models import BrandInfo, SocialShareSetting

@register.simple_tag
def get_brand_info():
    """Get brand info for use in templates"""
    return BrandInfo.get_brand_info()

@register.simple_tag
def get_theme_class():
    """Get active theme class for body tag"""
    brand = BrandInfo.get_brand_info()
    if brand:
        return f"theme-{brand.active_theme}"
    return "theme-default"

@register.simple_tag(takes_context=True)
def get_social_share_tags(context, product=None):
    """
    Generate complete social sharing meta tags
    """
    request = context.get('request')
    brand = BrandInfo.get_brand_info()
    if not brand:
        return ''
    
    # Get or create social share settings
    try:
        social = brand.social_share
    except SocialShareSetting.DoesNotExist:
        social = None
    
    # Build base URL
    base_url = ""
    if request:
        base_url = request.build_absolute_uri('/')[:-1]
    
    # Base OG tags
    title = brand.default_meta_title
    description = brand.default_meta_description
    
    if product:
        title = f"{product.name} - {brand.brand_name}"
        description = product.description[:160] if product.description else description
    
    # Default image
    default_image = ""
    if brand.brand_social_share_image:
        default_image = base_url + brand.brand_social_share_image.url
    else:
        default_image = base_url + static('images/default-social-share.jpg')
    
    # Product image
    product_image = default_image
    if product and hasattr(product, 'images') and product.images.exists():
        product_image = base_url + product.images.first().image.url
    
    # OG tags
    tags = f"""
    <meta property="og:type" content="website">
    <meta property="og:url" content="{request.build_absolute_uri() if request else ''}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{product_image}">
    <meta property="og:image:secure_url" content="{product_image}">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:site_name" content="{brand.brand_name}">
    """
    
    # Product specific OG tags
    if product:
        price = product.discount_price if hasattr(product, 'discount_price') and product.discount_price else (product.price if hasattr(product, 'price') else None)
        if price:
            tags += f"""
    <meta property="og:price:amount" content="{price}">
    <meta property="og:price:currency" content="BDT">
    <meta property="product:price:amount" content="{price}">
    <meta property="product:price:currency" content="BDT">
            """
        
        # Product availability
        if hasattr(product, 'is_in_stock'):
            availability = 'instock' if product.is_in_stock else 'outofstock'
            tags += f"""
    <meta property="og:availability" content="{availability}">
    <meta property="product:availability" content="{availability}">
            """
        
        # Product brand
        if hasattr(product, 'brand') and product.brand:
            tags += f"""
    <meta property="product:brand" content="{product.brand.name}">
            """
        
        tags += f"""
    <meta property="product:condition" content="new">
    <meta property="product:retailer_item_id" content="{product.id}">
    <meta property="product:item_group_id" content="{product.id}">
        """
    
    # Twitter Card tags
    twitter_site = ""
    twitter_creator = ""
    if social:
        twitter_site = social.twitter_site or ""
        twitter_creator = social.twitter_creator or ""
    
    tags += f"""
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="{twitter_site}">
    <meta name="twitter:creator" content="{twitter_creator}">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{product_image}">
    """
    
    # Additional meta tags
    tags += """
    <meta property="og:locale" content="en_US">
    <meta name="format-detection" content="telephone=no">
    """
    
    return mark_safe(tags)

@register.simple_tag
def get_custom_css():
    """Get custom CSS from brand settings"""
    brand = BrandInfo.get_brand_info()
    if brand and brand.custom_css:
        return mark_safe(f'<style>{brand.custom_css}</style>')
    return ''

@register.simple_tag
def get_custom_js():
    """Get custom JavaScript from brand settings"""
    brand = BrandInfo.get_brand_info()
    if brand and brand.custom_js:
        return mark_safe(f'<script>{brand.custom_js}</script>')
    return ''

@register.simple_tag
def get_theme_styles():
    """Generate theme-specific CSS variables"""
    brand = BrandInfo.get_brand_info()
    if not brand:
        return ''
    
    styles = f"""
    <style>
        :root {{
            --brand-primary: {brand.primary_color};
            --brand-secondary: {brand.secondary_color};
            --brand-accent: {brand.accent_color};
            --navbar-bg: {brand.navbar_color};
            --navbar-text: {brand.navbar_text_color};
            --footer-bg: {brand.footer_color};
            --footer-text: {brand.footer_text_color};
            --logo-size: {brand.logo_size};
        }}
    </style>
    """
    return mark_safe(styles)

@register.simple_tag(takes_context=True)
def get_og_image(context, product=None):
    """Get OG image URL"""
    request = context.get('request')
    brand = BrandInfo.get_brand_info()
    
    if not brand:
        return ''
    
    base_url = request.build_absolute_uri('/')[:-1] if request else ''
    
    if product and hasattr(product, 'images') and product.images.exists():
        return base_url + product.images.first().image.url
    
    if brand.brand_social_share_image:
        return base_url + brand.brand_social_share_image.url
    
    return base_url + static('images/default-social-share.jpg')

@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    """Get canonical URL"""
    request = context.get('request')
    if request:
        return request.build_absolute_uri()
    return ''