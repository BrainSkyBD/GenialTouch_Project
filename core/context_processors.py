from django.core.cache import cache
from .models import CurrencySettingsTable
from .models import BrandProfile



def currency_context(request):
    """
    Cache currency settings across the site
    """
    cache_key = 'active_currency'
    currency_data = cache.get(cache_key)
    
    if not currency_data:
        try:
            active_currency = CurrencySettingsTable.get_active_currency()
            currency_data = {
                'currency_symbol': active_currency.currency_symbol if active_currency else '৳',
                'currency_code': active_currency.currency_code if active_currency else 'BDT',
            }
            cache.set(cache_key, currency_data, 3600)  # Cache for 1 hour
        except:
            currency_data = {
                'currency_symbol': '৳',
                'currency_code': 'BDT',
            }
    
    return currency_data



def brand_context(request):
    return {
        'brand_profile': BrandProfile.get_active_profile(),
        'brand_info': BrandProfile.get_seo_info(),
        'contact_info': BrandProfile.get_contact_info(),
    }