# core/utils.py (or core/helpers.py)
from branding_management.models import BrandInfo

def get_active_theme_folder():
    """Get the active theme folder name with fallback to default"""
    brand_info = BrandInfo.get_brand_info()
    return brand_info.active_theme if brand_info else 'theme-01-default'


def get_theme_template(template_name):
    """Build full template path with active theme folder"""
    return f'{get_active_theme_folder()}/{template_name}'