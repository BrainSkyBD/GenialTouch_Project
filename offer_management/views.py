from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from .models import PromoCode, PromoCodeUsage
from cart.views import get_cart_context

@require_POST
def apply_promo_code(request):
    """Apply promo code to cart with minimum purchase validation"""
    code = request.POST.get('promo_code', '').strip().upper()

    print(code)
    
    if not code:
        return JsonResponse({
            'status': 'error',
            'message': 'Please enter a promo code'
        })
    
    try:
        promo_code = PromoCode.objects.get(code=code, is_active=True)
        
        # Get cart total
        cart_context = get_cart_context(request)
        cart_total = cart_context['cart_total']
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Calculate discount with validation
        discount_amount, is_valid, message = promo_code.calculate_discount(
            cart_total, 
            user=user
        )
        
        if not is_valid:
            return JsonResponse({
                'status': 'error',
                'message': message
            })
        
        # Check minimum purchase requirement specifically
        if cart_total < promo_code.minimum_purchase_amount:
            return JsonResponse({
                'status': 'error',
                'message': f'This promo code requires a minimum purchase of {{ currency_symbol }}{{ promo_code.minimum_purchase_amount }}. Your current cart total is {{ currency_symbol }}{{ cart_total }}.'
            })
        
        # Store in session
        request.session['applied_promo_code'] = promo_code.id
        request.session['promo_discount'] = float(discount_amount)
        
        # Calculate new totals
        new_total = cart_total - discount_amount
        
        return JsonResponse({
            'status': 'success',
            'message': f'Promo code applied! You saved {discount_amount}',
            'discount_amount': float(discount_amount),
            'new_total': float(new_total),
            'promo_code': promo_code.code,
            'promo_id': promo_code.id,
            'minimum_purchase': float(promo_code.minimum_purchase_amount),
            'cart_total': float(cart_total)
        })
        
    except PromoCode.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid promo code'
        })

@require_POST
def remove_promo_code(request):
    """Remove applied promo code from session"""
    if 'applied_promo_code' in request.session:
        del request.session['applied_promo_code']
    if 'promo_discount' in request.session:
        del request.session['promo_discount']
    
    # Get cart total
    cart_context = get_cart_context(request)
    cart_total = cart_context['cart_total']
    
    return JsonResponse({
        'status': 'success',
        'message': 'Promo code removed',
        'new_total': float(cart_total)
    })

def validate_promo_code(request):
    """Validate promo code without applying - shows minimum purchase requirement"""
    code = request.GET.get('code', '').strip().upper()
    
    if not code:
        return JsonResponse({
            'valid': False,
            'message': 'No code provided'
        })
    
    try:
        promo_code = PromoCode.objects.get(code=code, is_active=True)
        
        # Get cart total
        cart_context = get_cart_context(request)
        cart_total = cart_context['cart_total']
        
        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Check minimum purchase requirement first (for display)
        meets_minimum = cart_total >= promo_code.minimum_purchase_amount
        remaining_amount = max(0, promo_code.minimum_purchase_amount - cart_total)
        
        # Calculate discount if applicable
        discount_amount, is_valid, message = promo_code.calculate_discount(
            cart_total, 
            user=user
        )
        
        response_data = {
            'valid': is_valid,
            'discount_type': promo_code.discount_type,
            'discount_value': float(promo_code.discount_value),
            'minimum_purchase': float(promo_code.minimum_purchase_amount),
            'cart_total': float(cart_total),
            'meets_minimum': meets_minimum,
            'remaining_amount': float(remaining_amount),
            'estimated_discount': float(discount_amount) if is_valid else 0,
        }
        
        if is_valid:
            response_data['message'] = f'Valid! Add {{ currency_symbol }}{{ cart_total|floatformat:2 }} to cart to get {{ discount_amount|floatformat:2 }} discount'
        elif not meets_minimum:
            response_data['message'] = f'Add {{ currency_symbol }}{{ remaining_amount|floatformat:2 }} more to use this code (Minimum: {{ currency_symbol }}{{ promo_code.minimum_purchase_amount }})'
        else:
            response_data['message'] = message
            
        return JsonResponse(response_data)
            
    except PromoCode.DoesNotExist:
        return JsonResponse({
            'valid': False,
            'message': 'Invalid promo code'
        })