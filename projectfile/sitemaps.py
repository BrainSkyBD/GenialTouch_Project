# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from products.models import Product, Category
from orders.models import Order
from datetime import datetime

class ProductSitemap(Sitemap):
    """
    Sitemap for product detail pages
    """
    changefreq = "daily"  # How often product pages change
    priority = 0.9  # High priority for product pages
    protocol = 'https'  # Your site protocol

    def items(self):
        # Return only active products that are in stock
        return Product.objects.filter(is_active=True).order_by('id')

    def lastmod(self, obj):
        # Use the product's update time
        return obj.updated_at

    def location(self, obj):
        # Generate the URL for each product
        return reverse('product_detail', args=[obj.slug])

class CategorySitemap(Sitemap):
    """
    Sitemap for category listing pages
    """
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        # Return only active categories
        return Category.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Categories might not have an update field, so use current time
        return datetime.now()

    def location(self, obj):
        return reverse('products_by_category', args=[obj.slug])

class StaticViewSitemap(Sitemap):
    """
    Sitemap for static pages like home, about, contact
    """
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'

    def items(self):
        # List all your static view names
        return ['home', 'about', 'contact', 'faq']

    def location(self, item):
        return reverse(item)