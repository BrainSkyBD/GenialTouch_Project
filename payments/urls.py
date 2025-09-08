from django.urls import path
from . import views

urlpatterns = [
    path('process/<str:order_id>/', views.process_payment, name='process_payment'),
    path('success/<str:order_id>/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<str:order_id>/<int:payment_id>/', views.payment_failed, name='payment_failed'),
]