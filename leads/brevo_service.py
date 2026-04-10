"""
Brevo Email Service - For automated confirmation emails ONLY
All other emails (quotes, follow-ups) are sent manually by staff
"""

import logging
import httpx
import json
from django.conf import settings
from django.template import Template, Context
from django.utils.html import strip_tags
from core.models import EmailTemplate

logger = logging.getLogger(__name__)

# Brevo API endpoint
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_lead_confirmation_email(lead):
    """
    Send confirmation email to customer via Brevo API
    Used ONLY for automatic lead form submission confirmations
    
    Args:
        lead: Lead object from database
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    
    # Check if Brevo API key is configured
    if not settings.BREVO_API_KEY:
        logger.warning("Brevo API key not configured. Confirmation email not sent.")
        return False
    
    try:
        delivery_frequency = (
            getattr(lead, "delivery_frequency", None) or "Not specified"
        )
        context = {
            "lead": lead,
            "contact_name": lead.contact_name,
            "company_name": lead.company_name,
            "company": {
                "name": settings.SITE_NAME,
                "phone": settings.SITE_PHONE,
                "email": settings.SITE_EMAIL,
                "website": getattr(settings, "SITE_URL", "http://127.0.0.1:8000"),
                "maps_url": getattr(settings, "SITE_GOOGLE_BUSINESS_URL", ""),
            },
        }

        # Use dashboard-managed welcome template when available.
        tpl = EmailTemplate.objects.filter(template_type="welcome", is_active=True).first()
        if tpl and (tpl.subject or tpl.body):
            subject = Template(tpl.subject or f"Welcome to {settings.SITE_NAME}!").render(Context(context)).strip()
            html_content = Template(tpl.body or "").render(Context(context))
            text_content = strip_tags(html_content)
        else:
            subject = f"Thank You for Your Interest - {settings.SITE_NAME}"
            html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2>Thank You for Your Inquiry, {lead.contact_name}!</h2>
                    
                    <p>We have received your delivery service inquiry for <strong>{lead.company_name}</strong>.</p>
                    
                    <p>Our team at {settings.SITE_NAME} will review your request shortly and contact you to discuss:</p>
                    <ul>
                        <li>Your delivery requirements</li>
                        <li>Service area coverage</li>
                        <li>Custom pricing for your needs</li>
                    </ul>
                    
                    <p><strong>Your Submission Details:</strong></p>
                    <ul>
                        <li>Company: {lead.company_name}</li>
                        <li>Service Area: {lead.service_area}</li>
                        <li>Business Type: {lead.get_business_type_display()}</li>
                        <li>Delivery Frequency: {delivery_frequency}</li>
                    </ul>
                    
                    <p>We typically respond within 24-48 hours during business hours. If you need immediate assistance, 
                    feel free to call us at <strong>{settings.SITE_PHONE}</strong>.</p>
                    
                    <p>Best regards,<br><strong>The {settings.SITE_NAME} Team</strong></p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #666;">
                        This is an automated confirmation email. Please do not reply directly to this email.
                        For inquiries, please contact us at {settings.SITE_EMAIL}.
                    </p>
                </div>
            </body>
        </html>
        """

            text_content = f"""
Thank You for Your Inquiry, {lead.contact_name}!

We have received your delivery service inquiry for {lead.company_name}.

Our team at {settings.SITE_NAME} will review your request shortly and contact you to discuss:
- Your delivery requirements
- Service area coverage
- Custom pricing for your needs

Your Submission Details:
- Company: {lead.company_name}
- Service Area: {lead.service_area}
- Business Type: {lead.get_business_type_display()}
- Delivery Frequency: {delivery_frequency}

We typically respond within 24-48 hours during business hours. If you need immediate assistance, 
feel free to call us at {settings.SITE_PHONE}.

Best regards,
The {settings.SITE_NAME} Team

---
This is an automated confirmation email. Please do not reply directly to this email.
For inquiries, please contact us at {settings.SITE_EMAIL}.
        """
        
        # Prepare email payload following Brevo API specification
        email_payload = {
            "sender": {
                "email": settings.BREVO_SENDER_EMAIL,
                "name": settings.BREVO_SENDER_NAME
            },
            "to": [{
                "email": lead.email,
                "name": lead.contact_name
            }],
            "subject": subject,
            "htmlContent": html_content,
            "textContent": text_content
        }
        
        # Send request to Brevo API
        headers = {
            "api-key": settings.BREVO_API_KEY,
            "Content-Type": "application/json"
        }
        
        with httpx.Client() as client:
            response = client.post(BREVO_API_URL, json=email_payload, headers=headers, timeout=30.0)
            response.raise_for_status()
        
        logger.info(f"Confirmation email sent successfully to {lead.email} (Lead ID: {lead.id})")
        logger.debug(f"Brevo API Response: {response.status_code}")
        
        return True
        
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code if e.response is not None else "unknown"
        response_text = e.response.text if e.response is not None else str(e)
        logger.error(
            f"Brevo API HTTP error sending confirmation email to {lead.email}: {status_code} - {response_text}"
        )
        return False
    except httpx.TimeoutException as e:
        logger.error(f"Brevo API timeout sending confirmation email to {lead.email}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending confirmation email to {lead.email}: {str(e)}")
        return False
