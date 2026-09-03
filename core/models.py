from django.db import models
from django.core.exceptions import ValidationError

from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import os

class BrandProfile(models.Model):
    """
    Complete Brand Profile with all possible details including logo sizes,
    image dimensions, brand guidelines, etc.
    """
    
    # ============ BASIC BRAND INFO ============
    brand_name = models.CharField(
        max_length=255,
        verbose_name="Brand Name",
        help_text="Your website/brand name"
    )
    
    brand_tagline = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Tagline/Slogan",
        help_text="Short tagline or slogan (e.g., 'Building the Future')"
    )
    
    brand_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Description",
        help_text="Brief description about your brand (max 500 characters)"
    )
    
    brand_story = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Story",
        help_text="Complete brand story, mission, vision"
    )
    
    # ============ LOGO WITH SIZES ============
    # Primary Logo
    logo_primary = models.ImageField(
        upload_to='brand/logos/primary/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Primary Logo",
        help_text="Main logo (Recommended: 500x500px, Max: 2MB)"
    )
    
    logo_primary_width = models.PositiveIntegerField(
        default=500,
        verbose_name="Primary Logo Width",
        help_text="Width in pixels (e.g., 500)"
    )
    
    logo_primary_height = models.PositiveIntegerField(
        default=500,
        verbose_name="Primary Logo Height",
        help_text="Height in pixels (e.g., 500)"
    )
    
    # Alternative Logo (White/Reverse)
    logo_alternative = models.ImageField(
        upload_to='brand/logos/alternative/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'svg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Alternative Logo (White/Reverse)",
        help_text="White/reverse version for dark backgrounds (Recommended: 500x500px)"
    )
    
    # Horizontal Logo
    logo_horizontal = models.ImageField(
        upload_to='brand/logos/horizontal/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Horizontal Logo",
        help_text="Horizontal version for header (Recommended: 600x200px)"
    )
    
    logo_horizontal_width = models.PositiveIntegerField(
        default=600,
        verbose_name="Horizontal Logo Width",
        help_text="Width in pixels (e.g., 600)"
    )
    
    logo_horizontal_height = models.PositiveIntegerField(
        default=200,
        verbose_name="Horizontal Logo Height",
        help_text="Height in pixels (e.g., 200)"
    )
    
    # Small Logo (Favicon/Icon)
    logo_small = models.ImageField(
        upload_to='brand/logos/small/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'ico', 'svg']),
        ],
        blank=True,
        null=True,
        verbose_name="Small Logo (Icon)",
        help_text="Small icon for favicon (Recommended: 32x32px or 64x64px)"
    )
    
    logo_small_width = models.PositiveIntegerField(
        default=32,
        verbose_name="Small Logo Width",
        help_text="Width in pixels (e.g., 32)"
    )
    
    logo_small_height = models.PositiveIntegerField(
        default=32,
        verbose_name="Small Logo Height",
        help_text="Height in pixels (e.g., 32)"
    )
    
    # Logo Alt Text
    logo_alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Logo Alt Text",
        help_text="Alternative text for logo (SEO & Accessibility)"
    )
    
    # ============ FAVICONS ============
    favicon_16x16 = models.ImageField(
        upload_to='brand/favicons/16x16/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'ico'])],
        blank=True,
        null=True,
        verbose_name="Favicon 16x16",
        help_text="16x16 pixels favicon"
    )
    
    favicon_32x32 = models.ImageField(
        upload_to='brand/favicons/32x32/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'ico'])],
        blank=True,
        null=True,
        verbose_name="Favicon 32x32",
        help_text="32x32 pixels favicon"
    )
    
    favicon_48x48 = models.ImageField(
        upload_to='brand/favicons/48x48/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'ico'])],
        blank=True,
        null=True,
        verbose_name="Favicon 48x48",
        help_text="48x48 pixels favicon"
    )
    
    favicon_apple = models.ImageField(
        upload_to='brand/favicons/apple/',
        validators=[FileExtensionValidator(allowed_extensions=['png'])],
        blank=True,
        null=True,
        verbose_name="Apple Touch Icon",
        help_text="Apple touch icon (Recommended: 180x180px)"
    )
    
    # ============ AUTHOR / OWNER INFO ============
    website_author = models.CharField(
        max_length=255,
        verbose_name="Website Author/Owner",
        help_text="Name of the website author/owner"
    )
    
    author_bio = models.TextField(
        blank=True,
        null=True,
        verbose_name="Author Bio",
        help_text="Brief biography of the author"
    )
    
    author_image = models.ImageField(
        upload_to='brand/authors/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Author Image",
        help_text="Profile picture of the author (Recommended: 400x400px, Max: 500KB)"
    )
    
    author_image_width = models.PositiveIntegerField(
        default=400,
        verbose_name="Author Image Width",
        help_text="Width in pixels (e.g., 400)"
    )
    
    author_image_height = models.PositiveIntegerField(
        default=400,
        verbose_name="Author Image Height",
        help_text="Height in pixels (e.g., 400)"
    )
    
    author_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Author Email",
        help_text="Contact email of the author"
    )
    
    author_designation = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Author Designation",
        help_text="e.g., Founder, CEO, Developer"
    )
    
    author_social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Author Social Links",
        help_text='Example: {"facebook": "url", "twitter": "url", "linkedin": "url", "github": "url"}'
    )
    
    # ============ CONTACT INFO ============
    contact_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Contact Email",
        help_text="General contact email for the website"
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Contact Phone",
        help_text="Contact phone number with country code"
    )
    
    contact_phone_country = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Phone Country Code",
        help_text="e.g., +880, +1, +44"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Physical Address",
        help_text="Complete physical address"
    )
    
    address_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name="Latitude",
        help_text="GPS Latitude for Google Maps"
    )
    
    address_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        blank=True,
        null=True,
        verbose_name="Longitude",
        help_text="GPS Longitude for Google Maps"
    )
    
    # ============ SEO INFO ============
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        null=True,
        verbose_name="Meta Title",
        help_text="SEO title (Recommended: 50-60 characters)"
    )
    
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        null=True,
        verbose_name="Meta Description",
        help_text="SEO description (Recommended: 150-160 characters)"
    )
    
    meta_keywords = models.TextField(
        blank=True,
        null=True,
        verbose_name="Meta Keywords",
        help_text="Comma-separated keywords for SEO"
    )
    
    canonical_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Canonical URL",
        help_text="Canonical URL for the website"
    )
    
    robots_txt = models.TextField(
        blank=True,
        null=True,
        verbose_name="Robots.txt Content",
        help_text="Custom robots.txt rules"
    )
    
    sitemap_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Sitemap URL",
        help_text="URL of your sitemap.xml"
    )
    
    # ============ SOCIAL MEDIA ============
    social_links = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Social Media Links",
        help_text='Example: {"facebook": "https://facebook.com/...", "twitter": "https://twitter.com/...", "instagram": "https://instagram.com/...", "youtube": "https://youtube.com/...", "linkedin": "https://linkedin.com/...", "pinterest": "https://pinterest.com/...", "tiktok": "https://tiktok.com/...", "github": "https://github.com/..."}'
    )
    
    social_media_handles = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Social Media Handles",
        help_text='Example: {"twitter": "@username", "instagram": "@username", "facebook": "@username"}'
    )
    
    # ============ OPEN GRAPH (OG) TAGS ============
    og_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="OG Title",
        help_text="Open Graph title (Recommended: 60-90 characters)"
    )
    
    og_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="OG Description",
        help_text="Open Graph description (Recommended: 70-200 characters)"
    )
    
    og_image = models.ImageField(
        upload_to='brand/og-images/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="OG Image",
        help_text="Image for social sharing (Recommended: 1200x630px, Max: 1MB)"
    )
    
    og_image_width = models.PositiveIntegerField(
        default=1200,
        verbose_name="OG Image Width",
        help_text="Width in pixels (e.g., 1200)"
    )
    
    og_image_height = models.PositiveIntegerField(
        default=630,
        verbose_name="OG Image Height",
        help_text="Height in pixels (e.g., 630)"
    )
    
    og_type = models.CharField(
        max_length=50,
        default="website",
        verbose_name="OG Type",
        help_text="Open Graph type (e.g., website, article, product)"
    )
    
    og_site_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="OG Site Name",
        help_text="Site name for Open Graph"
    )
    
    # ============ TWITTER CARDS ============
    twitter_card_type = models.CharField(
        max_length=50,
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary with Large Image'),
            ('app', 'App'),
            ('player', 'Player'),
        ],
        default='summary_large_image',
        verbose_name="Twitter Card Type",
        help_text="Twitter card type"
    )
    
    twitter_site = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Twitter Site",
        help_text="@username of the website (e.g., @example)"
    )
    
    twitter_creator = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Twitter Creator",
        help_text="@username of the content creator (e.g., @creator)"
    )
    
    twitter_image = models.ImageField(
        upload_to='brand/twitter/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Twitter Card Image",
        help_text="Image for Twitter cards (Recommended: 1200x675px)"
    )
    
    twitter_image_width = models.PositiveIntegerField(
        default=1200,
        verbose_name="Twitter Image Width",
        help_text="Width in pixels (e.g., 1200)"
    )
    
    twitter_image_height = models.PositiveIntegerField(
        default=675,
        verbose_name="Twitter Image Height",
        help_text="Height in pixels (e.g., 675)"
    )
    
    # ============ BRAND COLORS ============
    brand_colors = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Brand Colors",
        help_text='Example: {"primary": "#007bff", "secondary": "#6c757d", "accent": "#28a745", "dark": "#343a40", "light": "#f8f9fa"}'
    )
    
    primary_color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Primary Color",
        help_text="HEX color code (e.g., #007bff)"
    )
    
    secondary_color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Secondary Color",
        help_text="HEX color code (e.g., #6c757d)"
    )
    
    accent_color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Accent Color",
        help_text="HEX color code (e.g., #28a745)"
    )
    
    text_color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Text Color",
        help_text="HEX color code (e.g., #333333)"
    )
    
    background_color = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Background Color",
        help_text="HEX color code (e.g., #ffffff)"
    )
    
    # ============ TYPOGRAPHY ============
    primary_font = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Primary Font",
        help_text="Primary font family (e.g., 'Inter', sans-serif)"
    )
    
    secondary_font = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Secondary Font",
        help_text="Secondary font family (e.g., 'Roboto', sans-serif)"
    )
    
    heading_font = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Heading Font",
        help_text="Font for headings (e.g., 'Poppins', sans-serif)"
    )
    
    google_fonts_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Google Fonts URL",
        help_text="Google Fonts import URL"
    )
    
    # ============ BRAND GUIDELINES ============
    brand_guidelines = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Guidelines",
        help_text="Complete brand usage guidelines"
    )
    
    brand_voice = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Voice",
        help_text="Brand voice and tone guidelines"
    )
    
    brand_personality = models.TextField(
        blank=True,
        null=True,
        verbose_name="Brand Personality",
        help_text="Brand personality traits (e.g., Professional, Friendly, Innovative)"
    )
    
    target_audience = models.TextField(
        blank=True,
        null=True,
        verbose_name="Target Audience",
        help_text="Description of target audience"
    )
    
    # ============ OTHER BRAND INFO ============
    copyright_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Copyright Text",
        help_text="Copyright notice text (e.g., '© 2024 Brand Name. All rights reserved.')"
    )
    
    established_year = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1900), MaxValueValidator(2100)],
        verbose_name="Established Year",
        help_text="Year the brand was established"
    )
    
    company_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Company Type",
        help_text="e.g., LLC, Inc, Pvt Ltd, Sole Proprietorship"
    )
    
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Registration Number",
        help_text="Company registration number"
    )
    
    tax_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Tax ID/VAT Number",
        help_text="Tax identification number"
    )
    
    # ============ EMAIL SETTINGS ============
    email_from_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Email From Name",
        help_text="Name to show in email 'From' field"
    )
    
    email_from_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email From Address",
        help_text="Email address to show in 'From' field"
    )
    
    email_reply_to = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email Reply-To",
        help_text="Reply-to email address"
    )
    
    email_footer_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Email Footer Text",
        help_text="Text to appear in all email footers"
    )
    
    # ============ ANALYTICS & TRACKING ============
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Google Analytics ID",
        help_text="e.g., G-XXXXXXXXXX or UA-XXXXXXXX-X"
    )
    
    google_tag_manager_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Google Tag Manager ID",
        help_text="e.g., GTM-XXXXXXX"
    )
    
    facebook_pixel_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Facebook Pixel ID",
        help_text="e.g., 123456789012345"
    )
    
    custom_analytics_code = models.TextField(
        blank=True,
        null=True,
        verbose_name="Custom Analytics Code",
        help_text="Any custom tracking/analytics code"
    )
    
    # ============ SYSTEM FIELDS ============
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Is this brand profile active?"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At"
    )
    
    updated_by = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Updated By",
        help_text="Name of person who last updated"
    )
    
    class Meta:
        verbose_name = "Brand Profile"
        verbose_name_plural = "Brand Profiles"
        ordering = ['-created_at']
        
        constraints = [
            models.UniqueConstraint(
                fields=['is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_brand'
            )
        ]
    
    def __str__(self):
        return f"{self.brand_name} ({'Active' if self.is_active else 'Inactive'})"
    
    def clean(self):
        """Validation before saving"""
        # Validate logo file size
        if self.logo_primary:
            if self.logo_primary.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError("Primary logo file size must be under 2MB")
        
        if self.og_image:
            if self.og_image.size > 1 * 1024 * 1024:  # 1MB
                raise ValidationError("OG image file size must be under 1MB")
        
        # Ensure only one active instance
        if self.is_active:
            active_profiles = BrandProfile.objects.filter(is_active=True)
            if self.pk:
                active_profiles = active_profiles.exclude(pk=self.pk)
            if active_profiles.exists():
                raise ValidationError("Only one active brand profile can exist at a time.")
    
    def save(self, *args, **kwargs):
        """Auto-set SEO fields if not provided"""
        if not self.meta_title and self.brand_name:
            self.meta_title = self.brand_name
            if self.brand_tagline:
                self.meta_title += f" - {self.brand_tagline}"
        
        if not self.meta_description and self.brand_description:
            self.meta_description = self.brand_description[:160]
        
        if not self.og_title and self.meta_title:
            self.og_title = self.meta_title
        
        if not self.og_description and self.meta_description:
            self.og_description = self.meta_description
        
        if not self.og_site_name and self.brand_name:
            self.og_site_name = self.brand_name
        
        super().save(*args, **kwargs)
    
    # ============ PROPERTIES ============
    @property
    def full_name(self):
        """Return full brand name with tagline"""
        if self.brand_tagline:
            return f"{self.brand_name} - {self.brand_tagline}"
        return self.brand_name
    
    @property
    def primary_logo_url(self):
        return self.logo_primary.url if self.logo_primary else None
    
    @property
    def alt_logo_url(self):
        return self.logo_alternative.url if self.logo_alternative else None
    
    @property
    def horizontal_logo_url(self):
        return self.logo_horizontal.url if self.logo_horizontal else None
    
    @property
    def favicon_16_url(self):
        return self.favicon_16x16.url if self.favicon_16x16 else None
    
    @property
    def favicon_32_url(self):
        return self.favicon_32x32.url if self.favicon_32x32 else None
    
    @property
    def og_image_url(self):
        return self.og_image.url if self.og_image else None
    
    @property
    def twitter_image_url(self):
        return self.twitter_image.url if self.twitter_image else None
    
    @property
    def primary_color_hex(self):
        return self.primary_color if self.primary_color else "#000000"
    
    @property
    def color_palette(self):
        """Return complete color palette as dict"""
        return {
            'primary': self.primary_color or '#007bff',
            'secondary': self.secondary_color or '#6c757d',
            'accent': self.accent_color or '#28a745',
            'text': self.text_color or '#333333',
            'background': self.background_color or '#ffffff',
        }
    
    @property
    def font_families(self):
        """Return font families as dict"""
        return {
            'primary': self.primary_font or 'Inter, sans-serif',
            'secondary': self.secondary_font or 'Roboto, sans-serif',
            'heading': self.heading_font or 'Poppins, sans-serif',
        }
    
    # ============ CLASS METHODS ============
    @classmethod
    def get_active_profile(cls):
        """Get the active brand profile"""
        try:
            return cls.objects.get(is_active=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_contact_info(cls):
        """Get contact information"""
        profile = cls.get_active_profile()
        if profile:
            return {
                'email': profile.contact_email,
                'phone': profile.contact_phone,
                'address': profile.address,
                'latitude': profile.address_latitude,
                'longitude': profile.address_longitude,
            }
        return {}
    
    @classmethod
    def get_seo_info(cls):
        """Get SEO information"""
        profile = cls.get_active_profile()
        if profile:
            return {
                'title': profile.meta_title,
                'description': profile.meta_description,
                'keywords': profile.meta_keywords,
                'canonical': profile.canonical_url,
                'robots': profile.robots_txt,
            }
        return {}


# ============ FOOTER MODEL ============
class BrandFooter(models.Model):
    """
    Footer-specific branding information
    """
    brand = models.OneToOneField(
        BrandProfile,
        on_delete=models.CASCADE,
        related_name='footer',
        verbose_name="Brand Profile"
    )
    
    footer_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Footer Text",
        help_text="Text to display in footer"
    )
    
    footer_links = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Footer Links",
        help_text='Example: [{"title": "Privacy Policy", "url": "/privacy"}, {"title": "Terms of Service", "url": "/terms"}, {"title": "Contact", "url": "/contact"}]'
    )
    
    footer_logo = models.ImageField(
        upload_to='brand/footer-logos/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'svg', 'webp']),
        ],
        blank=True,
        null=True,
        verbose_name="Footer Logo",
        help_text="Footer-specific logo (Recommended: 200x50px)"
    )
    
    footer_logo_width = models.PositiveIntegerField(
        default=200,
        verbose_name="Footer Logo Width",
        help_text="Width in pixels (e.g., 200)"
    )
    
    footer_logo_height = models.PositiveIntegerField(
        default=50,
        verbose_name="Footer Logo Height",
        help_text="Height in pixels (e.g., 50)"
    )
    
    show_powered_by = models.BooleanField(
        default=True,
        verbose_name="Show Powered By",
        help_text="Display 'Powered by' text in footer"
    )
    
    powered_by_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Powered By Text",
        help_text="Custom 'Powered by' text"
    )
    
    newsletter_enabled = models.BooleanField(
        default=False,
        verbose_name="Enable Newsletter",
        help_text="Show newsletter subscription in footer"
    )
    
    newsletter_title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Newsletter Title",
        help_text="Title for newsletter section"
    )
    
    newsletter_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Newsletter Description",
        help_text="Description for newsletter section"
    )
    
    social_icons_in_footer = models.BooleanField(
        default=True,
        verbose_name="Show Social Icons in Footer",
        help_text="Display social media icons in footer"
    )
    
    def __str__(self):
        return f"Footer for {self.brand.brand_name}"


