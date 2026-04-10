from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

try:
    # Twilio is optional at runtime (credentials can be empty).
    from twilio.rest import Client
except ImportError:  # pragma: no cover
    Client = None


def send_email_notification(subject, message, recipient_email, html_message=None, attachment_file=None):
    """
    Centralized email sending utility to avoid duplication
    
    Args:
        subject: Email subject
        message: Plain text message
        recipient_email: Email address to send to
        html_message: Optional HTML version of message
        attachment_file: Optional file to attach
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if html_message:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            msg.attach_alternative(html_message, "text/html")
            
            if attachment_file:
                msg.attach_file(attachment_file)
            
            msg.send(fail_silently=False)
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False,
            )
        
        logger.info(f"Email sent successfully to {recipient_email}: {subject}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_admin_notification(subject, message):
    """
    Send notification to admin email
    
    Args:
        subject: Email subject
        message: Email message
    
    Returns:
        bool: True if sent successfully
    """
    return send_email_notification(subject, message, settings.SITE_EMAIL)


def send_lead_notification(lead):
    """
    Send notifications for new lead:
    1. Admin notification via email + WhatsApp
    2. Customer confirmation email via Brevo API (automated)
    
    Note: Quote and follow-up emails are sent manually by staff
    
    Args:
        lead: Lead object
    
    Returns:
        dict: {'admin_email': bool, 'whatsapp': bool, 'customer_confirmation': bool}
    """
    try:
        # Send email to admin - fail silently to not block form submission
        subject = f'New Lead: {lead.company_name}'
        message = f"""New lead received from {lead.company_name}
Contact: {lead.contact_name}
Phone: {lead.phone}
Email: {lead.email}
Business Type: {lead.get_business_type_display()}
Service Area: {lead.service_area}"""
        
        admin_email_sent = send_admin_notification(subject, message)
        
        # Send WhatsApp silently - don't block if it fails
        whatsapp_sent = False
        try:
            whatsapp_sent = send_whatsapp_notification(lead)
        except Exception as e:
            logger.warning(f"WhatsApp notification failed for lead {lead.id}: {str(e)}")
        
        # Send customer confirmation email via Brevo - don't block if it fails
        customer_confirmation_sent = False
        try:
            from leads.brevo_service import send_lead_confirmation_email
            customer_confirmation_sent = send_lead_confirmation_email(lead)
        except Exception as e:
            logger.warning(f"Brevo confirmation email failed for lead {lead.id}: {str(e)}")
        
        return {
            'admin_email': admin_email_sent,
            'whatsapp': whatsapp_sent,
            'customer_confirmation': customer_confirmation_sent
        }
    except Exception as e:
        logger.error(f"Lead notification error for {lead.id}: {str(e)}")
        return {'admin_email': False, 'whatsapp': False, 'customer_confirmation': False}


def send_whatsapp_notification(lead):
    """Send WhatsApp notification for new lead"""
    if not getattr(settings, "STAFF_WHATSAPP_NUMBER", ""):
        logger.warning("STAFF_WHATSAPP_NUMBER not configured")
        return False
    if not all([settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NUMBER]):
        logger.warning("Twilio credentials not configured")
        return False
    if Client is None:  # pragma: no cover
        logger.warning("Twilio client not available (is `twilio` installed?)")
        return False
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = f"""🔔 *New Lead Alert!*
        
Company: {lead.company_name}
Contact: {lead.contact_name}
Phone: {lead.phone}
Email: {lead.email}
Type: {lead.get_business_type_display()}
Area: {lead.service_area}

View in dashboard: {settings.SITE_URL}/dashboard/leads/{lead.id}/"""
        
        message = client.messages.create(
            body=message,
            from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
            to=f'whatsapp:{settings.STAFF_WHATSAPP_NUMBER}'  # Add this to settings
        )
        
        logger.info(f"WhatsApp notification sent for lead {lead.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp: {e}")
        return False


def send_followup_reminder(followup):
    """Send reminder for scheduled follow-up"""
    # Implementation for email/SMS reminders
    pass


# ==================== ORDERING UTILITIES ====================

def normalize_service_orders():
    """
    Ensure all active services have unique, sequential order numbers (1, 2, 3, ...).
    Automatically reassigns orders if there are duplicates or gaps.
    """
    from .models import Service
    
    # Get all active services sorted by current order, then by ID for stability
    active_services = Service.objects.filter(is_active=True).order_by('order', 'id')
    
    # Reassign orders sequentially
    for index, service in enumerate(active_services, start=1):
        if service.order != index:
            service.order = index
            service.save(update_fields=['order'])


def normalize_fleet_orders():
    """
    Ensure all active fleet vehicles have unique, sequential order numbers (1, 2, 3, ...).
    Automatically reassigns orders if there are duplicates or gaps.

    Uses bulk_update instead of per-row save() so we do not re-enter Fleet.save()
    (which would recurse and could yield inconsistent results while mutating orders).
    """
    from .models import Fleet

    active_fleet = list(Fleet.objects.filter(is_active=True).order_by('order', 'id'))
    to_update = []
    for index, vehicle in enumerate(active_fleet, start=1):
        if vehicle.order != index:
            vehicle.order = index
            to_update.append(vehicle)
    if to_update:
        Fleet.objects.bulk_update(to_update, ['order'])


def get_next_service_order():
    """Get the next available order number for a service"""
    from .models import Service
    
    active_count = Service.objects.filter(is_active=True).count()
    return active_count + 1


def get_next_fleet_order():
    """Get the next available order number for a fleet vehicle"""
    from .models import Fleet
    
    active_count = Fleet.objects.filter(is_active=True).count()
    return active_count + 1


def check_order_conflict(model_class, order_number, is_active, exclude_id=None):
    """
    Check if a given order number conflicts with existing active items.
    
    Args:
        model_class: Service or Fleet model class
        order_number: The order number to check
        is_active: Boolean indicating if item is active
        exclude_id: ID to exclude from check (for editing)
    
    Returns:
        bool: True if conflict exists, False otherwise
    """
    if not is_active:
        return False  # Inactive items don't have ordering constraints
    
    query = model_class.objects.filter(is_active=True, order=order_number)
    
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    return query.exists()