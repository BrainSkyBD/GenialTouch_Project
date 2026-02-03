from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import User, CustomerProfile
from orders.models import Order

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.core.paginator import Paginator
from django_countries.data import COUNTRIES
from django.db.models import Q
from PIL import Image
from io import BytesIO
import os
from django.core.files.base import ContentFile


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('register')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            username=email
        )
        
        # Create customer profile
        CustomerProfile.objects.create(user=user)
        
        # Log the user in
        login(request, user)
        messages.success(request, 'Registration successful')
        return redirect('home')
    
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')

# @login_required
# def profile(request):
#     user = request.user
#     orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
#     if request.method == 'POST':
#         user.first_name = request.POST.get('first_name')
#         user.last_name = request.POST.get('last_name')
#         user.phone_number = request.POST.get('phone_number')
#         user.date_of_birth = request.POST.get('date_of_birth')
#         user.address_line1 = request.POST.get('address_line1')
#         user.address_line2 = request.POST.get('address_line2')
#         user.city = request.POST.get('city')
#         user.state = request.POST.get('state')
#         user.postal_code = request.POST.get('postal_code')
#         user.country = request.POST.get('country')
#         user.save()
        
#         messages.success(request, 'Profile updated successfully')
#         return redirect('profile')
    
#     context = {
#         'user': user,
#         'orders': orders
#     }
#     return render(request, 'accounts/profile.html', context)

# @login_required
# def change_password(request):
#     if request.method == 'POST':
#         current_password = request.POST.get('current_password')
#         new_password = request.POST.get('new_password')
#         confirm_password = request.POST.get('confirm_password')
        
#         user = request.user
        
#         if not user.check_password(current_password):
#             messages.error(request, 'Current password is incorrect')
#             return redirect('change_password')
        
#         if new_password != confirm_password:
#             messages.error(request, 'Passwords do not match')
#             return redirect('change_password')
        
#         user.set_password(new_password)
#         user.save()
        
#         # Re-authenticate user after password change
#         login(request, user)
#         messages.success(request, 'Password changed successfully')
#         return redirect('profile')
    
#     return render(request, 'accounts/change_password.html')




@login_required
def profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    
    if request.method == 'POST':
        # Handle text fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.phone_number = request.POST.get('phone_number', '')
        
        # Handle date field
        date_of_birth = request.POST.get('date_of_birth')
        user.date_of_birth = date_of_birth if date_of_birth else None
        
        user.address_line1 = request.POST.get('address_line1', '')
        user.address_line2 = request.POST.get('address_line2', '')
        user.city = request.POST.get('city', '')
        user.state = request.POST.get('state', '')
        user.postal_code = request.POST.get('postal_code', '')
        user.country = request.POST.get('country', '')
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
            # The save() method in User model will handle WebP conversion
        
        user.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    # Sort countries alphabetically
    countries = sorted(COUNTRIES.items(), key=lambda x: x[1])
    
    context = {
        'user': user,
        'orders': orders,
        'countries': countries
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        user = request.user
        
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect')
            return redirect('change_password')
        
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('change_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('change_password')
        
        user.set_password(new_password)
        user.save()
        
        # Re-authenticate user after password change
        login(request, user)
        messages.success(request, 'Password changed successfully')
        return redirect('profile')
    
    return render(request, 'accounts/change_password.html')


@login_required
def order_history(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(id__icontains=search_query) |
            Q(status__icontains=search_query)
        )
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Date range filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        orders = orders.filter(created_at__date__range=[start_date, end_date])
    elif start_date:
        orders = orders.filter(created_at__date__gte=start_date)
    elif end_date:
        orders = orders.filter(created_at__date__lte=end_date)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices from Order model
    status_choices = Order.STATUS_CHOICES if hasattr(Order, 'STATUS_CHOICES') else []
    
    context = {
        'orders': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'start_date': start_date,
        'end_date': end_date,
        'status_choices': status_choices,
        'total_orders': orders.count(),
        'total_amount': sum(order.grand_total for order in orders if order.grand_total),
    }
    
    return render(request, 'accounts/order_history.html', context)












