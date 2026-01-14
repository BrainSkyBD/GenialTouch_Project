from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem, OrderTracking
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

import uuid

from django.http import JsonResponse
from .models import Country, District, Thana

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

# def calculate_tax(request):
#     country_id = request.GET.get('country_id')
#     subtotal = Decimal(request.GET.get('subtotal', '0'))
#     shipping = Decimal(request.GET.get('shipping', '0'))
    
#     try:
#         country = Country.objects.get(id=country_id)
#         tax_config = TaxConfiguration.objects.filter(
#             is_active=True,
#         ).filter(
#             Q(applies_to_all=True) | 
#             Q(countries=country)
#         ).first()
        
#         if tax_config:
#             tax_amount = (subtotal) * (tax_config.rate / 100)
#             print("tax_amount")
#             print(tax_amount)
#             return JsonResponse({
#                 'status': 'success',
#                 'tax_rate': str(tax_config.rate),
#                 'tax_amount': str(tax_amount),
#                 'tax_name': tax_config.name,
#                 'grand_total': str(subtotal + shipping + tax_amount)
#             })
#     except Exception as e:
#         print(f"Error calculating tax: {e}")
    
#     return JsonResponse({
#         'status': 'success',
#         'tax_rate': '0',
#         'tax_amount': '0',
#         'tax_name': 'No Tax',
#         'grand_total': str(subtotal + shipping)
#     })


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


# @login_required
# def checkout(request):
#     if request.method == 'POST':
#         # Get form data
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')  # Optional
#         phone_number = request.POST.get('phone_number')
#         full_address = request.POST.get('full_address')
#         country_id = request.POST.get('country')
#         district_id = request.POST.get('district')
#         thana_id = request.POST.get('thana')
#         postal_code = request.POST.get('postal_code', '')
#         order_note = request.POST.get('order_note', '')
#         payment_method_id = request.POST.get('payment_method')
        
#         # Validate required fields
#         required_fields = {
#             'First Name': first_name,
#             'Last Name': last_name,
#             'Phone Number': phone_number,
#             'Full Address': full_address,
#             'Country': country_id,
#             'District': district_id,
#             'Payment Method': payment_method_id
#         }
        
#         for field, value in required_fields.items():
#             if not value:
#                 messages.error(request, f"{field} is required")
#                 return redirect('checkout')
        
#         try:
#             country = Country.objects.get(id=country_id)
#             district = District.objects.get(id=district_id)
#             thana = None
#             if thana_id:
#                 thana = Thana.objects.get(id=thana_id, district=district)
#             payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
#         except (Country.DoesNotExist, District.DoesNotExist, 
#                 Thana.DoesNotExist, PaymentMethod.DoesNotExist) as e:
#             messages.error(request, "Invalid selection")
#             return redirect('checkout')
        
#         # Get cart data
#         cart = request.session.get('cart', {})
#         if not cart:
#             messages.error(request, "Your cart is empty")
#             return redirect('cart_detail')
        
#         # Calculate totals
#         cart_context = get_cart_context(request)
#         cart_total = cart_context['cart_total']
#         shipping_cost = district.shipping_cost
        
#         # Calculate tax
#         tax_config = TaxConfiguration.objects.filter(
#             is_active=True,
#         ).filter(
#             Q(applies_to_all=True) | 
#             Q(countries=country)
#         ).first()
        
#         tax_rate = tax_config.rate if tax_config else Decimal('0')
#         tax_amount = (cart_total + shipping_cost) * (tax_rate / 100)
#         grand_total = cart_total + shipping_cost + tax_amount
        
#         # Create the order
#         order = Order.objects.create(
#             user=request.user,
#             first_name=first_name,
#             last_name=last_name,
#             email=email if email else request.user.email,  # Use user email if not provided
#             phone_number=phone_number,
#             full_address=full_address,
#             country=country,
#             district=district,
#             thana=thana,
#             postal_code=postal_code,
#             order_note=order_note,
#             order_total=cart_total,
#             shipping_cost=shipping_cost,
#             tax_rate=tax_rate,
#             tax_amount=tax_amount,
#             grand_total=grand_total,
#             payment_method=payment_method,
#             status='pending',
#             ip_address=request.META.get('REMOTE_ADDR')
#         )
        
