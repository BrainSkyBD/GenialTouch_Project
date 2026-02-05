# context_processors.py (create this file in your app)
from .models import CurrencySettingsTable

def currency_context(request):
    try:
        active_currency = CurrencySettingsTable.objects.get(is_active=True)
        return {
            'active_currency': active_currency,
            'currency_code': active_currency.currency_code,
            'currency_symbol': active_currency.currency_symbol,
        }
    except CurrencySettingsTable.DoesNotExist:
        # Fallback to default currency
        return {
            'active_currency': None,
            'currency_code': 'BDT',
            'currency_symbol': '৳',
        }