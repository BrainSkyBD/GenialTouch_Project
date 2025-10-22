from django.contrib import admin

# Register your models here.
from .models import User, CustomerProfile

admin.site.register(User)
admin.site.register(CustomerProfile)