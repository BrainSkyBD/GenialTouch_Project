# models.py
from django.db import models
from django.utils.text import slugify

class Banner(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='banners/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title

class Promotion(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='promotions/')
    url = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.title

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
        
    def __str__(self):
        return self.title