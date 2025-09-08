from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, ProductVariation
from decimal import Decimal
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect

def cart_detail(request):
    # The context processor already provides cart data
    return render(request, 'cart/detail.html')


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        
        # Get selected attributes
        selected_attributes = {}
        for key, value in request.POST.items():
            if key.startswith('attribute_'):
                attr_name = key.replace('attribute_', '')
                selected_attributes[attr_name] = value
        
        # Find the matching variation
        variation = None
        if selected_attributes:
            variations = product.variations.all()
            for var in variations:
                var_attrs = {attr.attribute.name.lower(): attr.value for attr in var.attributes.all()}
                if var_attrs == selected_attributes:
                    variation = var
                    break
        
        if variation and variation.stock < quantity:
            return JsonResponse({
                'status': 'error',
                'message': 'Not enough stock available'
            }, status=400)
        
        cart = request.session.get('cart', {})
        cart_key = f"{product.id}-{variation.id}" if variation else str(product.id)
        
        if cart_key in cart:
            cart[cart_key]['quantity'] += quantity
        else:
            cart[cart_key] = {
                'quantity': quantity,
                'price': str(variation.get_price() if variation else product.get_price()),
                'name': product.name,
                'image': product.images.first().image.url if product.images.exists() else '',
                'variation_id': variation.id if variation else None,
                'attributes': selected_attributes if variation else {}
            }
        
        request.session['cart'] = cart
        request.session.modified = True
        
        context = get_cart_context(request)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'cart_item_count': context['cart_item_count'],
                'cart_total': str(context['cart_total']),
                'cart_items_html': render_to_string('partials/cart_items.html', context),
                'product_name': product.name,
                'product_price': str(variation.get_price() if variation else product.get_price()),
                'product_image': product.images.first().image.url if product.images.exists() else '',
                'variation_info': selected_attributes if variation else None
            })
        return redirect('cart_detail')
    
    return JsonResponse({'status': 'error'}, status=400)

def remove_from_cart(request, cart_key):
    cart = request.session.get('cart', {})
    
    if cart_key in cart:
        product_name = cart[cart_key].get('name', '')
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
        
        context = get_cart_context(request)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'cart_item_count': context['cart_item_count'],
                'cart_total': str(context['cart_total']),
                'cart_items_html': render_to_string('partials/cart_items.html', context),
                'cart_key': cart_key,
                'product_name': product_name
            })
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    
    return JsonResponse({'status': 'error', 'message': 'Item not in cart'}, status=400)

def get_cart_context(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')
    cart_item_count = 0
    
    for cart_key, item_data in cart.items():
        try:
            product_id = int(cart_key.split('-')[0])
            product = Product.objects.get(id=product_id)
            variation = None
            if 'variation_id' in item_data:
                variation = ProductVariation.objects.filter(id=item_data['variation_id']).first()
            
            price = Decimal(item_data.get('price', '0'))
            quantity = item_data.get('quantity', 0)
            item_total = price * quantity
            
            cart_items.append({
                'product': product,
                'variation': variation,
                'quantity': quantity,
                'price': price,
                'total': item_total,
                'attributes': item_data.get('attributes', {}),
                'cart_key': cart_key
            })
            
            cart_total += item_total
            cart_item_count += quantity
        except (Product.DoesNotExist, ValueError):
            continue
    
    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_item_count': cart_item_count
    }




def update_cart(request, cart_key):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        
        if cart_key in cart:
            cart[cart_key]['quantity'] = quantity
            request.session['cart'] = cart
            request.session.modified = True
            
            context = get_cart_context(request)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Find the item total
                item_total = Decimal(cart[cart_key]['price']) * quantity
                
                return JsonResponse({
                    'status': 'success',
                    'item_total': str(item_total),
                    'cart_total': str(context['cart_total']),
                    'cart_item_count': context['cart_item_count']
                })
    
    return JsonResponse({'status': 'error'}, status=400)



    