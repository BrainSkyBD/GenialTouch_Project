from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def send_order_confirmation_email(order, recipient_email=None, send_to_admins=False):
    """
    Send order confirmation email with HTML template
    """
    try:
        # Common context
        context = {
            'order': order,
            'site_url': settings.SITE_URL,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL,
            'current_year': timezone.now().year,
            'currency_symbol': '৳',
        }
        
        # Determine template, subject, and recipients
        if send_to_admins:
            # Admin template with admin-specific URLs
            context.update({
                'admin_order_url': f"{settings.SITE_URL}/admin/orders/order/{order.id}/change/",
                'admin_edit_url': f"{settings.SITE_URL}/admin/orders/order/{order.id}/change/",
                'admin_invoice_url': f"{settings.SITE_URL}/admin/orders/order/{order.id}/invoice/",
                'admin_dashboard_url': f"{settings.SITE_URL}/admin/",
                'admin_orders_url': f"{settings.SITE_URL}/admin/orders/order/",
            })
            
            template_name = 'emails/admin_order_confirmation.html'
            recipients = settings.ADMIN_EMAILS
            subject = f"[ADMIN] New Order #{order.order_number} - {order.get_full_name}"
            
        else:
            # Customer template
            context.update({
                'track_order_url': f"{settings.SITE_URL}/order/track/{order.order_number}/",
            })
            
            template_name = 'emails/order_confirmation.html'
            
            if recipient_email:
                recipients = [recipient_email]
            elif order.email:
                recipients = [order.email]
            else:
                logger.warning(f"No recipient for order {order.order_number}")
                return False
            
            subject = f"Order Confirmation #{order.order_number}"
        
        # Render HTML template
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=[settings.SUPPORT_EMAIL],
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        recipient_list = ', '.join(recipients)
        logger.info(f"{'Admin' if send_to_admins else 'Customer'} email sent for order {order.order_number} to {recipient_list}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False


def send_order_status_update_email(order, old_status, new_status, notify_admins=False):
    """
    Send email when order status changes
    """
    try:
        context = {
            'order': order,
            'old_status': old_status,
            'new_status': new_status,
            'track_order_url': f"{settings.SITE_URL}/order/track/{order.order_number}/",
            'site_url': settings.SITE_URL,
            'site_name': settings.SITE_NAME,
            'support_email': settings.SUPPORT_EMAIL,
            'current_year': timezone.now().year,
            'currency_symbol': '৳',
        }
        
        if notify_admins:
            # Admin status update template
            template_name = 'emails/admin_order_status_update.html'
            recipients = settings.ADMIN_EMAILS
            subject = f"[ADMIN] Order #{order.order_number} Status: {order.get_status_display()}"
            
            # Add admin URLs
            context.update({
                'admin_order_url': f"{settings.SITE_URL}/admin/orders/order/{order.id}/change/",
            })
        else:
            # Customer status update template (using same as before)
            template_name = 'emails/order_status_update.html'
            
            if not order.email:
                return False
            recipients = [order.email]
            subject = f"Order #{order.order_number} Status Update: {order.get_status_display()}"
        
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
        )
        
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send status update email: {str(e)}")
        return False


# Convenience functions
def notify_customer_new_order(order):
    """Send order confirmation to customer"""
    return send_order_confirmation_email(order, send_to_admins=False)


def notify_admins_new_order(order):
    """Send order notification to all admins"""
    return send_order_confirmation_email(order, send_to_admins=True)


def notify_both_new_order(order):
    """Send notifications to both customer and admins"""
    customer_sent = notify_customer_new_order(order)
    admin_sent = notify_admins_new_order(order)
    return customer_sent and admin_sent