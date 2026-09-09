# branding_management/management/commands/create_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw
import io
import os
import random
from decimal import Decimal

# Import all models
from products.models import (
    Product, Category, Brand, Attribute, AttributeValue, 
    ProductAttribute, ProductVariation, ProductImage
)
from core.models import Banner, Promotion, HomeAd, SiteFeature
from branding_management.models import BrandInfo, TrustBadge, SocialShareSetting

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for the e-commerce website'

    def create_default_image(self, width=200, height=200, color='#0f2a5c', text=''):
        """Create a simple colored image with text"""
        try:
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)
            
            if text:
                try:
                    from PIL import ImageFont
                    try:
                        font = ImageFont.truetype("arial.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
                
                text_width = draw.textlength(text, font=font)
                x = (width - text_width) // 2
                y = (height - 24) // 2
                draw.text((x, y), text, fill='white', font=font)
            
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return ContentFile(img_byte_arr)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not create image: {e}'))
            return None

    def create_categories(self):
        """Create sample categories"""
        self.stdout.write('Creating categories...')
        
        categories_data = [
            {
                'name': 'Halal Food',
                'slug': 'halal-food',
                'description': '100% Halal certified food products from trusted suppliers',
                'is_featured': True,
                'display_order': 1
            },
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Latest electronics and gadgets at competitive prices',
                'is_featured': True,
                'display_order': 2
            },
            {
                'name': 'Clothing',
                'slug': 'clothing',
                'description': 'Fashionable clothing for men, women, and children',
                'is_featured': True,
                'display_order': 3
            },
            {
                'name': 'Beauty & Health',
                'slug': 'beauty-health',
                'description': 'Premium beauty and health products',
                'is_featured': False,
                'display_order': 4
            },
            {
                'name': 'Home & Kitchen',
                'slug': 'home-kitchen',
                'description': 'Quality home and kitchen essentials',
                'is_featured': False,
                'display_order': 5
            },
            {
                'name': 'Toys & Games',
                'slug': 'toys-games',
                'description': 'Fun toys and games for all ages',
                'is_featured': False,
                'display_order': 6
            }
        ]
        
        categories = []
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'is_featured': data['is_featured'],
                    'display_order': data['display_order'],
                    'is_active': True
                }
            )
            
            # Create category image
            if created or not category.image:
                img_file = self.create_default_image(400, 400, '#0f2a5c', data['name'][:2])
                if img_file:
                    category.image.save(f'{data["slug"]}.png', img_file, save=True)
            
            categories.append(category)
            self.stdout.write(f'  ✓ Created category: {category.name}')
        
        return categories

    def create_brands(self):
        """Create sample brands"""
        self.stdout.write('Creating brands...')
        
        brands_data = [
            {'name': 'Sony', 'slug': 'sony', 'description': 'Japanese electronics giant'},
            {'name': 'Samsung', 'slug': 'samsung', 'description': 'Global technology leader'},
            {'name': 'Apple', 'slug': 'apple', 'description': 'Premium technology products'},
            {'name': 'Nike', 'slug': 'nike', 'description': 'World-leading sports brand'},
            {'name': 'Adidas', 'slug': 'adidas', 'description': 'German sports apparel brand'},
            {'name': 'Halal Food Co.', 'slug': 'halal-food-co', 'description': 'Premium halal food products'},
            {'name': 'Saudi Dates', 'slug': 'saudi-dates', 'description': 'Premium dates from Saudi Arabia'},
            {'name': 'LG', 'slug': 'lg', 'description': 'Korean electronics manufacturer'},
            {'name': 'Puma', 'slug': 'puma', 'description': 'German sportswear brand'},
            {'name': 'Zara', 'slug': 'zara', 'description': 'Spanish fashion retailer'}
        ]
        
        brands = []
        for data in brands_data:
            brand, created = Brand.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'is_active': True
                }
            )
            
            # Create brand logo
            if created or not brand.logo:
                img_file = self.create_default_image(200, 200, '#1e7a3d', data['name'][:3])
                if img_file:
                    brand.logo.save(f'{data["slug"]}.png', img_file, save=True)
            
            brands.append(brand)
            self.stdout.write(f'  ✓ Created brand: {brand.name}')
        
        return brands

    def create_attributes(self):
        """Create sample attributes"""
        self.stdout.write('Creating attributes...')
        
        attributes_data = [
            {'name': 'Size', 'description': 'Product size'},
            {'name': 'Color', 'description': 'Product color'},
            {'name': 'Material', 'description': 'Product material'},
            {'name': 'Weight', 'description': 'Product weight'},
            {'name': 'Capacity', 'description': 'Product capacity'},
            {'name': 'Model', 'description': 'Product model'},
            {'name': 'Brand', 'description': 'Product brand'}
        ]
        
        attributes = []
        for data in attributes_data:
            attr, created = Attribute.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            attributes.append(attr)
            self.stdout.write(f'  ✓ Created attribute: {attr.name}')
        
        # Create attribute values
        attribute_values_data = {
            'Size': ['Small', 'Medium', 'Large', 'XL', 'XXL'],
            'Color': ['Red', 'Blue', 'Green', 'Black', 'White', 'Gold', 'Silver'],
            'Material': ['Cotton', 'Polyester', 'Leather', 'Metal', 'Plastic', 'Glass'],
            'Weight': ['1kg', '2kg', '5kg', '10kg'],
            'Capacity': ['1GB', '2GB', '4GB', '8GB', '16GB', '32GB', '64GB', '128GB'],
            'Model': ['Standard', 'Pro', 'Max', 'Plus', 'Mini'],
            'Brand': ['Sony', 'Samsung', 'Apple', 'Nike', 'Adidas']
        }
        
        attribute_values = []
        for attr in attributes:
            values = attribute_values_data.get(attr.name, [])
            for value in values:
                attr_val, created = AttributeValue.objects.get_or_create(
                    attribute=attr,
                    value=value
                )
                attribute_values.append(attr_val)
                if created:
                    self.stdout.write(f'    ✓ Created value: {attr_val}')
        
        return attributes, attribute_values

    def create_products(self, categories, brands, attribute_values):
        """Create sample products"""
        self.stdout.write('Creating products...')
        
        products_data = [
            # Halal Food Products
            {
                'name': 'Premium Halal Chicken Nuggets',
                'slug': 'premium-halal-chicken-nuggets',
                'brand': 'Halal Food Co.',
                'categories': ['Halal Food'],
                'price': 890,
                'discount_price': 720,
                'sku': 'HF-001',
                'description': 'Premium quality halal chicken nuggets, perfect for quick meals. Made from 100% halal chicken breast meat with a crispy coating.',
                'is_featured': True,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': 'Organic Basmati Rice 5kg',
                'slug': 'organic-basmati-rice-5kg',
                'brand': 'Halal Food Co.',
                'categories': ['Halal Food'],
                'price': 1450,
                'discount_price': 1250,
                'sku': 'HF-002',
                'description': 'Premium organic basmati rice from the foothills of Himalayas. Long grain, aromatic, and perfect for biryani.',
                'is_featured': True,
                'min_delivery_days': 2,
                'max_delivery_days': 4,
            },
            {
                'name': 'Saudi Premium Dates 1kg',
                'slug': 'saudi-premium-dates-1kg',
                'brand': 'Saudi Dates',
                'categories': ['Halal Food'],
                'price': 1250,
                'discount_price': 1050,
                'sku': 'HF-003',
                'description': 'Premium quality dates from Saudi Arabia. Naturally sweet, rich in fiber and essential nutrients.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': 'Halal Beef Sausages 500g',
                'slug': 'halal-beef-sausages-500g',
                'brand': 'Halal Food Co.',
                'categories': ['Halal Food'],
                'price': 950,
                'discount_price': 820,
                'sku': 'HF-004',
                'description': '100% halal beef sausages, seasoned with authentic spices. Perfect for breakfast and BBQs.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': 'Coconut Milk 6-Pack',
                'slug': 'coconut-milk-6-pack',
                'brand': 'Halal Food Co.',
                'categories': ['Halal Food'],
                'price': 980,
                'discount_price': None,
                'sku': 'HF-005',
                'description': 'Premium coconut milk in convenient 6-pack. Perfect for cooking, smoothies, and baking.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': 'Organic Honey Jar 500g',
                'slug': 'organic-honey-jar-500g',
                'brand': 'Halal Food Co.',
                'categories': ['Halal Food'],
                'price': 1680,
                'discount_price': 1480,
                'sku': 'HF-006',
                'description': 'Pure organic honey from pristine forests. Rich in antioxidants and natural enzymes.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 4,
            },
            
            # Electronics Products
            {
                'name': 'iPhone 15 Pro Max 256GB',
                'slug': 'iphone-15-pro-max-256gb',
                'brand': 'Apple',
                'categories': ['Electronics'],
                'price': 159900,
                'discount_price': 149900,
                'sku': 'EL-001',
                'description': 'Latest iPhone with A17 Pro chip, titanium body, and advanced camera system.',
                'is_featured': True,
                'min_delivery_days': 1,
                'max_delivery_days': 2,
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'slug': 'samsung-galaxy-s24-ultra',
                'brand': 'Samsung',
                'categories': ['Electronics'],
                'price': 139900,
                'discount_price': 129900,
                'sku': 'EL-002',
                'description': 'Samsung\'s flagship with AI-powered features, S Pen, and pro-grade camera.',
                'is_featured': True,
                'min_delivery_days': 1,
                'max_delivery_days': 2,
            },
            {
                'name': 'Sony WH-1000XM5 Headphones',
                'slug': 'sony-wh-1000xm5-headphones',
                'brand': 'Sony',
                'categories': ['Electronics'],
                'price': 29800,
                'discount_price': 26800,
                'sku': 'EL-003',
                'description': 'Industry-leading noise cancellation with exceptional sound quality and comfort.',
                'is_featured': False,
                'min_delivery_days': 1,
                'max_delivery_days': 3,
            },
            {
                'name': 'LG 4K OLED Smart TV 65"',
                'slug': 'lg-4k-oled-smart-tv-65',
                'brand': 'LG',
                'categories': ['Electronics'],
                'price': 189900,
                'discount_price': 169900,
                'sku': 'EL-004',
                'description': '65-inch 4K OLED TV with perfect blacks, infinite contrast, and AI processing.',
                'is_featured': False,
                'min_delivery_days': 3,
                'max_delivery_days': 5,
            },
            {
                'name': 'Samsung Galaxy Watch 6',
                'slug': 'samsung-galaxy-watch-6',
                'brand': 'Samsung',
                'categories': ['Electronics'],
                'price': 49800,
                'discount_price': 44800,
                'sku': 'EL-005',
                'description': 'Advanced smartwatch with fitness tracking, ECG monitor, and sleep analysis.',
                'is_featured': False,
                'min_delivery_days': 1,
                'max_delivery_days': 2,
            },
            {
                'name': 'Sony PlayStation 5',
                'slug': 'sony-playstation-5',
                'brand': 'Sony',
                'categories': ['Electronics'],
                'price': 79800,
                'discount_price': 74800,
                'sku': 'EL-006',
                'description': 'Next-gen gaming console with ultra-fast SSD, 4K gaming, and immersive controller.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            
            # Clothing Products
            {
                'name': 'Nike Air Max 270',
                'slug': 'nike-air-max-270',
                'brand': 'Nike',
                'categories': ['Clothing'],
                'price': 24800,
                'discount_price': 21800,
                'sku': 'CL-001',
                'description': 'Iconic Nike Air Max with visible Air cushioning and modern design.',
                'is_featured': True,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': 'Adidas Ultraboost 22',
                'slug': 'adidas-ultraboost-22',
                'brand': 'Adidas',
                'categories': ['Clothing'],
                'price': 22800,
                'discount_price': 19800,
                'sku': 'CL-002',
                'description': 'Premium running shoes with responsive Boost foam and Primeknit upper.',
                'is_featured': True,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': "Men's Premium Winter Jacket",
                'slug': 'mens-premium-winter-jacket',
                'brand': 'Zara',
                'categories': ['Clothing'],
                'price': 12800,
                'discount_price': 10800,
                'sku': 'CL-003',
                'description': 'Stylish and warm winter jacket for men. Water-resistant and insulated.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 4,
            },
            {
                'name': "Women's Elegant Abaya",
                'slug': 'womens-elegant-abaya',
                'brand': 'Zara',
                'categories': ['Clothing'],
                'price': 9800,
                'discount_price': 8800,
                'sku': 'CL-004',
                'description': 'Elegant and modest abaya with premium fabric and beautiful design.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 4,
            },
            {
                'name': 'Puma Suede Classic',
                'slug': 'puma-suede-classic',
                'brand': 'Puma',
                'categories': ['Clothing'],
                'price': 12800,
                'discount_price': 10800,
                'sku': 'CL-005',
                'description': 'Classic Puma Suede sneakers, a timeless style icon.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            },
            {
                'name': "Kids' Sports T-Shirt 3-Pack",
                'slug': 'kids-sports-t-shirt-3-pack',
                'brand': 'Adidas',
                'categories': ['Clothing'],
                'price': 5980,
                'discount_price': 4980,
                'sku': 'CL-006',
                'description': 'Comfortable and durable sports t-shirt pack for kids.',
                'is_featured': False,
                'min_delivery_days': 2,
                'max_delivery_days': 3,
            }
        ]
        
        products_created = []
        for data in products_data:
            try:
                # Get brand
                brand = Brand.objects.get(name=data['brand'])
                
                # Get categories
                product_categories = Category.objects.filter(name__in=data['categories'])
                
                # Create product
                product, created = Product.objects.get_or_create(
                    slug=data['slug'],
                    defaults={
                        'name': data['name'],
                        'brand': brand,
                        'price': Decimal(str(data['price'])),
                        'discount_price': Decimal(str(data['discount_price'])) if data['discount_price'] else None,
                        'sku': data['sku'],
                        'description': data['description'],
                        'is_featured': data['is_featured'],
                        'is_active': True,
                        'min_delivery_days': data['min_delivery_days'],
                        'max_delivery_days': data['max_delivery_days'],
                    }
                )
                
                # Add categories
                if created:
                    product.categories.set(product_categories)
                
                # Create product image
                if created or not product.images.exists():
                    img_file = self.create_default_image(800, 600, '#e8f0fe', data['name'][:15])
                    if img_file:
                        ProductImage.objects.create(
                            product=product,
                            image=img_file,
                            alt_text=data['name'],
                            is_featured=True,
                            display_order=1
                        )
                
                # Create product variation (for electronics with storage)
                if 'Electronics' in data['categories'] and created:
                    try:
                        size_attr = Attribute.objects.get(name='Capacity')
                        size_values = ['64GB', '128GB', '256GB']
                        
                        for size in size_values[:2]:
                            attr_val = AttributeValue.objects.get(attribute=size_attr, value=size)
                            
                            variation = ProductVariation.objects.create(
                                product=product,
                                sku=f"{data['sku']}-{size.replace('GB', '')}",
                                price=Decimal(str(data['price'])) if size == '64GB' else Decimal(str(data['price'])) + Decimal('5000'),
                                stock=random.randint(10, 50),
                                is_active=True
                            )
                            variation.attributes.add(attr_val)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ! Could not create variations for {data["name"]}: {e}'))
                
                # Create product variation (for clothing with sizes)
                if 'Clothing' in data['categories'] and created:
                    try:
                        size_attr = Attribute.objects.get(name='Size')
                        size_values = ['S', 'M', 'L', 'XL']
                        
                        for size in size_values[:3]:
                            attr_val = AttributeValue.objects.get(attribute=size_attr, value=size)
                            
                            variation = ProductVariation.objects.create(
                                product=product,
                                sku=f"{data['sku']}-{size}",
                                price=Decimal(str(data['price'])),
                                stock=random.randint(15, 40),
                                is_active=True
                            )
                            variation.attributes.add(attr_val)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'  ! Could not create variations for {data["name"]}: {e}'))
                
                products_created.append(product)
                self.stdout.write(f'  ✓ Created product: {product.name}')
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ✗ Error creating product {data["name"]}: {e}'))
        
        return products_created

    def create_banners(self):
        """Create sample banners"""
        self.stdout.write('Creating banners...')
        
        banners_data = [
            {
                'title': 'Summer Sale - Up to 50% Off',
                'url': '/products/?featured=true',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'New Arrivals - Spring Collection',
                'url': '/products/?sort=newest',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Halal Food - 100% Certified',
                'url': '/category/halal-food/',
                'order': 3,
                'is_active': True
            }
        ]
        
        banners = []
        for data in banners_data:
            banner, created = Banner.objects.get_or_create(
                title=data['title'],
                defaults={
                    'url': data['url'],
                    'order': data['order'],
                    'is_active': data['is_active']
                }
            )
            
            if created or not banner.image:
                img_file = self.create_default_image(1200, 400, '#0f2a5c', data['title'][:20])
                if img_file:
                    banner.image.save(f'banner_{data["order"]}.png', img_file, save=True)
            
            banners.append(banner)
            self.stdout.write(f'  ✓ Created banner: {banner.title}')
        
        return banners

    def create_promotions(self):
        """Create sample promotions"""
        self.stdout.write('Creating promotions...')
        
        promotions_data = [
            {
                'title': 'Special Offer - 30% Off',
                'url': '/products/?featured=true',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Free Delivery on Orders Over ৳5000',
                'url': '/products/',
                'order': 2,
                'is_active': True
            }
        ]
        
        promotions = []
        for data in promotions_data:
            promo, created = Promotion.objects.get_or_create(
                title=data['title'],
                defaults={
                    'url': data['url'],
                    'order': data['order'],
                    'is_active': data['is_active']
                }
            )
            
            if created or not promo.image:
                img_file = self.create_default_image(400, 300, '#1e7a3d', data['title'][:15])
                if img_file:
                    promo.image.save(f'promo_{data["order"]}.png', img_file, save=True)
            
            promotions.append(promo)
            self.stdout.write(f'  ✓ Created promotion: {promo.title}')
        
        return promotions

    def create_home_ads(self):
        """Create sample home ads"""
        self.stdout.write('Creating home ads...')
        
        ads_data = [
            {
                'title': 'Premium Electronics',
                'url': '/category/electronics/',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Fashion Collection',
                'url': '/category/clothing/',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Halal Food Specials',
                'url': '/category/halal-food/',
                'order': 3,
                'is_active': True
            },
            {
                'title': 'Home & Kitchen',
                'url': '/category/home-kitchen/',
                'order': 4,
                'is_active': True
            },
            {
                'title': 'Beauty Products',
                'url': '/category/beauty-health/',
                'order': 5,
                'is_active': True
            }
        ]
        
        ads = []
        for data in ads_data:
            ad, created = HomeAd.objects.get_or_create(
                title=data['title'],
                defaults={
                    'url': data['url'],
                    'order': data['order'],
                    'is_active': data['is_active']
                }
            )
            
            if created or not ad.image:
                img_file = self.create_default_image(600, 400, '#7a3fc4', data['title'][:15])
                if img_file:
                    ad.image.save(f'ad_{data["order"]}.png', img_file, save=True)
            
            ads.append(ad)
            self.stdout.write(f'  ✓ Created home ad: {ad.title}')
        
        return ads

    def create_site_features(self):
        """Create sample site features"""
        self.stdout.write('Creating site features...')
        
        features_data = [
            {
                'title': 'Free Delivery',
                'description': 'Free delivery on all orders',
                'icon': 'icon-truck',
                'min_order_amount': '5000',
                'return_days': None,
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Secure Payment',
                'description': '100% secure payment gateway',
                'icon': 'icon-lock',
                'min_order_amount': None,
                'return_days': None,
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Easy Returns',
                'description': 'Hassle-free returns',
                'icon': 'icon-sync',
                'min_order_amount': None,
                'return_days': 7,
                'order': 3,
                'is_active': True
            },
            {
                'title': 'Quality Guarantee',
                'description': 'Premium quality products',
                'icon': 'icon-star',
                'min_order_amount': None,
                'return_days': None,
                'order': 4,
                'is_active': True
            },
            {
                'title': '24/7 Support',
                'description': 'Dedicated customer support',
                'icon': 'icon-bubbles',
                'min_order_amount': None,
                'return_days': None,
                'order': 5,
                'is_active': True
            }
        ]
        
        features = []
        for data in features_data:
            feature, created = SiteFeature.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'icon': data['icon'],
                    'min_order_amount': data['min_order_amount'],
                    'return_days': data['return_days'],
                    'order': data['order'],
                    'is_active': data['is_active']
                }
            )
            features.append(feature)
            self.stdout.write(f'  ✓ Created feature: {feature.title}')
        
        return features

    def create_brand_info(self):
        """Create brand information"""
        self.stdout.write('Creating brand information...')
        
        brand_info, created = BrandInfo.objects.get_or_create(
            brand_name='SHINRAI',
            defaults={
                'brand_tagline': 'Your Trusted Shopping Partner',
                'brand_description': 'Bringing authentic, halal-certified Japanese products to your doorstep with trust and care.',
                'brand_email': 'info@shinrai.com',
                'brand_phone': '+81 3-1234-5678',
                'brand_whatsapp': '+81 80-1234-5678',
                'brand_address': 'Tokyo, Japan',
                'primary_color': '#0f2a5c',
                'secondary_color': '#e8536a',
                'accent_color': '#f5b400',
                'navbar_color': '#ffffff',
                'navbar_text_color': '#16213e',
                'footer_color': '#0a1d40',
                'footer_text_color': '#c6d0ea',
                'logo_size': '160px',
                'logo_width': '74%',
                'active_theme': 'theme-01-default',
                'copyright_text': '© 2026 SHINRAI. All rights reserved.',
                'default_meta_title': 'SHINRAI - Your Trusted Shopping Partner',
                'default_meta_description': 'Shop authentic, halal-certified Japanese products at SHINRAI.',
                'default_meta_keywords': 'SHINRAI, online shopping, halal products, e-commerce, Japan',
                'meta_author': 'SHINRAI',
                'show_brand_section': True,
                'show_trust_badges': True,
                'show_social_icons': True,
                'show_newsletter': True,
                'enable_cache': True,
                'cache_duration': 3600,
                'language': 'English',
                'currency': 'BDT',
                'track_order_url': '/track-order/',
                'help_center_url': '/help-center/',
                'privacy_policy_url': '/privacy-policy/',
                'terms_conditions_url': '/terms-conditions/',
                'return_policy_url': '/return-policy/',
                'shipping_policy_url': '/shipping-policy/',
                'refund_policy_url': '/refund-policy/',
                'cookie_policy_url': '/cookie-policy/',
            }
        )
        
        # Create logo
        if created or not brand_info.brand_logo:
            img_file = self.create_default_image(200, 60, '#0f2a5c', 'SHINRAI')
            if img_file:
                brand_info.brand_logo.save('logo.png', img_file, save=True)
        
        # Create favicon
        if created or not brand_info.brand_favicon:
            img_file = self.create_default_image(32, 32, '#0f2a5c', 'S')
            if img_file:
                brand_info.brand_favicon.save('favicon.png', img_file, save=True)
        
        self.stdout.write(f'  ✓ Created brand info: {brand_info.brand_name}')
        
        return brand_info

    def create_trust_badges(self, brand_info):
        """Create trust badges"""
        self.stdout.write('Creating trust badges...')
        
        badges_data = [
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
            }
        ]
        
        badges = []
        for data in badges_data:
            badge, created = TrustBadge.objects.get_or_create(
                brand=brand_info,
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'icon_class': data['icon_class'],
                    'order': data['order'],
                    'is_active': data['is_active']
                }
            )
            badges.append(badge)
            self.stdout.write(f'  ✓ Created trust badge: {badge.title}')
        
        return badges

    def create_social_share_settings(self, brand_info):
        """Create social share settings"""
        self.stdout.write('Creating social share settings...')
        
        social_settings, created = SocialShareSetting.objects.get_or_create(
            brand=brand_info,
            defaults={
                'og_title': 'SHINRAI - Your Trusted Shopping Partner',
                'og_description': 'Shop authentic, halal-certified Japanese products at SHINRAI.',
                'og_type': 'website',
                'og_locale': 'en_US',
                'twitter_card': 'summary_large_image',
                'twitter_site': '@SHINRAI',
                'twitter_creator': '@SHINRAI',
                'meta_robots': 'index, follow',
                'meta_revisit_after': '7 days',
                'meta_rating': 'General'
            }
        )
        
        self.stdout.write('  ✓ Created social share settings')
        return social_settings

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('🚀 Creating Sample Data'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Create all data
        categories = self.create_categories()
        brands = self.create_brands()
        attributes, attribute_values = self.create_attributes()
        products = self.create_products(categories, brands, attribute_values)
        banners = self.create_banners()
        promotions = self.create_promotions()
        home_ads = self.create_home_ads()
        site_features = self.create_site_features()
        brand_info = self.create_brand_info()
        trust_badges = self.create_trust_badges(brand_info)
        social_settings = self.create_social_share_settings(brand_info)
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('✅ Sample Data Creation Complete!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS(f'\n📊 Summary:'))
        self.stdout.write(self.style.SUCCESS(f'  • Categories: {len(categories)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Brands: {len(brands)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Products: {len(products)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Banners: {len(banners)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Promotions: {len(promotions)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Home Ads: {len(home_ads)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Site Features: {len(site_features)}'))
        self.stdout.write(self.style.SUCCESS(f'  • Trust Badges: {len(trust_badges)}'))
        self.stdout.write(self.style.SUCCESS(f'\n🏷️ Brand: {brand_info.brand_name}'))
        self.stdout.write(self.style.SUCCESS(f'🎨 Theme: {brand_info.active_theme}'))
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('\n🎯 Next Steps:'))
        self.stdout.write(self.style.SUCCESS('1. Run: python manage.py runserver'))
        self.stdout.write(self.style.SUCCESS('2. Visit your website to see the sample data'))
        self.stdout.write(self.style.SUCCESS('3. Customize data from Django Admin panel'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))