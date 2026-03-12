# sitemaps.py
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone
from products.models import Product, Category, Brand
from datetime import datetime

class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = 'https'

    def items(self):
        return Product.objects.filter(
            is_active=True
        ).select_related(
            'brand'
        ).prefetch_related(
            'images',
            'categories'
        ).order_by('-updated_at')

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

    def images(self, obj):
        """Add product images to sitemap for Google Image search"""
        images = []
        for img in obj.images.all()[:10]:  # Limit to 10 images per product
            images.append({
                'location': img.image.url,
                'title': obj.name,
                'caption': img.alt_text or obj.name,
                'license': 'https://genialtouch.com/terms-and-conditions/',
            })
        return images
    
    def get_urls(self, page=1, site=None, protocol=None):
        """Override to add image support"""
        urls = super().get_urls(page, site, protocol)
        for url in urls:
            item = url.get('item')
            if hasattr(item, 'images') and item.images.exists():
                url['images'] = self.images(item)
        return urls

class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Category.objects.filter(
            is_active=True
        ).prefetch_related(
            'products'
        ).order_by('display_order', 'name')

    def lastmod(self, obj):
        # Categories might not have updated_at, so use current time
        return timezone.now()

    def location(self, obj):
        return reverse('products_by_category', args=[obj.slug])
    
    def get_urls(self, page=1, site=None, protocol=None):
        """Override to add changefreq and priority based on category size"""
        urls = super().get_urls(page, site, protocol)
        for url in urls:
            item = url.get('item')
            # Adjust priority based on whether category has products
            if item.products.filter(is_active=True).count() > 0:
                url['priority'] = 0.8
            else:
                url['priority'] = 0.5
                url['changefreq'] = 'monthly'
        return urls

class BrandSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    protocol = 'https'
    
    def items(self):
        return Brand.objects.filter(
            is_active=True
        ).prefetch_related(
            'product_set'  # This is the reverse relation from Brand to Product
        ).order_by('name')
    
    def lastmod(self, obj):
        """Get the last modified date from the most recent product of this brand"""
        latest_product = obj.product_set.filter(
            is_active=True
        ).order_by('-updated_at').first()
        return latest_product.updated_at if latest_product else timezone.now()
    
    def location(self, obj):
        return reverse('products_by_brand', args=[obj.slug])
    
    def images(self, obj):
        """Add brand logo to sitemap if available"""
        if obj.logo:
            return [{
                'location': obj.logo.url,
                'title': f"{obj.name} Logo",
                'caption': f"{obj.name} - Official Brand at GenialTouch",
            }]
        return []
    
    def get_urls(self, page=1, site=None, protocol=None):
        """Override to add images and dynamic priority"""
        urls = super().get_urls(page, site, protocol)
        for url in urls:
            item = url.get('item')
            
            # Add logo image if exists
            if item.logo:
                url['images'] = self.images(item)
            
            # Adjust priority based on number of products
            product_count = item.product_set.filter(is_active=True).count()
            if product_count > 50:
                url['priority'] = 0.8
            elif product_count > 20:
                url['priority'] = 0.7
            elif product_count > 0:
                url['priority'] = 0.6
            else:
                url['priority'] = 0.4
                url['changefreq'] = 'monthly'
        
        return urls

class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    protocol = 'https'

    def items(self):
        return ['home', 'about', 'contact', 'view_all_deals', 'view_all_new_arrivals', 'return_and_refund_policy', 'terms_and_conditions', 'Replacement_Policy']

    def location(self, item):
        return reverse(item)
    
    def lastmod(self, item):
        # Static pages use current date
        return timezone.now()