#         # Create order items
#         for cart_key, item_data in cart.items():
#             product_id = int(cart_key.split('-')[0])
#             product = Product.objects.get(id=product_id)
#             variation = None
#             if 'variation_id' in item_data:
#                 variation = ProductVariation.objects.get(id=item_data['variation_id'])
            
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 variation=variation,
#                 quantity=item_data['quantity'],
#                 price=item_data['price']
#             )
        
#         # Clear the cart
#         request.session['cart'] = {}
#         request.session.modified = True
        
#         messages.success(request, f"Order #{order.order_number} placed successfully!")
#         return redirect('order_confirmation', order_number=order.order_number)
    
#     # GET request - show checkout form
#     cart_context = get_cart_context(request)
#     if not cart_context['cart_items']:
#         messages.warning(request, "Your cart is empty")
#         return redirect('cart_detail')
    
#     # Pre-fill form with user data if available
#     initial_data = {}
#     if request.user.is_authenticated:
#         initial_data = {
#             'first_name': request.user.first_name or '',
#             'last_name': request.user.last_name or '',
#             'email': request.user.email,
#             'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
#         }
    
#     context = {
#         'countries': Country.objects.filter(is_active=True),
#         'payment_methods': PaymentMethod.objects.filter(is_active=True),
#         'cart_items': cart_context['cart_items'],
#         'cart_total': cart_context['cart_total'],
#         'cart_item_count': cart_context['cart_item_count'],
#         'initial_data': initial_data
#     }
#     return render(request, 'orders/checkout.html', context)

from datetime import datetime  


@login_required
def checkout(request):
    if request.method == 'POST':
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
        
        # Get birth date and month (optional) - NEW FORMAT
        birth_date = request.POST.get('birth_date', '')  # Now 1-31
        birth_month = request.POST.get('birth_month', '')
        
        # Validate birth date if provided
        if birth_date:
            try:
                # Convert to integer and validate
                birth_date_int = int(birth_date)
                if not (1 <= birth_date_int <= 31):
                    messages.error(request, "Birth date must be between 1 and 31")
                    return redirect('checkout')
            except (ValueError, TypeError):
                birth_date = None  # Reset to None if invalid
        
        # Validate birth month if provided
        if birth_month and birth_month not in [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]:
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
            messages.error(request, "Invalid selection")
            return redirect('checkout')
        
        # Get cart data
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty")
            return redirect('cart_detail')
        
        # Calculate totals
        cart_context = get_cart_context(request)
        cart_total = cart_context['cart_total']
        shipping_cost = district.shipping_cost
        
        # Calculate tax
        tax_config = TaxConfiguration.objects.filter(
            is_active=True,
        ).filter(
            Q(applies_to_all=True) | 
            Q(countries=country)
        ).first()
        
        tax_rate = tax_config.rate if tax_config else Decimal('0')
        tax_amount = (cart_total + shipping_cost) * (tax_rate / 100)
        grand_total = cart_total + shipping_cost + tax_amount
        
        # Create the order with birth date and month - UPDATED FORMAT
        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email if email else request.user.email,
            phone_number=phone_number,
            full_address=full_address,
            birth_date=birth_date if birth_date else None,  # Now stores day number
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
            grand_total=grand_total,
            payment_method=payment_method,
            status='pending',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        # Create order items
        for cart_key, item_data in cart.items():
            product_id = int(cart_key.split('-')[0])
            product = Product.objects.get(id=product_id)
            variation = None
            if 'variation_id' in item_data:
                variation = ProductVariation.objects.get(id=item_data['variation_id'])
            
            OrderItem.objects.create(
                order=order,
                product=product,
                variation=variation,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
        
        # Clear the cart
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f"Order #{order.order_number} placed successfully!")
        return redirect('order_confirmation', order_number=order.order_number)
    
    # GET request - show checkout form
    cart_context = get_cart_context(request)
    if not cart_context['cart_items']:
        messages.warning(request, "Your cart is empty")
        return redirect('cart_detail')
    
    # Pre-fill form with user data if available
    initial_data = {}
    if request.user.is_authenticated:
        initial_data = {
            'first_name': request.user.first_name or '',
            'last_name': request.user.last_name or '',
            'email': request.user.email,
            'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
        }
    
    # Generate days range for birth date dropdown
    days_range = range(1, 32)  # 1 to 31
    
    context = {
        'countries': Country.objects.filter(is_active=True).order_by('name'),
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'cart_items': cart_context['cart_items'],
        'cart_total': cart_context['cart_total'],
        'cart_item_count': cart_context['cart_item_count'],
        'initial_data': initial_data,
        'days_range': days_range,  # Add days range for dropdown
    }
    return render(request, 'orders/checkout.html', context)

