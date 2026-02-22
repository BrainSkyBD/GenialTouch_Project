from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from products.models import Product, ProductVariation
from orders.models import Country, District

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )
    
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(blank=True)
    
    # Discount configuration
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_purchase_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Minimum cart subtotal required to use this code"
    )
    maximum_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Maximum discount amount (for percentage discounts)"
    )
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(
        default=1,
        help_text="Total number of times this code can be used"
    )
    per_user_limit = models.PositiveIntegerField(
        default=1,
        help_text="Number of times a single user can use this code"
    )
    used_count = models.PositiveIntegerField(default=0)
    
    # Validity period
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Restrictions
    applies_to_all_products = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, blank=True)
    
    # Geographic restrictions
    applies_to_all_countries = models.BooleanField(default=True)
    countries = models.ManyToManyField(Country, blank=True)
    
    # User group restrictions (if you have user groups/roles)
    applies_to_all_users = models.BooleanField(default=True)
    # users = models.ManyToManyField(User, blank=True)  # Uncomment if needed
    
    # First time order only
    first_order_only = models.BooleanField(
        default=False,
        help_text="Can only be used on user's first order"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}: {self.discount_value}"
    
    @property
    def is_valid(self):
        """Check if promo code is currently valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to and
            self.used_count < self.usage_limit
        )
    
    def calculate_discount(self, subtotal, user=None, products=None):
        """
        Calculate discount amount for given subtotal
        Returns discount_amount and is_valid boolean with message
        """
        # Check if code is active and within validity period
        if not self.is_valid:
            if not self.is_active:
                return 0, False, "This promo code is not active"
            if self.used_count >= self.usage_limit:
                return 0, False, "This promo code has reached its usage limit"
            now = timezone.now()
            if now < self.valid_from:
                return 0, False, f"This promo code is not valid yet. It starts on {self.valid_from.strftime('%Y-%m-%d')}"
            if now > self.valid_to:
                return 0, False, f"This promo code expired on {self.valid_to.strftime('%Y-%m-%d')}"
            return 0, False, "This promo code is not valid"
        
        # Check minimum purchase amount
        if subtotal < self.minimum_purchase_amount:
            return 0, False, f"Minimum purchase amount of {self.minimum_purchase_amount} required to use this code"
        
        # Check first order only
        if self.first_order_only and user and user.is_authenticated:
            from orders.models import Order
            if Order.objects.filter(user=user).exists():
                return 0, False, "This promo code is only valid for first-time orders"
        
        # Check per-user limit
        if user and user.is_authenticated:
            from .models import PromoCodeUsage
            usage_count = PromoCodeUsage.objects.filter(
                promo_code=self,
                user=user
            ).count()
            if usage_count >= self.per_user_limit:
                return 0, False, f"You have already used this promo code {usage_count} time(s)"
        
        # Calculate discount based on type
        if self.discount_type == 'percentage':
            discount = (subtotal * self.discount_value) / 100
            if self.maximum_discount_amount:
                discount = min(discount, self.maximum_discount_amount)
        else:  # fixed amount
            discount = self.discount_value
            # Ensure discount doesn't exceed subtotal
            discount = min(discount, subtotal)
        
        return discount, True, f"Promo code applied! You saved {discount}"


class PromoCodeUsage(models.Model):
    """Track promo code usage"""
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['promo_code', 'order']
        ordering = ['-used_at']
    
    def __str__(self):
        return f"{self.promo_code.code} - Order: {self.order.order_number}"