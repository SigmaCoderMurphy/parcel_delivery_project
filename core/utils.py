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
    Send new lead notification to admin via email and WhatsApp
    
    Args:
        lead: Lead object
    
    Returns:
        dict: {'email': bool, 'whatsapp': bool}
    """
    # Send email
    subject = f'New Lead: {lead.company_name}'
    message = f"""New lead received from {lead.company_name}
Contact: {lead.contact_name}
Phone: {lead.phone}
Email: {lead.email}
Business Type: {lead.get_business_type_display()}
Service Area: {lead.service_area}"""
    
    email_sent = send_admin_notification(subject, message)
    
    # Send WhatsApp
    whatsapp_sent = send_whatsapp_notification(lead)
    
    return {
        'email': email_sent,
        'whatsapp': whatsapp_sent
    }


def send_whatsapp_notification(lead):
    """Send WhatsApp notification for new lead"""
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