# @login_required
# def checkout(request):
#     if request.method == 'POST':
#         # Get form data
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         phone_number = request.POST.get('phone_number')
#         full_address = request.POST.get('full_address')
#         country_id = request.POST.get('country')
#         district_id = request.POST.get('district')
#         thana_id = request.POST.get('thana')
#         postal_code = request.POST.get('postal_code', '')
#         order_note = request.POST.get('order_note', '')
#         payment_method_id = request.POST.get('payment_method')
        
#         # Get birth date and month (optional)
#         birth_date_str = request.POST.get('birth_date', '')
#         birth_month = request.POST.get('birth_month', '')
        
#         # Parse birth date if provided
#         birth_date = None
#         if birth_date_str:
#             try:
#                 birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
#             except (ValueError, TypeError):
#                 birth_date = None
        
#         # Validate required fields
#         required_fields = {
#             'First Name': first_name,
#             'Last Name': last_name,
#             'Phone Number': phone_number,
#             'Full Address': full_address,
#             'Country': country_id,
#             'District': district_id,
#             'Payment Method': payment_method_id
#         }
        
#         for field, value in required_fields.items():
#             if not value:
#                 messages.error(request, f"{field} is required")
#                 return redirect('checkout')
        
#         try:
#             country = Country.objects.get(id=country_id)
#             district = District.objects.get(id=district_id)
#             thana = None
#             if thana_id:
#                 thana = Thana.objects.get(id=thana_id, district=district)
#             payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
#         except (Country.DoesNotExist, District.DoesNotExist, 
#                 Thana.DoesNotExist, PaymentMethod.DoesNotExist) as e:
#             messages.error(request, "Invalid selection")
#             return redirect('checkout')
        
#         # Get cart data
#         cart = request.session.get('cart', {})
#         if not cart:
#             messages.error(request, "Your cart is empty")
#             return redirect('cart_detail')
        
#         # Calculate totals
#         cart_context = get_cart_context(request)
#         cart_total = cart_context['cart_total']
#         shipping_cost = district.shipping_cost
        
#         # Calculate tax
#         tax_config = TaxConfiguration.objects.filter(
#             is_active=True,
#         ).filter(
#             Q(applies_to_all=True) | 
#             Q(countries=country)
#         ).first()
        
#         tax_rate = tax_config.rate if tax_config else Decimal('0')
#         tax_amount = (cart_total + shipping_cost) * (tax_rate / 100)
#         grand_total = cart_total + shipping_cost + tax_amount
        
#         # Create the order with birth date and month
#         order = Order.objects.create(
#             user=request.user,
#             first_name=first_name,
#             last_name=last_name,
#             email=email if email else request.user.email,
#             phone_number=phone_number,
#             full_address=full_address,
#             birth_date=birth_date,  # Add birth date
#             birth_month=birth_month,  # Add birth month
#             country=country,
#             district=district,
#             thana=thana,
#             postal_code=postal_code,
#             order_note=order_note,
#             order_total=cart_total,
#             shipping_cost=shipping_cost,
#             tax_rate=tax_rate,
#             tax_amount=tax_amount,
#             grand_total=grand_total,
#             payment_method=payment_method,
#             status='pending',
#             ip_address=request.META.get('REMOTE_ADDR')
#         )
        
#         # Create order items
#         for cart_key, item_data in cart.items():
#             product_id = int(cart_key.split('-')[0])
#             product = Product.objects.get(id=product_id)
#             variation = None
#             if 'variation_id' in item_data:
#                 variation = ProductVariation.objects.get(id=item_data['variation_id'])
            
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 variation=variation,
#                 quantity=item_data['quantity'],
#                 price=item_data['price']
#             )
        
#         # Clear the cart
#         request.session['cart'] = {}
#         request.session.modified = True
        
#         messages.success(request, f"Order #{order.order_number} placed successfully!")
#         return redirect('order_confirmation', order_number=order.order_number)
    
#     # GET request - show checkout form
#     cart_context = get_cart_context(request)
#     if not cart_context['cart_items']:
#         messages.warning(request, "Your cart is empty")
#         return redirect('cart_detail')
    
