# products/context_processors.py
from .models import Category  # or wherever your Category model is located

def categories(request):
    categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children')
    return {
        'categories': categories
    }