from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Review
from orders.models import OrderItem

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased the product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product
    ).exists()
    
    if not has_purchased:
        messages.error(request, 'You need to purchase this product before reviewing it')
        return redirect('product_detail', slug=product.slug)
    
    # Check if user already reviewed this product
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(request, 'You have already reviewed this product')
        return redirect('product_detail', slug=product.slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title')
        comment = request.POST.get('comment')
        
        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            title=title,
            comment=comment,
            is_approved=True  # Auto-approve for now, can be moderated later
        )
        
        messages.success(request, 'Thank you for your review!')
        return redirect('product_detail', slug=product.slug)
    
    return render(request, 'reviews/add_review.html', {'product': product})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        review.rating = request.POST.get('rating')
        review.title = request.POST.get('title')
        review.comment = request.POST.get('comment')
        review.save()
        
        messages.success(request, 'Your review has been updated')
        return redirect('product_detail', slug=review.product.slug)
    
    return render(request, 'reviews/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    review.delete()
    
    messages.success(request, 'Your review has been deleted')
    return redirect('product_detail', slug=product_slug)