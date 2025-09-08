from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from orders.models import Order
from .models import Payment
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def process_payment(request, order_id):
    order = Order.objects.get(order_number=order_id, user=request.user)
    
    if order.status != 'pending':
        messages.error(request, 'This order cannot be paid for')
        return redirect('order_detail', order_id=order_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        try:
            if payment_method == 'stripe':
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.grand_total * 100),  # Amount in cents
                    currency='usd',
                    metadata={'order_id': order.order_number},
                )
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    payment_method='stripe',
                    amount=order.grand_total,
                    transaction_id=intent.id,
                    status='pending',
                )
                
                return render(request, 'payments/stripe_payment.html', {
                    'client_secret': intent.client_secret,
                    'order': order,
                    'payment': payment,
                    'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
                })
            
            elif payment_method == 'paypal':
                # PayPal integration would go here
                pass
            
            else:
                messages.error(request, 'Invalid payment method')
                return redirect('checkout_payment', order_id=order_id)
        
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('checkout_payment', order_id=order_id)
    
    return render(request, 'payments/process_payment.html', {'order': order})

@login_required
def payment_success(request, order_id, payment_id):
    order = Order.objects.get(order_number=order_id, user=request.user)
    payment = Payment.objects.get(id=payment_id, order=order)
    
    # Update payment status
    payment.status = 'completed'
    payment.save()
    
    # Update order status
    order.status = 'processing'
    order.is_ordered = True
    order.save()
    
    messages.success(request, 'Payment successful! Your order is being processed.')
    return redirect('order_detail', order_id=order_id)

@login_required
def payment_failed(request, order_id, payment_id):
    order = Order.objects.get(order_number=order_id, user=request.user)
    payment = Payment.objects.get(id=payment_id, order=order)
    
    # Update payment status
    payment.status = 'failed'
    payment.save()
    
    messages.error(request, 'Payment failed. Please try again.')
    return redirect('checkout_payment', order_id=order_id)