from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from celery import shared_task
from datetime import timedelta
from core.utils import send_email_notification
import time


class EmailFollowUpSystem:
    def __init__(self, lead):
        self.lead = lead
        self.sequence = [
            {
                'day': 0,
                'subject': 'Thank you for your interest in GTA Parcel Delivery!',
                'template': 'emails/welcome.html',
                'delay': 0
            },
            {
                'day': 2,
                'subject': 'Your Custom Quote is Ready!',
                'template': 'emails/quote_ready.html',
                'delay': 2
            },
            {
                'day': 5,
                'subject': 'Special Offer for GTA Businesses',
                'template': 'emails/special_offer.html',
                'delay': 5
            },
            {
                'day': 7,
                'subject': 'Need a Reliable Delivery Partner? Let us help!',
                'template': 'emails/followup_1.html',
                'delay': 7
            },
            {
                'day': 10,
                'subject': 'Last Chance: Limited Time Offer',
                'template': 'emails/last_chance.html',
                'delay': 10
            }
        ]
    
    def send_welcome_email(self):
        """Send welcome email immediately after lead capture"""
        context = {
            'lead': self.lead,
            'company': {
                'name': 'GTA Parcel Delivery',
                'phone': settings.SITE_PHONE,
                'email': settings.SITE_EMAIL,
                'website': settings.SITE_URL
            }
        }
        
        html_content = render_to_string('emails/welcome.html', context)
        text_content = strip_tags(html_content)
        
        return send_email_notification(
            subject='Welcome to GTA Parcel Delivery!',
            message=text_content,
            recipient_email=self.lead.email,
            html_message=html_content
        )
    
    def send_quote_email(self):
        """Send quote email when quote is generated"""
        context = {
            'lead': self.lead,
            'quote': self.lead.quotes.last(),
            'company': {
                'name': 'GTA Parcel Delivery',
                'phone': settings.SITE_PHONE
            }
        }
        
        html_content = render_to_string('emails/quote_ready.html', context)
        text_content = strip_tags(html_content)
        
        # Get attachment file if exists
        attachment_file = None
        if self.lead.quotes.last() and self.lead.quotes.last().pdf_file:
            attachment_file = self.lead.quotes.last().pdf_file.path
        
        return send_email_notification(
            subject='Your Custom Quote is Ready!',
            message=text_content,
            recipient_email=self.lead.email,
            html_message=html_content,
            attachment_file=attachment_file
        )
    
    def schedule_follow_up_sequence(self):
        """Schedule entire follow-up sequence"""
        from .models import ScheduledEmail
        
        for step in self.sequence:
            scheduled_email = ScheduledEmail.objects.create(
                lead=self.lead,
                email_type=step['template'].replace('emails/', '').replace('.html', ''),
                subject=step['subject'],
                scheduled_date=timezone.now() + timedelta(days=step['delay']),
                template_path=step['template']
            )


@shared_task
def send_scheduled_email(scheduled_email_id):
    """Celery task to send scheduled emails"""
    from .models import ScheduledEmail
    
    try:
        scheduled_email = ScheduledEmail.objects.get(id=scheduled_email_id)
        
        context = {
            'lead': scheduled_email.lead,
            'company': {
                'name': 'GTA Parcel Delivery',
                'phone': settings.SITE_PHONE,
                'email': settings.SITE_EMAIL
            }
        }
        
        html_content = render_to_string(scheduled_email.template_path, context)
        text_content = strip_tags(html_content)
        
        # Use centralized email utility
        email_sent = send_email_notification(
            subject=scheduled_email.subject,
            message=text_content,
            recipient_email=scheduled_email.lead.email,
            html_message=html_content
        )
        
        if email_sent:
            scheduled_email.sent = True
            scheduled_email.sent_at = timezone.now()
            scheduled_email.save()
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending scheduled email {scheduled_email_id}: {e}")
