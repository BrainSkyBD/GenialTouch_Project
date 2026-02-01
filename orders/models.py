from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import User
from products.models import Product, ProductVariation
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class District(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.country.name}"


class Thana(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}, {self.district.name}"


class TaxConfiguration(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # 10.00 for 10%
    is_active = models.BooleanField(default=True)
    applies_to_all = models.BooleanField(default=True)
    countries = models.ManyToManyField('Country', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"


class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='payment_methods/', blank=True, null=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('confirmed', 'Confirmed'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    full_address = models.TextField()  # Changed from address_line1, address_line2
    
    birth_date = models.PositiveSmallIntegerField(
        null=True, 
        blank=True,
        help_text="Birth date (1-31)",
        validators=[MinValueValidator(1), MaxValueValidator(31)]
    )
    birth_month = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        choices=[
            ('January', 'January'),
            ('February', 'February'),
            ('March', 'March'),
            ('April', 'April'),
            ('May', 'May'),
            ('June', 'June'),
            ('July', 'July'),
            ('August', 'August'),
            ('September', 'September'),
            ('October', 'October'),
            ('November', 'November'),
            ('December', 'December'),
        ],
        help_text="Birth month name"
    )

    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True)
    thana = models.ForeignKey(Thana, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    postal_code = models.CharField(max_length=20, blank=True)  # Made optional
    order_note = models.TextField(blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    ip_address = models.CharField(max_length=50, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_details = models.JSONField(blank=True, null=True)  # For storing payment-specific data

    # Tracking fields
    status_updated_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_date = models.DateField(null=True, blank=True)
    carrier = models.CharField(max_length=100, blank=True, null=True)
    
    # Status timestamps
    pending_at = models.DateTimeField(null=True, blank=True)
    processing_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    packed_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)


    
    def __str__(self):
        return self.order_number
    
    
    def get_full_address(self):
        address_parts = []
        if self.full_address:
            address_parts.append(self.full_address)
        if self.thana:
            address_parts.append(self.thana.name)
        if self.district:
            address_parts.append(self.district.name)
        if self.country:
            address_parts.append(self.country.name)
        if self.postal_code:
            address_parts.append(f"Postal Code: {self.postal_code}")
        return ", ".join(address_parts)

    @property
    def birth_info(self):
        if self.birth_date and self.birth_month:
            return f"{self.birth_date} {self.birth_month}"
        elif self.birth_month:
            return self.birth_month
        elif self.birth_date:
            return str(self.birth_date)
        return ""

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_simplified_address(self):
        """Return just the full address without country/district details"""
        return self.full_address


@receiver(pre_save, sender=Order)
def update_status_timestamps(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            if old_order.status != instance.status:
                # Update status timestamp field
                status_field = f"{instance.status}_at"
                if hasattr(instance, status_field):
                    setattr(instance, status_field, timezone.now())
                
                # Update general status updated_at
                instance.status_updated_at = timezone.now()
                
                # Create tracking history record
                OrderTrackingTableNew.objects.create(
                    order=instance,
                    status=instance.status,
                    note=f"Status changed from {old_order.status} to {instance.status}",
                    updated_by='System'
                )
        except Order.DoesNotExist:
            pass

@receiver(post_save, sender=Order)
def create_initial_status(sender, instance, created, **kwargs):
    if created:
        # Set initial timestamps
        instance.pending_at = instance.created_at
        instance.status_updated_at = instance.created_at
        instance.save()
        
        # Create initial tracking record
        OrderTrackingTableNew.objects.create(
            order=instance,
            status='pending',
            note='Order created successfully',
            updated_by='System'
        )

class OrderTrackingTableNew(models.Model):
    TRACKING_STATUS = Order.ORDER_STATUS
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=20, choices=TRACKING_STATUS)
    note = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True, null=True, default=None)
    updated_by = models.CharField(max_length=100, blank=True, null=True, default='System')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Tracking'



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(ProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
    
    def get_total(self):
        try:
            price_x_qty = self.price * self.quantity
        except Exception as exc:
            print(exc)
            price_x_qty = None
        return price_x_qty

