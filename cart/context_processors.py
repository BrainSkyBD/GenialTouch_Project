from decimal import Decimal
from products.models import Product, ProductVariation

def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    cart_total = Decimal('0.00')
    cart_item_count = 0
    
    for cart_key, item_data in cart.items():
        try:
            # Split the cart_key to get product_id and variation_id
            parts = cart_key.split('-')
            product_id = parts[0]
            
            product = Product.objects.get(id=product_id)
            variation = None
            variation_id = item_data.get('variation_id')
            
            if variation_id:
                variation = ProductVariation.objects.filter(id=variation_id).first()
            
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
            # Remove invalid products from cart
            del cart[cart_key]
            request.session.modified = True
    
    return {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'cart_item_count': cart_item_count
    }