#     # Pre-fill form with user data if available
#     initial_data = {}
#     if request.user.is_authenticated:
#         initial_data = {
#             'first_name': request.user.first_name or '',
#             'last_name': request.user.last_name or '',
#             'email': request.user.email,
#             'phone_number': request.user.phone_number if hasattr(request.user, 'phone_number') else '',
#         }
    
#     # Get today's date for max date in birth date field
#     today = datetime.now().strftime('%Y-%m-%d')
    
#     context = {
#         'countries': Country.objects.filter(is_active=True).order_by('name'),
#         'payment_methods': PaymentMethod.objects.filter(is_active=True),
#         'cart_items': cart_context['cart_items'],
#         'cart_total': cart_context['cart_total'],
#         'cart_item_count': cart_context['cart_item_count'],
#         'initial_data': initial_data,
#         'today': today,  # Add today's date for date picker
#     }
#     return render(request, 'orders/checkout.html', context)

# # @login_required
# def checkout(request):
#     if request.method == 'POST':
#         # Get form data
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         phone_number = request.POST.get('phone_number')
#         address_line1 = request.POST.get('address_line1')
#         address_line2 = request.POST.get('address_line2', '')
#         city_id = request.POST.get('city')
#         postal_code = request.POST.get('postal_code')
#         order_note = request.POST.get('order_note', '')
#         payment_method_id = request.POST.get('payment_method')
        
#         # Validate required fields
#         required_fields = {
#             'First Name': first_name,
#             'Last Name': last_name,
#             'Email': email,
#             'Phone Number': phone_number,
#             'Address Line 1': address_line1,
#             'City': city_id,
#             'Postal Code': postal_code,
#             'Payment Method': payment_method_id
#         }
        
#         for field, value in required_fields.items():
#             if not value:
#                 messages.error(request, f"{field} is required")
#                 return redirect('checkout')
        
#         try:
#             city = City.objects.get(id=city_id)
#             country = city.country
#             state = city.state if city.state else None
#             payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
#         except (City.DoesNotExist, PaymentMethod.DoesNotExist) as e:
#             messages.error(request, "Invalid selection")
#             return redirect('checkout')
        
#         # Get cart data
#         cart = request.session.get('cart', {})
#         if not cart:
#             messages.error(request, "Your cart is empty")
#             return redirect('cart_detail')
        
#         # Calculate totals
#         cart_context = get_cart_context(request)
#         cart_total = cart_context['cart_total']
#         shipping_cost = city.shipping_cost
        
#         # Calculate tax
#         tax_config = TaxConfiguration.objects.filter(
#             is_active=True,
#         ).filter(
#             Q(applies_to_all=True) | 
#             Q(countries=country)
#         ).first()
        
#         tax_rate = tax_config.rate if tax_config else Decimal('0')
#         tax_amount = (cart_total + shipping_cost) * (tax_rate / 100)
#         grand_total = cart_total + shipping_cost + tax_amount
        

#         if request.user.is_authenticated:
#             user=request.user
#         else:
#             user=None


#         # Create the order
#         order = Order.objects.create(
#             user=user,
#             first_name=first_name,
#             last_name=last_name,
#             email=email,
#             phone_number=phone_number,
#             address_line1=address_line1,
#             address_line2=address_line2,
#             postal_code=postal_code,
#             country=country,
#             state=state,
#             city=city,
#             order_note=order_note,
#             order_total=cart_total,
#             shipping_cost=shipping_cost,
#             tax_rate=tax_rate,
#             tax_amount=tax_amount,
#             grand_total=grand_total,
#             payment_method=payment_method,
#             status='pending',
#             ip_address=request.META.get('REMOTE_ADDR')
#         )
        
#         # Create order items
#         for cart_key, item_data in cart.items():
#             product_id = int(cart_key.split('-')[0])
#             product = Product.objects.get(id=product_id)
#             variation = None
#             if 'variation_id' in item_data:
#                 variation = ProductVariation.objects.get(id=item_data['variation_id'])
            
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 variation=variation,
#                 quantity=item_data['quantity'],
#                 price=item_data['price']
#             )
        
#         # Clear the cart
#         request.session['cart'] = {}
#         request.session.modified = True
        
#         messages.success(request, f"Order #{order.order_number} placed successfully!")
#         return redirect('order_confirmation', order_number=order.order_number)
    
