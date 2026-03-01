# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from products.models import Product, Category
from datetime import datetime

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Ensure we return a timezone-aware datetime
        if obj.updated_at:
            # If it's timezone-naive, make it aware
            if timezone.is_naive(obj.updated_at):
                return timezone.make_aware(obj.updated_at)
            return obj.updated_at
        return timezone.now()  # Fallback to current time

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Categories might not have updated_at, so use current time
        return timezone.now()

    def location(self, obj):
        return reverse('products_by_category', args=[obj.slug])

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'contact', 'faq']

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Static pages use current date
        return timezone.now()