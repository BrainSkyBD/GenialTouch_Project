# branding_management/management/commands/create_brand_info.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from branding_management.models import BrandInfo, TrustBadge, SocialShareSetting
from django.core.files.base import ContentFile
from PIL import Image
import io
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create initial brand info with default data if none exists'

    def create_default_images(self, brand_info):
        """Create default logo and favicon if they don't exist"""
        
        # Create a simple default logo if no logo exists
        if not brand_info.brand_logo:
            try:
                # Create a simple colored rectangle as logo
                img = Image.new('RGB', (200, 60), color='#0f2a5c')
                draw = Image.draw.ImageDraw(img)
                
                # Add text to logo
                from PIL import ImageFont
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except:
                    font = ImageFont.load_default()
                
                draw.text((20, 18), "SHINRAI", fill='white', font=font)
                draw.text((140, 18), "JAPAN", fill='#e8536a', font=font)
                
                # Save to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Save to model
                brand_info.brand_logo.save('default_logo.png', ContentFile(img_byte_arr), save=False)
                self.stdout.write(self.style.SUCCESS('  ✓ Default logo created'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ✗ Could not create default logo: {e}'))
        
        # Create a default favicon if none exists
        if not brand_info.brand_favicon:
            try:
                # Create simple favicon
                img = Image.new('RGB', (32, 32), color='#0f2a5c')
                
                # Save to bytes
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Save to model
                brand_info.brand_favicon.save('default_favicon.png', ContentFile(img_byte_arr), save=False)
                self.stdout.write(self.style.SUCCESS('  ✓ Default favicon created'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  ✗ Could not create default favicon: {e}'))

    def create_default_trust_badges(self, brand_info):
        """Create default trust badges"""
        
        default_badges = [
            {
                'title': '100% Halal',
                'description': 'All products are 100% Halal certified',
                'icon_class': 'fa-check-circle',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Quality Products',
                'description': 'Premium quality products from trusted suppliers',
                'icon_class': 'fa-star',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Fast Delivery',
                'description': 'Quick and reliable delivery across Japan',
                'icon_class': 'fa-truck',
                'order': 3,
                'is_active': True
            },
            {
                'title': 'Trusted Service',
                'description': '24/7 customer support for your convenience',
                'icon_class': 'fa-headset',
                'order': 4,
                'is_active': True
            },
            {
                'title': 'Secure Payment',
                'description': '100% secure payment processing',
                'icon_class': 'fa-lock',
                'order': 5,
                'is_active': True
            },
            {
                'title': 'Easy Returns',
                'description': 'Hassle-free returns within 7 days',
                'icon_class': 'fa-rotate-left',
                'order': 6,
                'is_active': True
            }
        ]
        
        for badge_data in default_badges:
            TrustBadge.objects.get_or_create(
                brand=brand_info,
                title=badge_data['title'],
                defaults={
                    'description': badge_data['description'],
                    'icon_class': badge_data['icon_class'],
                    'order': badge_data['order'],
                    'is_active': badge_data['is_active']
                }
            )
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(default_badges)} trust badges'))

    def create_social_share_settings(self, brand_info):
        """Create default social share settings"""
        
        SocialShareSetting.objects.get_or_create(
            brand=brand_info,
            defaults={
                'og_title': 'GenialTouch - Your Trusted Shopping Partner',
                'og_description': 'Shop authentic, halal-certified products at GenialTouch. Quality products, fast delivery, and trusted service.',
                'og_type': 'website',
                'og_locale': 'en_US',
                'twitter_card': 'summary_large_image',
                'twitter_site': '@GenialTouch',
                'twitter_creator': '@GenialTouch',
                'meta_robots': 'index, follow',
                'meta_revisit_after': '7 days',
                'meta_rating': 'General'
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✓ Social share settings created'))

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n=== Creating Brand Information ===\n'))
        
        # Check if BrandInfo already exists
        if BrandInfo.objects.exists():
            brand_info = BrandInfo.objects.first()
            self.stdout.write(self.style.WARNING(f'BrandInfo already exists for: {brand_info.brand_name}'))
            
            # Ask user if they want to update
            confirm = input('Do you want to update existing brand info with default values? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.SUCCESS('Operation cancelled.'))
                return
            
            self.stdout.write(self.style.SUCCESS('Updating existing brand info...'))
            
            # Update existing brand info
            brand_info.brand_name = 'SHINRAI'
            brand_info.brand_tagline = 'Your Trusted Shopping Partner'
            brand_info.brand_description = 'Bringing authentic, halal-certified Japanese products to your doorstep with trust and care.'
            brand_info.brand_email = 'info@shinrai.com'
            brand_info.brand_phone = '+81 3-1234-5678'
            brand_info.brand_phone_secondary = '+81 3-8765-4321'
            brand_info.brand_whatsapp = '+81 80-1234-5678'
            brand_info.brand_address = 'Tokyo, Japan'
            
            # Social Media
            brand_info.facebook_url = 'https://facebook.com/shinrai'
            brand_info.instagram_url = 'https://instagram.com/shinrai'
            brand_info.youtube_url = 'https://youtube.com/shinrai'
            brand_info.twitter_url = 'https://twitter.com/shinrai'
            brand_info.linkedin_url = 'https://linkedin.com/company/shinrai'
            brand_info.pinterest_url = 'https://pinterest.com/shinrai'
            brand_info.tiktok_url = 'https://tiktok.com/@shinrai'
            
            # Theme Settings - Default to theme-01-default
            brand_info.active_theme = 'theme-01-default'
            brand_info.primary_color = '#0f2a5c'
            brand_info.secondary_color = '#e8536a'
            brand_info.accent_color = '#f5b400'
            brand_info.navbar_color = '#ffffff'
            brand_info.navbar_text_color = '#16213e'
            brand_info.footer_color = '#0a1d40'
            brand_info.footer_text_color = '#c6d0ea'
            
            # Logo Settings
            brand_info.logo_size = '160px'
            brand_info.logo_width = '74%'
            brand_info.logo_height = None
            
            # SEO
            brand_info.default_meta_title = 'SHINRAI - Your Trusted Shopping Partner'
            brand_info.default_meta_description = 'Shop authentic, halal-certified Japanese products at SHINRAI. Quality products, fast delivery, and trusted service.'
            brand_info.default_meta_keywords = 'SHINRAI, online shopping, halal products, e-commerce, Japan'
            brand_info.meta_author = 'SHINRAI'
            
            # Copyright
            brand_info.copyright_text = '© 2026 SHINRAI. All rights reserved.'
            
            # Legal URLs
            brand_info.privacy_policy_url = '/privacy-policy/'
            brand_info.terms_conditions_url = '/terms-conditions/'
            brand_info.return_policy_url = '/return-policy/'
            brand_info.shipping_policy_url = '/shipping-policy/'
            brand_info.refund_policy_url = '/refund-policy/'
            brand_info.cookie_policy_url = '/cookie-policy/'
            
            # Business Information
            brand_info.business_registration_number = 'JP-12345678'
            brand_info.tax_id = 'JP-987654321'
            brand_info.year_established = 2020
            brand_info.business_type = 'E-commerce'
            
            # Additional Settings
            brand_info.show_brand_section = True
            brand_info.show_trust_badges = True
            brand_info.show_social_icons = True
            brand_info.show_newsletter = True
            
            # Custom CSS/JS (leave as None/default)
            brand_info.custom_css = None
            brand_info.custom_js = None
            
            # Advanced Settings
            brand_info.enable_cache = True
            brand_info.cache_duration = 3600
            
            # Additional URLs
            brand_info.track_order_url = '/track-order/'
            brand_info.help_center_url = '/help-center/'
            brand_info.language = 'English'
            brand_info.currency = 'JPY'
            
            brand_info.save()
            self.stdout.write(self.style.SUCCESS('✓ BrandInfo updated successfully'))
            
        else:
            # Get the first superuser as updated_by
            try:
                admin_user = User.objects.filter(is_superuser=True).first()
            except:
                admin_user = None
            
            # Create new BrandInfo
            self.stdout.write(self.style.SUCCESS('Creating new BrandInfo...'))
            
            brand_info = BrandInfo.objects.create(
                brand_name='SHINRAI',
                brand_tagline='Your Trusted Shopping Partner',
                brand_description='Bringing authentic, halal-certified Japanese products to your doorstep with trust and care.',
                brand_email='info@shinrai.com',
                brand_phone='+81 3-1234-5678',
                brand_phone_secondary='+81 3-8765-4321',
                brand_whatsapp='+81 80-1234-5678',
                brand_address='Tokyo, Japan',
                
                # Social Media
                facebook_url='https://facebook.com/shinrai',
                instagram_url='https://instagram.com/shinrai',
                youtube_url='https://youtube.com/shinrai',
                twitter_url='https://twitter.com/shinrai',
                linkedin_url='https://linkedin.com/company/shinrai',
                pinterest_url='https://pinterest.com/shinrai',
                tiktok_url='https://tiktok.com/@shinrai',
                
                # Theme Settings - Default to theme-01-default
                active_theme='theme-01-default',
                primary_color='#0f2a5c',
                secondary_color='#e8536a',
                accent_color='#f5b400',
                navbar_color='#ffffff',
                navbar_text_color='#16213e',
                footer_color='#0a1d40',
                footer_text_color='#c6d0ea',
                
                # Logo Settings
                logo_size='160px',
                logo_width='74%',
                
                # SEO
                default_meta_title='SHINRAI - Your Trusted Shopping Partner',
                default_meta_description='Shop authentic, halal-certified Japanese products at SHINRAI. Quality products, fast delivery, and trusted service.',
                default_meta_keywords='SHINRAI, online shopping, halal products, e-commerce, Japan',
                meta_author='SHINRAI',
                
                # Copyright
                copyright_text='© 2026 SHINRAI. All rights reserved.',
                
                # Legal URLs
                privacy_policy_url='/privacy-policy/',
                terms_conditions_url='/terms-conditions/',
                return_policy_url='/return-policy/',
                shipping_policy_url='/shipping-policy/',
                refund_policy_url='/refund-policy/',
                cookie_policy_url='/cookie-policy/',
                
                # Business Information
                business_registration_number='JP-12345678',
                tax_id='JP-987654321',
                year_established=2020,
                business_type='E-commerce',
                
                # Additional Settings
                show_brand_section=True,
                show_trust_badges=True,
                show_social_icons=True,
                show_newsletter=True,
                
                # Advanced Settings
                enable_cache=True,
                cache_duration=3600,
                
                # Additional URLs
                track_order_url='/track-order/',
                help_center_url='/help-center/',
                language='English',
                currency='JPY',
                
                updated_by=admin_user
            )
            
            self.stdout.write(self.style.SUCCESS('✓ BrandInfo created successfully'))
        
        # Create default images
        self.stdout.write(self.style.SUCCESS('\nCreating default images...'))
        self.create_default_images(brand_info)
        
        # Create default trust badges
        self.stdout.write(self.style.SUCCESS('\nCreating default trust badges...'))
        self.create_default_trust_badges(brand_info)
        
        # Create social share settings
        self.stdout.write(self.style.SUCCESS('\nCreating social share settings...'))
        self.create_social_share_settings(brand_info)
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✅ Brand Information Setup Complete!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Brand: {brand_info.brand_name}'))
        self.stdout.write(self.style.SUCCESS(f'🎨 Active Theme: {brand_info.active_theme}'))
        self.stdout.write(self.style.SUCCESS(f'📧 Email: {brand_info.brand_email}'))
        self.stdout.write(self.style.SUCCESS(f'📱 Phone: {brand_info.brand_phone}'))
        self.stdout.write(self.style.SUCCESS(f'🏢 Address: {brand_info.brand_address}'))
        self.stdout.write(self.style.SUCCESS(f'🌐 Currency: {brand_info.currency}'))
        
        trust_count = TrustBadge.objects.filter(brand=brand_info, is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f'🛡️ Trust Badges: {trust_count} active'))
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('🎯 Next Steps:'))
        self.stdout.write(self.style.SUCCESS('1. Upload your brand logo in Django Admin'))
        self.stdout.write(self.style.SUCCESS('2. Upload your favicon in Django Admin'))
        self.stdout.write(self.style.SUCCESS('3. Customize colors and settings as needed'))
        self.stdout.write(self.style.SUCCESS('4. Visit your website to see the changes!'))
        self.stdout.write(self.style.SUCCESS('='*50 + '\n'))