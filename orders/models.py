from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from accounts.models import User
from products.models import Product, ProductVariation
import uuid

from django.core.validators import MinValueValidator, MaxValueValidator


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
        ('shipped', 'Shipped'),
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

    # birth_date = models.DateField(null=True, blank=True, help_text="Customer's birth date (optional)")
    # birth_month = models.CharField(
    #     max_length=20, 
    #     null=True, 
    #     blank=True,
    #     help_text="Birth month name (e.g., January, February)"
    # )

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


    
    def __str__(self):
        return self.order_number
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
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


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=Order.ORDER_STATUS)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status}"


@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        instance.order_number = uuid.uuid4().hex[:10].upper()

@receiver(post_save, sender=Order)
def create_initial_tracking(sender, instance, created, **kwargs):
    if created:
        OrderTracking.objects.create(order=instance, status=instance.status)