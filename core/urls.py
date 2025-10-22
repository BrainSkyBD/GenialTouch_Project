from django.urls import path
from django.views.generic import TemplateView
from products import views as product_views
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', TemplateView.as_view(template_name='core/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='core/contact.html'), name='contact'),

    #policies
    path('return-and-refund_policy/', views.return_and_refund_policy, name='return_and_refund_policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
    path('Replacement-Policy/', views.Replacement_Policy, name='Replacement_Policy'),
]