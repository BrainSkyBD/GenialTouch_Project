from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem, OrderTrackingTableNew
from products.models import Product, ProductVariation
from accounts.models import CustomerProfile
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product, ProductVariation
from .models import Order, OrderItem
import uuid
from decimal import Decimal
from django.urls import reverse
from cart.views import get_cart_context
from django.core.validators import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from products.models import Product, ProductVariation
from .models import Order, OrderItem, Country, District, TaxConfiguration
from django.db.models import Q
from django.http import JsonResponse
from .models import Country, PaymentMethod

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal
from .models import Country, District, Thana, PaymentMethod, Order, OrderItem, TaxConfiguration
from products.models import Product, ProductVariation

from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.db.models import Q
from decimal import Decimal
import uuid
import random
import string
from django.utils import timezone
from django.urls import reverse

from .models import Order, OrderItem, Country, District, Thana, PaymentMethod, TaxConfiguration
from products.models import Product, ProductVariation
from cart.views import get_cart_context
import uuid

from django.http import JsonResponse
from .models import Country, District, Thana

from django.http import HttpResponse
from django.template.loader import render_to_string

from datetime import datetime
import requests
from io import BytesIO
import base64

# In views.py - add these views
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
import base64
import requests
from weasyprint import HTML
import tempfile
import os

import random
import string
from django.utils import timezone
from core.email_send_views import send_email_function
from .utils.email_utils import notify_both_new_order
from django.conf import settings


