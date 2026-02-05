from django import template
from django.utils.safestring import mark_safe
from urllib.parse import urlparse
import re

register = template.Library()


@register.filter
def product_image(product, size='thumbnail'):
    """
    Get optimized product image URL
    """
    if hasattr(product, 'get_main_image'):
        image = product.get_main_image()
        if image:
            return image.image.url
    elif hasattr(product, 'images') and product.images.exists():
        image = product.images.first()
        return image.image.url
    
    return '/static/img/no-image.jpg'


@register.filter
def discount_percentage(product):
    """Calculate discount percentage"""
    if hasattr(product, 'get_discount_percentage'):
        return product.get_discount_percentage()
    
    if hasattr(product, 'discount_price') and hasattr(product, 'price'):
        if product.discount_price and product.price and product.price > 0:
            discount = ((float(product.price) - float(product.discount_price)) / float(product.price)) * 100
            return int(round(discount))
    return 0


@register.filter
def format_price(price, currency_symbol='$'):
    """Format price with currency symbol"""
    try:
        price_float = float(price)
        return f"{currency_symbol}{price_float:,.2f}"
    except (ValueError, TypeError):
        try:
            return f"{currency_symbol}{price}"
        except:
            return f"{currency_symbol}0.00"


@register.filter
def truncate_name(name, length=50):
    """Truncate product name"""
    if not name:
        return ""
    
    name = str(name)
    if len(name) > length:
        return name[:length-3] + '...'
    return name


@register.filter
def safe_url(url):
    """Ensure URL is safe"""
    if not url:
        return '#'
    
    if isinstance(url, str):
        if not url.startswith(('http://', 'https://', '/', '#')):
            return '#' + url
    return url


@register.simple_tag
def get_image_url(image_field, width=None, height=None):
    """Get optimized image URL with optional dimensions"""
    if not image_field:
        return '/static/img/no-image.jpg'
    
    try:
        url = image_field.url
        
        # If you have a CDN with image processing, add parameters here
        # Example for Cloudinary: f"{url}?w={width}&h={height}&c=fill"
        
        return url
    except:
        return '/static/img/no-image.jpg'


@register.filter
def get_first_image(product):
    """Get first image of product"""
    if hasattr(product, 'images') and product.images.exists():
        return product.images.first().image.url
    return '/static/img/no-image.jpg'


@register.filter
def multiply(value, arg):
    """Multiply the value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide the value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0


@register.filter
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def add(value, arg):
    """Add arg to value"""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value


@register.filter
def percentage_of(value, total):
    """Calculate percentage of total"""
    try:
        if total == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    for k in [k for k, v in d.items() if not v]:
        del d[k]
    return d.urlencode()