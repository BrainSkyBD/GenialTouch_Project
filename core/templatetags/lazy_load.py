from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag
def lazy_image(image_url, alt_text, class_name='', width='', height=''):
    """
    Generate lazy-loaded image tag
    """
    placeholder = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    
    attributes = []
    if class_name:
        attributes.append(f'class="{class_name}"')
    if width:
        attributes.append(f'width="{width}"')
    if height:
        attributes.append(f'height="{height}"')
    
    attrs_str = ' '.join(attributes)
    
    return format_html(
        '<img src="{}" data-src="{}" alt="{}" loading="lazy" {}>',
        placeholder, image_url, alt_text, attrs_str
    )


@register.simple_tag
def lazy_background(image_url, class_name=''):
    """
    Generate lazy-loaded background image
    """
    return format_html(
        '<div class="{} lazy-background" data-bg="{}" style="background-color: #f5f5f5;"></div>',
        class_name, image_url
    )