#     # GET request - show checkout form
#     cart_context = get_cart_context(request)
#     if not cart_context['cart_items']:
#         messages.warning(request, "Your cart is empty")
#         return redirect('cart_detail')
    
#     # Pre-fill form with user data if available
#     initial_data = {}
#     if request.user.is_authenticated:
#         initial_data = {
#             'first_name': request.user.first_name,
#             'last_name': request.user.last_name,
#             'email': request.user.email,
#         }
    
#     context = {
#         'countries': Country.objects.filter(is_active=True),
#         'payment_methods': PaymentMethod.objects.filter(is_active=True),
#         'cart_items': cart_context['cart_items'],
#         'cart_total': cart_context['cart_total'],
#         'cart_item_count': cart_context['cart_item_count'],
#         'initial_data': initial_data
#     }
#     return render(request, 'orders/checkout.html', context)


# def get_states(request):
#     country_id = request.GET.get('country_id')
#     states = State.objects.filter(country_id=country_id, is_active=True)
#     data = [{'id': state.id, 'name': state.name} for state in states]
#     return JsonResponse(data, safe=False)

# def get_cities(request):
#     country_id = request.GET.get('country_id')
#     state_id = request.GET.get('state_id')
    
#     if state_id:
#         cities = City.objects.filter(state_id=state_id, is_active=True)
#     elif country_id:
#         cities = City.objects.filter(country_id=country_id, state__isnull=True, is_active=True)
#     else:
#         cities = City.objects.none()
    
#     data = [{
#         'id': city.id,
#         'name': city.name,
#         'shipping_cost': str(city.shipping_cost)
#     } for city in cities]
    
#     return JsonResponse(data, safe=False)



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_number=order_id, user=request.user)
    
    if order.status not in ['delivered', 'cancelled', 'refunded']:
        order.status = 'cancelled'
        order.save()
        OrderTracking.objects.create(order=order, status='cancelled', note='Order cancelled by customer')
        messages.success(request, 'Your order has been cancelled')
    else:
        messages.error(request, 'This order cannot be cancelled')
    
    return redirect('order_detail', order_id=order_id)



# @require_POST
# def process_buy_now(request):
#     try:
#         # Get product and quantity
#         product_id = request.POST.get('product_id')
#         quantity = int(request.POST.get('quantity', 1))
#         product = Product.objects.get(id=product_id)
        
#         # Get selected variations
#         variation_attributes = {}
#         for key, value in request.POST.items():
#             if key.startswith('attribute_'):
#                 attr_name = key.replace('attribute_', '')
#                 variation_attributes[attr_name] = value
        
#         # Find the matching variation
#         variation = None
#         if variation_attributes:
#             variations = product.variations.all()
#             for v in variations:
#                 if all(attr.value == variation_attributes.get(attr.attribute.name.lower().replace(' ', '_')) 
#                    for attr in v.attributes.all()):
#                     variation = v
#                     break
        
#         # Calculate price
#         price = variation.get_price() if variation else product.get_price()
#         total_price = price * quantity

#         get_payment_method_value = request.POST.get('payment_method')
#         get_payment_method_row = None
#         if get_payment_method_value:
#             get_payment_method_row = PaymentMethod.objects.get(id=get_payment_method_value)

        
#         get_country_value = request.POST.get('country')
#         get_country_row = None
#         if get_country_value:
#             get_country_row = Country.objects.get(id=get_country_value)

#         get_city_value = request.POST.get('city')
#         get_city_row = None
#         if get_city_value:
#             get_city_row = City.objects.get(id=get_city_value)

        
#         get_state_value = request.POST.get('state')
#         get_state_row = None
#         if get_state_value:
#             get_state_row = State.objects.get(id=get_state_value)


        
#         # Create order
#         order = Order(
#             order_number=uuid.uuid4().hex[:10].upper(),
#             first_name=request.POST.get('first_name'),
#             last_name=request.POST.get('last_name'),
#             email=request.POST.get('email'),
#             phone_number=request.POST.get('phone_number'),
#             address_line1=request.POST.get('address_line1'),
#             address_line2=request.POST.get('address_line2', ''),
#             city=get_city_row,
#             state=get_state_row,
#             postal_code=request.POST.get('postal_code'),
#             country=get_country_row,
#             order_note=request.POST.get('order_note', ''),
#             order_total=total_price,
#             tax=Decimal('0.00'),  # You can add tax calculation
#             shipping_cost=Decimal('0.00'),  # You can add shipping calculation
#             grand_total=total_price,
#             status='pending',
#             ip_address=request.META.get('REMOTE_ADDR'),
#             is_ordered=True,
#             payment_method=get_payment_method_row,
#         )
        
