from django.contrib import admin
from django import forms
from .models import Country, State, City, Order, OrderItem, OrderTracking, PaymentMethod, TaxConfiguration
from django.utils.html import format_html

# Custom Admin Forms
class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make state field optional
        self.fields['state'].required = False
        
        # Filter states based on selected country
        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.country:
            self.fields['state'].queryset = self.instance.country.state_set.order_by('name')
        else:
            self.fields['state'].queryset = State.objects.none()

# Inline Admin Classes
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'variation', 'quantity', 'price', 'get_total')
    extra = 0
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 1
    readonly_fields = ('created_at',)

# Main Admin Classes
@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'requires_state', 'is_active', 'city_count')
    list_filter = ('is_active', 'requires_state')
    search_fields = ('name', 'code')
    list_editable = ('is_active', 'requires_state')
    ordering = ('name',)
    
    def city_count(self, obj):
        return obj.city_set.count()
    city_count.short_description = 'Cities'

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code', 'is_active', 'city_count')
    list_filter = ('country', 'is_active')
    search_fields = ('name', 'country__name', 'code')
    list_editable = ('is_active',)
    ordering = ('country__name', 'name')
    
    def city_count(self, obj):
        return obj.city_set.count()
    city_count.short_description = 'Cities'

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    form = CityForm
    list_display = ('name', 'country_display', 'state_display', 'shipping_cost', 'is_active')
    list_filter = ('country', 'state', 'is_active')
    search_fields = ('name', 'country__name', 'state__name')
    list_editable = ('shipping_cost', 'is_active')
    ordering = ('country__name', 'state__name', 'name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'country', 'state', 'shipping_cost', 'is_active')
        }),
    )
    
    def country_display(self, obj):
        return obj.country.name
    country_display.short_description = 'Country'
    country_display.admin_order_field = 'country__name'
    
    def state_display(self, obj):
        return obj.state.name if obj.state else "-"
    state_display.short_description = 'State'
    state_display.admin_order_field = 'state__name'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'created_at',
        'user',
        'get_full_name',
        'grand_total',
        'status',
        'payment_status',
        'view_order'
    )
    list_filter = ('status', 'created_at', 'country')
    search_fields = ('order_number', 'user__email', 'first_name', 'last_name')
    readonly_fields = (
        'order_number',
        'user',
        'created_at',
        'updated_at',
        'ip_address',
        'get_full_address'
    )
    inlines = [OrderItemInline, OrderTrackingInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number',
                'user',
                'status',
                'created_at',
                'updated_at',
                'ip_address'
            )
        }),
        ('Customer Information', {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'phone_number'
            )
        }),
        ('Shipping Information', {
            'fields': (
                'address_line1',
                'address_line2',
                'country',
                'state',
                'city',
                'postal_code',
                'get_full_address'
            )
        }),
        ('Order Details', {
            'fields': (
                'order_note',
                'order_total',
                'shipping_cost',
                'tax',
                'grand_total'
            )
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Customer'
    
    def payment_status(self, obj):
        return "COD"  # For future payment method integration
    payment_status.short_description = 'Payment'
    
    def view_order(self, obj):
        return format_html('<a href="/admin/order/order/{}/change/">View</a>', obj.id)
    view_order.short_description = 'Action'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'variation', 'quantity', 'price', 'get_total')
    list_filter = ('order__status',)
    search_fields = ('order__order_number', 'product__name')
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'created_at', 'note_preview')
    list_filter = ('status', 'created_at')
    search_fields = ('order__order_number', 'note')
    readonly_fields = ('created_at',)
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if obj.note else '-'
    note_preview.short_description = 'Note Preview'


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'icon', 'is_active')
        }),
    )


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'rate', 'is_active', 'applies_to_all', 'country_list')
    list_filter = ('is_active', 'applies_to_all')
    list_editable = ('rate', 'is_active', 'applies_to_all')
    filter_horizontal = ('countries',)
    
    def country_list(self, obj):
        if obj.applies_to_all:
            return "All Countries"
        return ", ".join([country.name for country in obj.countries.all()])
    country_list.short_description = 'Applicable Countries'