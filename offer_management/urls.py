from django.urls import path
from . import views

app_name = 'offer_management'

urlpatterns = [
    path('apply-promo/', views.apply_promo_code, name='apply_promo'),
    path('remove-promo/', views.remove_promo_code, name='remove_promo'),
    path('validate-promo/', views.validate_promo_code, name='validate_promo'),
]