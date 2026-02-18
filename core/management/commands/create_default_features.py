from django.core.management.base import BaseCommand
from core.models import SiteFeature

class Command(BaseCommand):
    help = 'Create default site features'
    
    def handle(self, *args, **options):
        default_features = [
            {'title': 'Free Delivery', 'description': 'Free delivery on orders', 'icon': 'icon-rocket', 'min_order_amount': 99},
            {'title': '7 Days Return', 'description': 'If goods have problems', 'icon': 'icon-sync', 'return_days': 90},
            {'title': 'Secure Payment', 'description': '100% secure payment', 'icon': 'icon-credit-card'},
            {'title': '24/7 Support', 'description': 'Dedicated support', 'icon': 'icon-bubbles'},
            {'title': 'Gift Service', 'description': 'Support gift service', 'icon': 'icon-gift'},
        ]
        
        for i, feature_data in enumerate(default_features):
            feature_data['order'] = i
            SiteFeature.objects.get_or_create(
                title=feature_data['title'],
                defaults=feature_data
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created default features'))