from django.contrib import admin
from django.utils.html import format_html
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # Display fields in list view
    list_display = ('id', 'user_email', 'product_name', 'rating_stars', 'title', 'is_approved', 'created_at')
    
    # Make fields clickable for editing
    list_display_links = ('id', 'user_email', 'product_name')
    
    # Add filters in the sidebar
    list_filter = ('is_approved', 'rating', 'created_at', 'updated_at')
    
    # Add search functionality
    search_fields = ('user__email', 'product__name', 'title', 'comment')
    
    # Add actions for bulk operations
    actions = ['approve_reviews', 'disapprove_reviews']
    
    # Fields to display in the detail/edit form
    fieldsets = (
        ('User & Product Information', {
            'fields': ('user', 'product')
        }),
        ('Review Content', {
            'fields': ('rating', 'title', 'comment')
        }),
        ('Approval Status', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Makes this section collapsible
        })
    )
    
    # Fields that should be read-only
    readonly_fields = ('created_at', 'updated_at')
    
    # Custom methods for display
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def rating_stars(self, obj):
        # Display rating as stars (★) instead of numbers
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold; font-size: 14px;">{}</span>', stars)
    rating_stars.short_description = 'Rating'
    
    # Custom admin actions
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"Approved {queryset.count()} review(s).")
    approve_reviews.short_description = "Approve selected reviews"
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"Disapproved {queryset.count()} review(s).")
    disapprove_reviews.short_description = "Disapprove selected reviews"
    
    # Customize ordering
    ordering = ('-created_at', '-updated_at')
    
    # Pagination
    list_per_page = 20