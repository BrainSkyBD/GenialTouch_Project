from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderTrackingTableNew



@receiver(post_save, sender=OrderTrackingTableNew)
def send_order_status_email(sender, instance, created, **kwargs):
    if created:
        subject = f"Order {instance.order.order_number} status update"
        message = render_to_string('orders/email/order_status_update.txt', {
            'order': instance.order,
            'status': instance.get_status_display(),
            'note': instance.note,
        })
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.order.email],
            fail_silently=False,
        )