class Banner(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
        
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image.url,
            'url': self.url,
            'order': self.order,
        }


class Promotion(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='promotions/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
        
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image.url,
            'url': self.url,
            'order': self.order,
        }


class HomeAd(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='home_ads/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Home Ad'
        verbose_name_plural = 'Home Ads'
        indexes = [
            models.Index(fields=['is_active', 'order']),
        ]
        
    def __str__(self):
        return self.title
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'image_url': self.image.url,
            'url': self.url,
            'order': self.order,
        }


class CurrencySettingsTable(models.Model):
    # Currency choices (truncated for brevity, keep your existing list)
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('AUD', 'Australian Dollar (A$)'),
        ('CAD', 'Canadian Dollar (C$)'),
        ('CHF', 'Swiss Franc (CHF)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('INR', 'Indian Rupee (₹)'),
        ('RUB', 'Russian Ruble (₽)'),
        ('BRL', 'Brazilian Real (R$)'),
        ('ZAR', 'South African Rand (R)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('SEK', 'Swedish Krona (kr)'),
        ('NOK', 'Norwegian Krone (kr)'),
        ('DKK', 'Danish Krone (kr)'),
        ('SGD', 'Singapore Dollar (S$)'),
        ('HKD', 'Hong Kong Dollar (HK$)'),
        ('KRW', 'South Korean Won (₩)'),
        ('MXN', 'Mexican Peso (MX$)'),
        ('TWD', 'New Taiwan Dollar (NT$)'),
        ('THB', 'Thai Baht (฿)'),
        ('MYR', 'Malaysian Ringgit (RM)'),
        ('IDR', 'Indonesian Rupiah (Rp)'),
        ('PHP', 'Philippine Peso (₱)'),
        ('VND', 'Vietnamese Dong (₫)'),
        ('AED', 'UAE Dirham (د.إ)'),
        ('SAR', 'Saudi Riyal (﷼)'),
        ('QAR', 'Qatari Riyal (ر.ق)'),
        ('KWD', 'Kuwaiti Dinar (د.ك)'),
        ('BHD', 'Bahraini Dinar (ب.د)'),
        ('OMR', 'Omani Rial (﷼)'),
        ('EGP', 'Egyptian Pound (E£)'),
        ('NGN', 'Nigerian Naira (₦)'),
        ('KES', 'Kenyan Shilling (KSh)'),
        ('TZS', 'Tanzanian Shilling (TSh)'),
        ('UGX', 'Ugandan Shilling (USh)'),
        ('GHS', 'Ghanaian Cedi (₵)'),
        ('MAD', 'Moroccan Dirham (د.م.)'),
        ('DZD', 'Algerian Dinar (دج)'),
        ('TND', 'Tunisian Dinar (د.ت)'),
        ('XOF', 'West African CFA Franc (CFA)'),
        ('XAF', 'Central African CFA Franc (FCFA)'),
        ('MUR', 'Mauritian Rupee (₨)'),
        ('SCR', 'Seychellois Rupee (₨)'),
        ('PKR', 'Pakistani Rupee (₨)'),
        ('BDT', 'Bangladeshi Taka (৳)'),
        ('LKR', 'Sri Lankan Rupee (Rs)'),
        ('NPR', 'Nepalese Rupee (Rs)'),
        ('MMK', 'Myanmar Kyat (Ks)'),
        ('KHR', 'Cambodian Riel (៛)'),
        ('LAK', 'Lao Kip (₭)'),
        ('BND', 'Brunei Dollar (B$)'),
        ('FJD', 'Fijian Dollar (FJ$)'),
        ('PGK', 'Papua New Guinean Kina (K)'),
        ('SBD', 'Solomon Islands Dollar (SI$)'),
        ('WST', 'Samoan Tala (T)'),
        ('TOP', 'Tongan Paʻanga (T$)'),
        ('VUV', 'Vanuatu Vatu (Vt)'),
        ('NZD', 'New Zealand Dollar (NZ$)'),
        ('ARS', 'Argentine Peso ($)'),
        ('CLP', 'Chilean Peso ($)'),
        ('COP', 'Colombian Peso ($)'),
        ('PEN', 'Peruvian Sol (S/)'),
        ('UYU', 'Uruguayan Peso ($U)'),
        ('PYG', 'Paraguayan Guarani (₲)'),
        ('BOB', 'Bolivian Boliviano (Bs)'),
        ('VEF', 'Venezuelan Bolívar (Bs)'),
        ('GTQ', 'Guatemalan Quetzal (Q)'),
        ('CRC', 'Costa Rican Colón (₡)'),
        ('DOP', 'Dominican Peso (RD$)'),
        ('JMD', 'Jamaican Dollar (J$)'),
        ('TTD', 'Trinidad and Tobago Dollar (TT$)'),
        ('BBD', 'Barbadian Dollar (Bds$)'),
        ('BSD', 'Bahamian Dollar (B$)'),
        ('HTG', 'Haitian Gourde (G)'),
        ('CUP', 'Cuban Peso (₱)'),
        ('ANG', 'Netherlands Antillean Guilder (ƒ)'),
        ('AWG', 'Aruban Florin (ƒ)'),
        ('SRD', 'Surinamese Dollar ($)'),
        ('GYD', 'Guyanese Dollar (G$)'),
        ('LRD', 'Liberian Dollar (L$)'),
        ('SLL', 'Sierra Leonean Leone (Le)'),
        ('BWP', 'Botswana Pula (P)'),
        ('ZMW', 'Zambian Kwacha (ZK)'),
        ('MWK', 'Malawian Kwacha (MK)'),
        ('MZN', 'Mozambican Metical (MT)'),
        ('ETB', 'Ethiopian Birr (Br)'),
        ('SDG', 'Sudanese Pound (SDG)'),
        ('SSP', 'South Sudanese Pound (£)'),
        ('MGA', 'Malagasy Ariary (Ar)'),
        ('KMF', 'Comorian Franc (CF)'),
        ('DJF', 'Djiboutian Franc (Fdj)'),
        ('BIF', 'Burundian Franc (FBu)'),
        ('RWF', 'Rwandan Franc (FRw)'),
        ('CDF', 'Congolese Franc (FC)'),
        ('AOA', 'Angolan Kwanza (Kz)'),
        ('MOP', 'Macanese Pataca (P)'),
        ('MVR', 'Maldivian Rufiyaa (Rf)'),
        ('KZT', 'Kazakhstani Tenge (₸)'),
        ('UZS', 'Uzbekistani Soʻm (soʻm)'),
        ('TJS', 'Tajikistani Somoni (ЅM)'),
        ('KGS', 'Kyrgyzstani Som (сом)'),
        ('AFN', 'Afghan Afghani (؋)'),
        ('IRR', 'Iranian Rial (﷼)'),
        ('IQD', 'Iraqi Dinar (ع.د)'),
        ('SYP', 'Syrian Pound (£S)'),
        ('LBP', 'Lebanese Pound (ل.ل)'),
        ('JOD', 'Jordanian Dinar (د.ا)'),
        ('ILS', 'Israeli New Shekel (₪)'),
        ('TRY', 'Turkish Lira (₺)'),
        ('AZN', 'Azerbaijani Manat (₼)'),
        ('GEL', 'Georgian Lari (₾)'),
        ('AMD', 'Armenian Dram (֏)'),
    ]
    
    currency_code = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        unique=True,
        verbose_name='Currency Code'
    )
    
    currency_symbol = models.CharField(
        max_length=5,
        default='$',
        verbose_name='Currency Symbol'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Currency'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Currency Setting'
        verbose_name_plural = 'Currency Settings'
        ordering = ['currency_code']
    
    def __str__(self):
        return f"{self.currency_code} ({self.currency_symbol})"
    
    def clean(self):
        if self.is_active:
            active_currencies = CurrencySettingsTable.objects.filter(is_active=True)
            if self.pk:
                active_currencies = active_currencies.exclude(pk=self.pk)
            if active_currencies.exists():
                raise ValidationError('Only one currency can be active at a time.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_currency(cls):
        """Get active currency with caching"""
        try:
            return cls.objects.filter(is_active=True).first()
        except:
            return None




from django.db import models
from django.core.validators import MinValueValidator

class SiteFeature(models.Model):
    ICON_CHOICES = [
        ('icon-rocket', 'Rocket'),
        ('icon-sync', 'Sync'),
        ('icon-credit-card', 'Credit Card'),
        ('icon-bubbles', 'Bubbles'),
        ('icon-gift', 'Gift'),
        ('icon-truck', 'Truck'),
        ('icon-clock', 'Clock'),
        ('icon-heart', 'Heart'),
        ('icon-star', 'Star'),
        ('icon-cart', 'Cart'),
        ('icon-user', 'User'),
        ('icon-lock', 'Lock'),
    ]
    
    title = models.CharField(max_length=100, help_text="Feature title (e.g., Free Delivery)")
    description = models.TextField(max_length=200, help_text="Feature description")
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='icon-rocket')
    
    # For free delivery special case
    min_order_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum order amount for free delivery (only for Free Delivery feature)"
    )
    
    # For return days special case
    return_days = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Number of return days (only for Return feature)"
    )
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'Site Feature'
        verbose_name_plural = 'Site Features'
    
    def __str__(self):
        return self.title
    
    def get_display_description(self):
        """Process description with dynamic values"""
        if self.title.lower() == 'free delivery' and self.min_order_amount:
            return f"For all orders over {self.min_order_amount}"
        elif 'return' in self.title.lower() and self.return_days:
            return f"If goods have problems within {self.return_days} days"
        return self.description