def generate_order_number():
    """Generate a unique order number"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f'ORD-{timestamp}-{random_str}'

def get_districts(request):
    country_id = request.GET.get('country_id')
    if country_id:
        districts = District.objects.filter(country_id=country_id, is_active=True).order_by('name')
        data = [{'id': d.id, 'name': d.name, 'shipping_cost': str(d.shipping_cost)} for d in districts]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)


def get_thanas(request):
    district_id = request.GET.get('district_id')
    if district_id:
        thanas = Thana.objects.filter(district_id=district_id, is_active=True).order_by('name')
        data = [{'id': t.id, 'name': t.name} for t in thanas]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

def get_shipping_cost(request):
    city_id = request.GET.get('city_id')
    try:
        city = City.objects.get(id=city_id)
        return JsonResponse({'shipping_cost': str(city.shipping_cost)})
    except City.DoesNotExist:
        return JsonResponse({'shipping_cost': '0'})

def calculate_tax(request):
    """AJAX endpoint to calculate tax"""
    country_id = request.GET.get('country_id')
    district_id = request.GET.get('district_id')
    subtotal = Decimal(request.GET.get('subtotal', 0))
    shipping = Decimal(request.GET.get('shipping', 0))
    
    try:
        country = Country.objects.get(id=country_id)
        district = District.objects.get(id=district_id)
        
        tax_config = TaxConfiguration.objects.filter(
            is_active=True,
        ).filter(
            Q(applies_to_all=True) | 
            Q(countries=country)
        ).first()
        
        tax_rate = tax_config.rate if tax_config else Decimal('0')
        tax_amount = (subtotal + shipping) * (tax_rate / 100)
        grand_total = subtotal + shipping + tax_amount
        
        return JsonResponse({
            'status': 'success',
            'tax_rate': str(tax_rate),
            'tax_name': tax_config.name if tax_config else 'Tax',
            'tax_amount': str(tax_amount.quantize(Decimal('0.01'))),
            'grand_total': str(grand_total.quantize(Decimal('0.01'))),
            'shipping_cost': str(district.shipping_cost)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        })



def generate_order_number():
    """Generate a unique order number"""
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f'ORD-{timestamp}-{random_str}'



@require_POST
def process_buy_now(request):
    print('check buy now function...')
    try:
        # Get product and quantity
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(id=product_id)
        
        # Get selected variations
        variation_attributes = {}
        for key, value in request.POST.items():
            if key.startswith('attribute_'):
                attr_name = key.replace('attribute_', '')
                variation_attributes[attr_name] = value
        
        # Find the matching variation
        variation = None
        if variation_attributes:
            variations = product.variations.all()
            for v in variations:
                if all(attr.value == variation_attributes.get(attr.attribute.name.lower().replace(' ', '_')) 
                       for attr in v.attributes.all()):
                    variation = v
                    break
        
        # Calculate price
        price = variation.get_price() if variation else product.get_price()
        total_price = price * quantity

        # Get payment method
        get_payment_method_value = request.POST.get('payment_method')
        get_payment_method_row = None
        if get_payment_method_value:
            get_payment_method_row = PaymentMethod.objects.get(id=get_payment_method_value, is_active=True)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Payment method is required'
            }, status=400)

        # Get simplified form data
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        full_address = request.POST.get('full_address')

        # Validate required fields
        required_fields = {
            'Full Name': full_name,
            'Phone Number': phone_number,
            'Full Address': full_address,
        }
        
        for field, value in required_fields.items():
            if not value:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field} is required'
                }, status=400)

        # If email is not provided, set to None
        if not email:
            email = None

        # Split full name into first and last name (optional)
        first_name = full_name
        last_name = ""
        name_parts = full_name.strip().split(' ', 1)
        if len(name_parts) > 1:
            first_name = name_parts[0]
            last_name = name_parts[1]

        # Set default values for removed fields
        default_country = Country.objects.filter(name='Bangladesh').first()
        default_district = None
        if default_country:
            default_district = District.objects.filter(country=default_country).first()

        # Calculate shipping cost (use default district's shipping cost or 0)
        shipping_cost = default_district.shipping_cost if default_district else Decimal('0')
        
        # Calculate tax (simplified - you might want to adjust this)
        tax_rate = Decimal('0')  # Default 0% tax
        tax_amount = Decimal('0')
        
        # If you have a default tax configuration
        tax_config = TaxConfiguration.objects.filter(is_active=True).first()
        if tax_config:
            tax_rate = tax_config.rate
            tax_amount = (total_price + shipping_cost) * (tax_rate / 100)
        
        grand_total = total_price + shipping_cost + tax_amount

        # Create order with simplified data
        order = Order(
            order_number=uuid.uuid4().hex[:10].upper(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            full_address=full_address,
            
            # Set removed fields to None
            birth_date=None,
            birth_month=None,
            country=default_country,
            district=default_district,
            thana=None,
            postal_code="",
            order_note="",
            
            order_total=total_price,
            shipping_cost=shipping_cost,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            grand_total=grand_total,
            status='pending',
            ip_address=request.META.get('REMOTE_ADDR'),
            is_ordered=True,
            payment_method=get_payment_method_row,
        )
        
        if request.user.is_authenticated:
            order.user = request.user
        
        order.save()
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            variation=variation,
            quantity=quantity,
            price=price
        )


        try:
            # Send notifications to both customer and admins
            notify_both_new_order(order)
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            # You might want to log this to a database table for retry

        
        

        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('order_confirmation', args=[order.order_number])
        })
        
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Product not found'
        }, status=404)
    except PaymentMethod.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid payment method'
        }, status=400)
    except Exception as e:
        import traceback
        print(f"Error in process_buy_now: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)


# def order_confirmation(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number)
#         context = {
#             'order': order,
#         }
#         return render(request, 'orders/order_confirmation.html', context)
#     except Order.DoesNotExist:
#         raise Http404("Order not found")


# def order_confirmation(request, order_number):
#     try:
#         order = Order.objects.get(order_number=order_number)
        
#         # Check if GA4 event should be fired
#         fire_ga4_event = False
#         if not order.ga4_tracked:
#             fire_ga4_event = True
#             # Mark as tracked immediately to prevent duplicate on refresh
#             order.ga4_tracked = True
#             order.save(update_fields=['ga4_tracked'])
        
#         context = {
#             'order': order,
#             'fire_ga4_event': fire_ga4_event,  # Pass to template
#         }
#         return render(request, 'orders/order_confirmation.html', context)
#     except Order.DoesNotExist:
#         raise Http404("Order not found")




def order_confirmation(request, order_number):
    try:
        # Optimize with prefetch_related to reduce database queries
        order = Order.objects.prefetch_related(
            'items__product__brand',
            'items__product__categories',
            'items__product__images',  # For product images
            'items__variation__attributes__attribute'  # Deep prefetch for attributes
        ).get(order_number=order_number)
        
        # Check if GA4 event should be fired
        fire_ga4_event = False
        if not order.ga4_tracked:
            fire_ga4_event = True
            # Mark as tracked immediately to prevent duplicate on refresh
            order.ga4_tracked = True
            order.save(update_fields=['ga4_tracked'])
        
        # Prepare JSON data for GA4 items (optional but cleaner)
        order_items_json = []
        for item in order.items.all():
            item_data = {
                'id': str(item.product.id),
                'item_id': str(item.product.id),
                'item_name': item.product.name,
                'item_brand': item.product.brand.name if item.product.brand else 'GenialTouch',
                'item_category': item.product.categories.first().name if item.product.categories.first() else 'Uncategorized',
                'price': float(item.price),
                'quantity': item.quantity,
                'currency': 'BDT',
            }
            
            # Add variation data if exists
            if item.variation:
                item_data.update({
                    'item_variant': item.variation.get_variation_name(),
                    'item_variant_id': item.variation.id,
                    'attribute_ids': item.variation.get_attribute_ids(),
                    'attribute_ids_string': item.variation.get_attribute_ids_string(),
                    'attribute_data': item.variation.get_attribute_data(),
                })
            
            order_items_json.append(item_data)
        
        context = {
            'order': order,
            'fire_ga4_event': fire_ga4_event,
            'order_items_json': json.dumps(order_items_json),  # Pass as JSON string
        }
        
        return render(request, 'orders/order_confirmation.html', context)
        
    except Order.DoesNotExist:
        raise Http404("Order not found")

def checkout(request):
    if request.method == 'POST':
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        full_address = request.POST.get('full_address')
        country_id = request.POST.get('country')
        district_id = request.POST.get('district')
        thana_id = request.POST.get('thana')
        postal_code = request.POST.get('postal_code', '')
        order_note = request.POST.get('order_note', '')
        payment_method_id = request.POST.get('payment_method')
        
        # Get birth date and month (optional)
        birth_date = request.POST.get('birth_date', '')
        birth_month = request.POST.get('birth_month', '')
        
        # Validate birth date if provided
        if birth_date:
            try:
                birth_date_int = int(birth_date)
                if not (1 <= birth_date_int <= 31):
                    if is_ajax:
                        return JsonResponse({
                            'status': 'error',
                            'message': "Birth date must be between 1 and 31"
                        }, status=400)
                    messages.error(request, "Birth date must be between 1 and 31")
                    return redirect('checkout')
            except (ValueError, TypeError):
                birth_date = None
        
        # Validate birth month if provided
        if birth_month and birth_month not in [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': "Invalid birth month selected"
                }, status=400)
            messages.error(request, "Invalid birth month selected")
            return redirect('checkout')
        
        # Validate required fields
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Phone Number': phone_number,
            'Full Address': full_address,
            'Country': country_id,
            'District': district_id,
            'Payment Method': payment_method_id
        }
        
        for field, value in required_fields.items():
            if not value:
                if is_ajax:
                    return JsonResponse({
                        'status': 'error',
                        'message': f"{field} is required"
                    }, status=400)
                messages.error(request, f"{field} is required")
                return redirect('checkout')
        
        try:
            country = Country.objects.get(id=country_id)
            district = District.objects.get(id=district_id)
            thana = None
            if thana_id:
                thana = Thana.objects.get(id=thana_id, district=district)
            payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
        except (Country.DoesNotExist, District.DoesNotExist, 
                Thana.DoesNotExist, PaymentMethod.DoesNotExist) as e:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': "Invalid selection"
                }, status=400)
            messages.error(request, "Invalid selection")
            return redirect('checkout')
        
        # Get cart data
        cart = request.session.get('cart', {})
        if not cart:
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': "Your cart is empty"
                }, status=400)
            messages.error(request, "Your cart is empty")
            return redirect('cart_detail')
        
        # Calculate totals
        cart_context = get_cart_context(request)
        cart_total = cart_context['cart_total']
        shipping_cost = district.shipping_cost
        
        # Validate promo code if applied
        promo_code_id = request.session.get('applied_promo_code')
        promo_discount = request.session.get('promo_discount', 0)
        
        # Convert promo_discount to Decimal if it's a float
        if isinstance(promo_discount, float):
            promo_discount = Decimal(str(promo_discount))
        else:
            promo_discount = Decimal(promo_discount)
        
        if promo_code_id:
            from offer_management.models import PromoCode
            try:
                promo_code = PromoCode.objects.get(id=promo_code_id)
                user = request.user if request.user.is_authenticated else None
                
                # Re-validate the promo code with current cart total
                discount_amount, is_valid, message = promo_code.calculate_discount(
                    cart_total, 
                    user=user
                )
                
                if not is_valid:
                    # Clear invalid promo from session
                    if 'applied_promo_code' in request.session:
                        del request.session['applied_promo_code']
                    if 'promo_discount' in request.session:
                        del request.session['promo_discount']
                    
                    if is_ajax:
                        return JsonResponse({
                            'status': 'error',
                            'message': f"Promo code removed: {message}"
                        }, status=400)
                    
                    messages.warning(request, f"Promo code removed: {message}")
                    promo_code_id = None
                    promo_discount = Decimal('0')
                elif discount_amount != promo_discount:
                    # Update discount if it changed
                    promo_discount = discount_amount
                    request.session['promo_discount'] = float(discount_amount)
                    
            except PromoCode.DoesNotExist:
                # Clear invalid promo from session
                if 'applied_promo_code' in request.session:
                    del request.session['applied_promo_code']
                if 'promo_discount' in request.session:
                    del request.session['promo_discount']
                promo_code_id = None
                promo_discount = Decimal('0')
        
        # Calculate tax
        tax_config = TaxConfiguration.objects.filter(
            is_active=True,
        ).filter(
            Q(applies_to_all=True) | 
            Q(countries=country)
        ).first()
        
        tax_rate = tax_config.rate if tax_config else Decimal('0')
        tax_amount = (cart_total + shipping_cost - promo_discount) * (tax_rate / 100)
        grand_total = cart_total + shipping_cost + tax_amount - promo_discount
        
        # Create the order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            order_number=generate_order_number(),
            first_name=first_name,
            last_name=last_name,
            email=email if email else (request.user.email if request.user.is_authenticated else None),
            phone_number=phone_number,
            full_address=full_address,
            birth_date=birth_date if birth_date else None,
            birth_month=birth_month if birth_month else None,
            country=country,
            district=district,
            thana=thana,
            postal_code=postal_code,
            order_note=order_note,
            order_total=cart_total,
            shipping_cost=shipping_cost,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            promo_discount=promo_discount,
            grand_total=grand_total,
            payment_method=payment_method,
            status='pending',
            ip_address=request.META.get('REMOTE_ADDR'),
            promo_code_id=promo_code_id if promo_code_id else None,
        )
        
        # Prepare order items data for GA4 tracking
        order_items_data = []
        
        # Create order items and prepare tracking data
        for cart_key, item_data in cart.items():
            product_id = int(cart_key.split('-')[0])
            product = Product.objects.get(id=product_id)
            variation = None
            variation_name = None
            
            if 'variation_id' in item_data:
                variation = ProductVariation.objects.get(id=item_data['variation_id'])
                variation_name = variation.get_variation_name()
            
            OrderItem.objects.create(
                order=order,
                product=product,
                variation=variation,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            
            # Prepare item data for GA4 tracking
            item_data_tracking = {
                'item_id': str(product.id),
                'item_name': product.name,
                'item_brand': product.brand.name if product.brand else 'GenialTouch',
                'item_category': product.categories.first().name if product.categories.exists() else 'Uncategorized',
                'price': float(item_data['price']),
                'quantity': item_data['quantity'],
                'currency': 'BDT'
            }
            
            if variation_name:
                item_data_tracking['item_variant'] = variation_name
                
            order_items_data.append(item_data_tracking)
        
        # Record promo code usage if applied
        if promo_code_id:
            from offer_management.models import PromoCode, PromoCodeUsage
            promo_code = PromoCode.objects.get(id=promo_code_id)
            PromoCodeUsage.objects.create(
                promo_code=promo_code,
                order=order,
                user=request.user if request.user.is_authenticated else None,
                discount_amount=promo_discount
            )
            promo_code.used_count += 1
            promo_code.save()
            
            # Clear promo code from session
            if 'applied_promo_code' in request.session:
                del request.session['applied_promo_code']
            if 'promo_discount' in request.session:
                del request.session['promo_discount']
        

        try:
            # Send notifications to both customer and admins
            notify_both_new_order(order)
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            # You might want to log this to a database table for retry

            
        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True
        
        # Prepare tracking data for GA4
        tracking_data = {
            'order_number': order.order_number,
            'grand_total': float(grand_total),
            'shipping_cost': float(shipping_cost),
            'tax_amount': float(tax_amount),
            'order_total': float(cart_total),
            'promo_discount': float(promo_discount),
            'promo_code': promo_code.code if promo_code_id and 'promo_code' in locals() else None,
            'payment_method': payment_method.name,
            'items': order_items_data
        }
        
        # if is_ajax:
        #     # Return JSON response for AJAX checkout
        #     return JsonResponse({
        #         'status': 'success',
        #         'message': f"Order #{order.order_number} placed successfully!",
        #         'order_number': order.order_number,
        #         'redirect_url': reverse('order_confirmation', args=[order.order_number]),
        #         'tracking_data': tracking_data  # Include tracking data for GA4
        #     })
        
        if is_ajax:
            return JsonResponse({
                'status': 'success',
                'message': f"Order #{order.order_number} placed successfully!",
                'order_number': order.order_number,
                'redirect_url': reverse('order_confirmation', args=[order.order_number]),
                'tracking_data': tracking_data,
                'debug_info': {
                    'order_created_at': order.created_at.isoformat(),
                    'grand_total': float(order.grand_total),
                } if settings.DEBUG else None  # Only in debug mode
            })
        
        # Regular form submission
        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect('order_confirmation', order_number=order.order_number)
    
        # GET request - show checkout form
    cart_context = get_cart_context(request)
    if not cart_context['cart_items']:
        messages.warning(request, "Your cart is empty")
        return redirect('cart_detail')
    
    # Check if promo code is applied in session
    applied_promo = None
    promo_discount = Decimal('0')
    
    if request.session.get('applied_promo_code'):
        from offer_management.models import PromoCode
        try:
            applied_promo = PromoCode.objects.get(
                id=request.session['applied_promo_code']
            )
            # Convert promo_discount from session to Decimal
            session_discount = request.session.get('promo_discount', 0)
            if isinstance(session_discount, float):
                promo_discount = Decimal(str(session_discount))
            else:
                promo_discount = Decimal(session_discount)
        except PromoCode.DoesNotExist:
            # Clear invalid promo from session
            if 'applied_promo_code' in request.session:
                del request.session['applied_promo_code']
            if 'promo_discount' in request.session:
                del request.session['promo_discount']
    
    # Pre-fill form with user data if available
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name or '',
            'last_name': request.user.last_name or '',
            'email': request.user.email,
            'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
        }
    
    # Calculate cart total with promo discount for display
    # Both are now Decimal objects
    display_cart_total = cart_context['cart_total'] - promo_discount
    
    context = {
        'countries': Country.objects.filter(is_active=True).order_by('name'),
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'cart_items': cart_context['cart_items'],
        'cart_total': cart_context['cart_total'],
        'display_cart_total': display_cart_total,
        'cart_item_count': cart_context['cart_item_count'],
        'initial_data': initial_data,
        'days_range': range(1, 32),
        'applied_promo': applied_promo,
        'promo_discount': promo_discount,
        'currency_symbol': '৳',  # Add your currency symbol
    }
    return render(request, 'orders/checkout.html', context)




@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    
    if order.status not in ['delivered', 'cancelled', 'refunded']:
        order.status = 'cancelled'
        order.save()
        OrderTrackingTableNew.objects.create(order=order, status='cancelled', note='Order cancelled by customer')
        messages.success(request, 'Your order has been cancelled')
    else:
        messages.error(request, 'This order cannot be cancelled')
    
    return redirect('order_detail', order_id=order_id)









def download_simple_invoice(request, order_number):
    """Customer-facing invoice download"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Optional: Check if user owns this order (if logged in)
    if request.user.is_authenticated and order.user != request.user:
        raise Http404("Order not found")
    
    pdf_data = generate_pdf_invoice(order, is_admin=False)
    
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
        return response
    else:
        return HttpResponse(
            f"""
            Invoice #{order.order_number}
            Date: {order.created_at.strftime('%B %d, %Y')}
            Customer: {order.get_full_name()}
            Total: ${order.grand_total}
            Status: {order.get_status_display()}
            """,
            content_type='text/plain'
        )