#         if request.user.is_authenticated:
#             order.user = request.user
        
#         order.save()
        
#         # Create order item
#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             variation=variation,
#             quantity=quantity,
#             price=price
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'redirect_url': reverse('order_confirmation', args=[order.order_number])
#         })
        
#     except Product.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Product not found'
#         }, status=404)
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=400)



# @require_POST
# def process_buy_now(request):
#     try:
#         # Get product and quantity
#         product_id = request.POST.get('product_id')
#         quantity = int(request.POST.get('quantity', 1))
#         product = Product.objects.get(id=product_id)
        
#         # Get selected variations
#         variation_attributes = {}
#         for key, value in request.POST.items():
#             if key.startswith('attribute_'):
#                 attr_name = key.replace('attribute_', '')
#                 variation_attributes[attr_name] = value
        
#         # Find the matching variation
#         variation = None
#         if variation_attributes:
#             variations = product.variations.all()
#             for v in variations:
#                 if all(attr.value == variation_attributes.get(attr.attribute.name.lower().replace(' ', '_')) 
#                    for attr in v.attributes.all()):
#                     variation = v
#                     break
        
#         # Calculate price
#         price = variation.get_price() if variation else product.get_price()
#         total_price = price * quantity

#         # Get payment method
#         get_payment_method_value = request.POST.get('payment_method')
#         get_payment_method_row = None
#         if get_payment_method_value:
#             get_payment_method_row = PaymentMethod.objects.get(id=get_payment_method_value)

#         # Get location data
#         get_country_value = request.POST.get('country')
#         get_country_row = None
#         if get_country_value:
#             get_country_row = Country.objects.get(id=get_country_value)

#         get_district_value = request.POST.get('district')
#         get_district_row = None
#         if get_district_value:
#             get_district_row = District.objects.get(id=get_district_value)

#         get_thana_value = request.POST.get('thana')
#         get_thana_row = None
#         if get_thana_value:
#             get_thana_row = Thana.objects.get(id=get_thana_value)

#         # Calculate shipping cost (get from district)
#         shipping_cost = Decimal('0.00')
#         if get_district_row:
#             shipping_cost = get_district_row.shipping_cost

#         # Calculate tax
#         tax_rate = Decimal('0.00')
#         tax_amount = Decimal('0.00')
        
#         # Find applicable tax configuration
#         if get_country_row:
#             # Try to find tax for specific country first
#             tax_configs = TaxConfiguration.objects.filter(
#                 is_active=True,
#                 countries=get_country_row
#             ).order_by('-rate').first()
            
#             if not tax_configs:
#                 # If no country-specific tax, try global tax
#                 tax_configs = TaxConfiguration.objects.filter(
#                     is_active=True,
#                     applies_to_all=True
#                 ).order_by('-rate').first()
            
#             if tax_configs:
#                 tax_rate = tax_configs.rate
#                 tax_amount = (total_price * tax_rate) / Decimal('100.00')

#         # Calculate grand total
#         grand_total = total_price + shipping_cost + tax_amount

#         # Create order with updated field names
#         order = Order(
#             order_number=uuid.uuid4().hex[:10].upper(),
#             first_name=request.POST.get('first_name'),
#             last_name=request.POST.get('last_name'),
#             email=request.POST.get('email'),
#             phone_number=request.POST.get('phone_number'),
#             full_address=request.POST.get('full_address'),  # Updated field
#             country=get_country_row,
#             district=get_district_row,
#             thana=get_thana_row,
#             postal_code=request.POST.get('postal_code', ''),
#             order_note=request.POST.get('order_note', ''),
#             order_total=total_price,
#             shipping_cost=shipping_cost,
#             tax=tax_amount,  # You might want to keep this for backward compatibility
#             grand_total=grand_total,
#             tax_rate=tax_rate,  # New field
#             tax_amount=tax_amount,  # New field
#             status='pending',
#             ip_address=request.META.get('REMOTE_ADDR'),
#             is_ordered=True,
#             payment_method=get_payment_method_row,
#             payment_details={}  # You can store payment-specific data here
#         )
        
