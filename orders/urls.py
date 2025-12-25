from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('order/<str:order_id>/', views.order_detail, name='order_detail'),
    path('history/', views.order_history, name='order_history'),
    path('cancel/<str:order_id>/', views.cancel_order, name='cancel_order'),

    path('buy-now/',  views.process_buy_now, name='process_buy_now'),
    path('order-confirmation/<str:order_number>/',  views.order_confirmation, name='order_confirmation'),

    # path('get_states/', views.get_states, name='get_states'),
    # path('get_cities/', views.get_cities, name='get_cities'),

    path('get_districts/', views.get_districts, name='get_districts'),
    path('get_thanas/', views.get_thanas, name='get_thanas'),

    path('get_shipping_cost/', views.get_shipping_cost, name='get_shipping_cost'),


    path('calculate_tax/', views.calculate_tax, name='calculate_tax'),


]