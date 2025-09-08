from django.urls import path
from django.views.generic import TemplateView
from products import views as product_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),
]