#         if request.user.is_authenticated:
#             order.user = request.user
        
#         order.save()
        
#         # Create order item
#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             variation=variation,
#             quantity=quantity,
#             price=price
#         )
        
#         return JsonResponse({
#             'status': 'success',
#             'redirect_url': reverse('order_confirmation', args=[order.order_number])
#         })
        
#     except Product.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Product not found'
#         }, status=404)
#     except PaymentMethod.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Payment method not found'
#         }, status=400)
#     except Country.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Country not found'
#         }, status=400)
#     except District.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'District not found'
#         }, status=400)
#     except Thana.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Thana not found'
#         }, status=400)
#     except Exception as e:
#         return JsonResponse({
#             'status': 'error',
#             'message': str(e)
#         }, status=400)





@require_POST
def process_buy_now(request):
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

        # Get country
        get_country_value = request.POST.get('country')
        get_country_row = None
        if get_country_value:
            get_country_row = Country.objects.get(id=get_country_value)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Country is required'
            }, status=400)

        # Get district
        get_district_value = request.POST.get('district')
        get_district_row = None
        if get_district_value:
            get_district_row = District.objects.get(id=get_district_value)
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'District is required'
            }, status=400)

        # Get thana (optional)
        get_thana_value = request.POST.get('thana')
        get_thana_row = None
        if get_thana_value:
            try:
                get_thana_row = Thana.objects.get(id=get_thana_value, district=get_district_row)
            except Thana.DoesNotExist:
                get_thana_row = None

        # Get required form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        full_address = request.POST.get('full_address')
        postal_code = request.POST.get('postal_code', '')
        order_note = request.POST.get('order_note', '')

        # Get birth date and month (optional)
        # birth_date_str = request.POST.get('birth_date', '')
        # birth_month = request.POST.get('birth_month', '')

        # Get birth date and month (optional)
        birth_date = request.POST.get('birth_date', '')
        birth_month = request.POST.get('birth_month', '')
        
        # Parse birth date if provided
        # birth_date = None
        # if birth_date_str:
        #     try:
        #         birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        #     except (ValueError, TypeError):
        #         birth_date = None
        
        # Validate birth date if provided
        if birth_date:
            try:
                # Convert to integer and validate
                birth_date_int = int(birth_date)
                if not (1 <= birth_date_int <= 31):
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Birth date must be between 1 and 31'
                    }, status=400)
            except (ValueError, TypeError):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid birth date'
                }, status=400)
        # Validate birth month if provided
        if birth_month and birth_month not in [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid birth month'
            }, status=400)



        # Validate required fields
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Phone Number': phone_number,
            'Full Address': full_address,
        }
        
        for field, value in required_fields.items():
            if not value:
                return JsonResponse({
                    'status': 'error',
                    'message': f'{field} is required'
                }, status=400)

        # If email is not provided and user is authenticated, use user's email
        if not email and request.user.is_authenticated:
            email = request.user.email
        elif not email:
            email = f"buynow-{uuid.uuid4().hex[:8]}@example.com"  # Generate a temporary email

        # Calculate shipping cost
        shipping_cost = get_district_row.shipping_cost
        
        # Calculate tax
        tax_config = TaxConfiguration.objects.filter(
            is_active=True,
        ).filter(
            Q(applies_to_all=True) | 
            Q(countries=get_country_row)
        ).first()
        
        tax_rate = tax_config.rate if tax_config else Decimal('0')
        tax_amount = (total_price + shipping_cost) * (tax_rate / 100)
        grand_total = total_price + shipping_cost + tax_amount

        # Create order
        order = Order(
            order_number=uuid.uuid4().hex[:10].upper(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            full_address=full_address,

            birth_date=birth_date if birth_date else None,
            birth_month=birth_month if birth_month else None,

            country=get_country_row,
            district=get_district_row,
            thana=get_thana_row,
            postal_code=postal_code,
            order_note=order_note,
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
    except Country.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid country'
        }, status=400)
    except District.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid district'
        }, status=400)
    except Exception as e:
        import traceback
        print(f"Error in process_buy_now: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)


def order_confirmation(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        context = {
            'order': order,
        }
        return render(request, 'orders/order_confirmation.html', context)
    except Order.DoesNotExist:
        raise Http404("Order not found")