def track_order(request):
    """Track order page"""
    order = None
    tracking_data = None
    order_number = request.GET.get('order_number', '').strip()
    
    if order_number:
        try:
            order = Order.objects.get(order_number=order_number)
            tracking_data = order.tracking_history.all().order_by('created_at')
            
            # Calculate estimated delivery if not set
            if not order.estimated_delivery_date and order.shipped_at:
                order.estimated_delivery_date = order.shipped_at + timedelta(days=3)
                order.save()
                
        except Order.DoesNotExist:
            messages.error(request, f"No order found with number: {order_number}")
    
    context = {
        'order': order,
        'tracking_data': tracking_data,
        'order_number': order_number,
    }
    return render(request, 'orders/track_order.html', context)


def track_order_by_number(request, order_number):
    """Direct tracking by order number in URL"""
    try:
        order = Order.objects.get(order_number=order_number)
        tracking_data = order.tracking_history.all().order_by('created_at')
        
        context = {
            'order': order,
            'tracking_data': tracking_data,
            'order_number': order_number,
        }
        return render(request, 'orders/track_order.html', context)
        
    except Order.DoesNotExist:
        messages.error(request, f"No order found with number: {order_number}")
        return redirect('track_order')


def order_tracking_api(request, order_number):
    """API endpoint for AJAX tracking"""
    try:
        order = Order.objects.get(order_number=order_number)
        tracking_data = order.tracking_history.all().order_by('created_at')
        
        # Serialize data
        data = {
            'success': True,
            'order': {
                'order_number': order.order_number,
                'status': order.get_status_display(),
                'status_code': order.status,
                'created_at': order.created_at.strftime('%B %d, %Y'),
                'estimated_delivery': order.estimated_delivery_date.strftime('%B %d, %Y') if order.estimated_delivery_date else None,
                'carrier': order.carrier,
                'customer_name': order.get_full_name(),
            },
            'tracking_history': [
                {
                    'status': track.get_status_display(),
                    'status_code': track.status,
                    'note': track.note,
                    'location': track.location,
                    'updated_by': track.updated_by,
                    'date': track.created_at.strftime('%B %d, %Y'),
                    'time': track.created_at.strftime('%I:%M %p'),
                    'datetime': track.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'is_current': track.status == order.status,
                }
                for track in tracking_data
            ],
            'status_timeline': {
                'pending': order.pending_at.strftime('%B %d, %Y %I:%M %p') if order.pending_at else None,
                'processing': order.processing_at.strftime('%B %d, %Y %I:%M %p') if order.processing_at else None,
                'confirmed': order.confirmed_at.strftime('%B %d, %Y %I:%M %p') if order.confirmed_at else None,
                'packed': order.packed_at.strftime('%B %d, %Y %I:%M %p') if order.packed_at else None,
                'shipped': order.shipped_at.strftime('%B %d, %Y %I:%M %p') if order.shipped_at else None,
                'out_for_delivery': order.out_for_delivery_at.strftime('%B %d, %Y %I:%M %p') if order.out_for_delivery_at else None,
                'delivered': order.delivered_at.strftime('%B %d, %Y %I:%M %p') if order.delivered_at else None,
            }
        }
        return JsonResponse(data)
        
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': f"No order found with number: {order_number}"
        }, status=404)






