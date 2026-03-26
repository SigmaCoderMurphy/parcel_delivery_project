from django.conf import settings
import logging

logger = logging.getLogger(__name__)

try:
    # Twilio is optional at runtime (credentials can be empty).
    from twilio.rest import Client
except ImportError:  # pragma: no cover
    Client = None

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
        
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp: {e}")
        return False

def send_followup_reminder(followup):
    """Send reminder for scheduled follow-up"""
    # Implementation for email/SMS reminders
    pass