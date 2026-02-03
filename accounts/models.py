from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    is_customer = models.BooleanField(default=True)
    phone_number = PhoneNumberField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
    
    
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wishlist = models.ManyToManyField('products.Product', blank=True)
    newsletter_subscription = models.BooleanField(default=False)
    preferred_payment_method = models.CharField(max_length=50, blank=True)
    preferred_shipping_method = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

        