def generate_pdf_invoice(order, is_admin=False):
    """Generate PDF invoice for an order"""
    try:
        # Download logo and convert to base64
        logo_url = "https://www.genialtouch.com/static/png%20transparent-01.png"
        logo_base64 = ""
        
        try:
            response = requests.get(logo_url)
            if response.status_code == 200:
                logo_base64 = base64.b64encode(response.content).decode('utf-8')
        except:
            pass
        
        context = {
            'order': order,
            'current_date': timezone.now(),
            'logo_base64': logo_base64,
            'logo_url': logo_url,
            'is_admin': is_admin,  # Add admin flag for template customization
        }
        
        # Render HTML template
        html_string = render_to_string('orders/invoice_simple.html', context)
        
        # Generate PDF using WeasyPrint (recommended for better PDF generation)
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        
        HTML(string=html_string).write_pdf(pdf_file.name)
        
        pdf_file.close()
        
        with open(pdf_file.name, 'rb') as f:
            pdf_data = f.read()
        
        os.unlink(pdf_file.name)
        
        return pdf_data
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

@user_passes_test(lambda u: u.is_staff)
def admin_download_invoice(request, order_number):
    """View for admin to download invoice"""
    order = get_object_or_404(Order, order_number=order_number)
    
    pdf_data = generate_pdf_invoice(order, is_admin=True)
    
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order.order_number}.pdf"'
        return response
    else:
        # Fallback to simple text
        return HttpResponse(
            f"""
            Invoice #{order.order_number}
            Customer: {order.get_full_name()}
            Email: {order.email}
            Phone: {order.phone_number}
            Address: {order.get_full_address()}
            Status: {order.get_status_display()}
            Total: ${order.grand_total}
            Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
            """,
            content_type='text/plain'
        )