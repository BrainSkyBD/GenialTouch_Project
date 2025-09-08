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

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from decimal import Decimal
from products.models import Product, ProductVariation
from .models import Order, OrderItem, Country, State, City, TaxConfiguration
from django.db.models import Q
from django.http import JsonResponse
from .models import Country, State, City, PaymentMethod




def get_shipping_cost(request):
    city_id = request.GET.get('city_id')
    try:
        city = City.objects.get(id=city_id)
        return JsonResponse({'shipping_cost': str(city.shipping_cost)})
    except City.DoesNotExist:
        return JsonResponse({'shipping_cost': '0'})

def calculate_tax(request):
    country_id = request.GET.get('country_id')
    subtotal = Decimal(request.GET.get('subtotal', '0'))
    shipping = Decimal(request.GET.get('shipping', '0'))
    
    try:
        country = Country.objects.get(id=country_id)
        tax_config = TaxConfiguration.objects.filter(
            is_active=True,
        ).filter(
            Q(applies_to_all=True) | 
            Q(countries=country)
        ).first()
        
        if tax_config:
            tax_amount = (subtotal) * (tax_config.rate / 100)
            print("tax_amount")
            print(tax_amount)
            return JsonResponse({
                'status': 'success',
                'tax_rate': str(tax_config.rate),
                'tax_amount': str(tax_amount),
                'tax_name': tax_config.name,
                'grand_total': str(subtotal + shipping + tax_amount)
            })
    except Exception as e:
        print(f"Error calculating tax: {e}")
    
    return JsonResponse({
        'status': 'success',
        'tax_rate': '0',
        'tax_amount': '0',
        'tax_name': 'No Tax',
        'grand_total': str(subtotal + shipping)
    })






# @login_required
def checkout(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address_line1 = request.POST.get('address_line1')
        address_line2 = request.POST.get('address_line2', '')
        city_id = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        order_note = request.POST.get('order_note', '')
        payment_method_id = request.POST.get('payment_method')
        
        # Validate required fields
        required_fields = {
            'First Name': first_name,
            'Last Name': last_name,
            'Email': email,
            'Phone Number': phone_number,
            'Address Line 1': address_line1,
            'City': city_id,
            'Postal Code': postal_code,
            'Payment Method': payment_method_id
        }
        
        for field, value in required_fields.items():
            if not value:
                messages.error(request, f"{field} is required")
                return redirect('checkout')
        
        try:
            city = City.objects.get(id=city_id)
            country = city.country
            state = city.state if city.state else None
            payment_method = PaymentMethod.objects.get(id=payment_method_id, is_active=True)
        except (City.DoesNotExist, PaymentMethod.DoesNotExist) as e:
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
        shipping_cost = city.shipping_cost
        
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
        

        if request.user.is_authenticated:
            user=request.user
        else:
            user=None


        # Create the order
        order = Order.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address_line1=address_line1,
            address_line2=address_line2,
            postal_code=postal_code,
            country=country,
            state=state,
            city=city,
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
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
    
    context = {
        'countries': Country.objects.filter(is_active=True),
        'payment_methods': PaymentMethod.objects.filter(is_active=True),
        'cart_items': cart_context['cart_items'],
        'cart_total': cart_context['cart_total'],
        'cart_item_count': cart_context['cart_item_count'],
        'initial_data': initial_data
    }
    return render(request, 'orders/checkout.html', context)


def get_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id, is_active=True)
    data = [{'id': state.id, 'name': state.name} for state in states]
    return JsonResponse(data, safe=False)

def get_cities(request):
    country_id = request.GET.get('country_id')
    state_id = request.GET.get('state_id')
    
    if state_id:
        cities = City.objects.filter(state_id=state_id, is_active=True)
    elif country_id:
        cities = City.objects.filter(country_id=country_id, state__isnull=True, is_active=True)
    else:
        cities = City.objects.none()
    
    data = [{
        'id': city.id,
        'name': city.name,
        'shipping_cost': str(city.shipping_cost)
    } for city in cities]
    
    return JsonResponse(data, safe=False)



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
        
        # Create order
        order = Order(
            order_number=uuid.uuid4().hex[:10].upper(),
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone_number=request.POST.get('phone_number'),
            address_line1=request.POST.get('address_line1'),
            address_line2=request.POST.get('address_line2', ''),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country'),
            order_note=request.POST.get('order_note', ''),
            order_total=total_price,
            tax=Decimal('0.00'),  # You can add tax calculation
            shipping_cost=Decimal('0.00'),  # You can add shipping calculation
            grand_total=total_price,
            status='pending',
            ip_address=request.META.get('REMOTE_ADDR'),
            is_ordered=True
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
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)



def order_confirmation(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number)
        context = {
            'order': order,
        }
        return render(request, 'orders/order_confirmation.html', context)
    except Order.DoesNotExist:
        raise Http404("Order not found")