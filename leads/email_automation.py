from django.core.mail import send_mail, EmailMultiAlternatives
from django.template import Template, Context
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
                'subject': 'Thank you for your interest in Eastern Logistics!',
                'template': 'email/welcome.html',
                'delay': 0
            },
            {
                'day': 2,
                'subject': 'Your Custom Quote is Ready!',
                'template': 'email/quote_ready.html',
                'delay': 2
            },
            {
                'day': 5,
                'subject': 'Special Offer for GTA Businesses',
                'template': 'email/special_offer.html',
                'delay': 5
            },
            {
                'day': 7,
                'subject': 'Need a Reliable Delivery Partner? Let us help!',
                'template': 'email/followup_1.html',
                'delay': 7
            },
            {
                'day': 10,
                'subject': 'Last Chance: Limited Time Offer',
                'template': 'email/last_chance.html',
                'delay': 10
            }
        ]
    
    def send_welcome_email(self):
        """Send welcome email immediately after lead capture"""
        from core.models import EmailTemplate

        context = {
            'lead': self.lead,
            'company': {
                'name': settings.SITE_NAME,
                'phone': settings.SITE_PHONE,
                'email': settings.SITE_EMAIL,
                'website': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'maps_url': getattr(settings, 'SITE_GOOGLE_BUSINESS_URL', ''),
            },
            'contact_name': self.lead.contact_name,
            'company_name': self.lead.company_name,
        }

        tpl = EmailTemplate.objects.filter(template_type='welcome', is_active=True).first()
        if tpl and (tpl.subject or tpl.body):
            subject = Template(tpl.subject or f'Welcome to {settings.SITE_NAME}!').render(Context(context)).strip()
            body_html = Template(tpl.body or '').render(Context(context))
            text_content = strip_tags(body_html)
            return send_email_notification(
                subject=subject,
                message=text_content,
                recipient_email=self.lead.email,
                html_message=body_html
            )

        html_content = render_to_string('email/welcome.html', context)
        text_content = strip_tags(html_content)
        return send_email_notification(
            subject=f'Welcome to {settings.SITE_NAME}!',
            message=text_content,
            recipient_email=self.lead.email,
            html_message=html_content
        )
    
    def send_quote_email(self):
        """Send quote email when quote is generated"""
        from core.models import EmailTemplate

        quote = self.lead.quotes.last()
        contact_name = self.lead.contact_name

        context = {
            'lead': self.lead,
            'quote': quote,
            'company': {
                'name': settings.SITE_NAME,
                'phone': settings.SITE_PHONE,
                'email': settings.SITE_EMAIL,
                'maps_url': getattr(settings, 'SITE_GOOGLE_BUSINESS_URL', ''),
            },
            'contact_name': contact_name,
            'company_name': self.lead.company_name,
            'quote_number': quote.quote_number if quote else '',
            'valid_until': quote.valid_until if quote else '',
        }

        tpl = EmailTemplate.objects.filter(template_type='quote', is_active=True).first()
        if tpl and (tpl.subject or tpl.body):
            subject = Template(tpl.subject or 'Your Custom Quote is Ready!').render(Context(context)).strip()
            body_html = Template(tpl.body or '').render(Context(context))
            text_content = strip_tags(body_html)

            # Get attachment file if exists
            attachment_file = None
            if quote and quote.pdf_file:
                attachment_file = quote.pdf_file.path

            return send_email_notification(
                subject=subject,
                message=text_content,
                recipient_email=self.lead.email,
                html_message=body_html,
                attachment_file=attachment_file
            )

        html_content = render_to_string('email/quote_ready.html', context)
        text_content = strip_tags(html_content)

        # Get attachment file if exists
        attachment_file = None
        if quote and quote.pdf_file:
            attachment_file = quote.pdf_file.path
        
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
        from core.models import EmailTemplate
        
        for step in self.sequence:
            template_path = step['template']
            # Map existing template files into our settings template types.
            if template_path.endswith('welcome.html'):
                email_type = 'welcome'
            elif template_path.endswith('quote_ready.html'):
                email_type = 'quote'
            else:
                email_type = 'followup'

            tpl = EmailTemplate.objects.filter(template_type=email_type, is_active=True).first()
            subject = tpl.subject if tpl and tpl.subject else step['subject']

            scheduled_email = ScheduledEmail.objects.create(
                lead=self.lead,
                email_type=email_type,
                subject=subject,
                scheduled_date=timezone.now() + timedelta(days=step['delay']),
                template_path=template_path
            )


@shared_task
def send_scheduled_email(scheduled_email_id):
    """Celery task to send scheduled emails"""
    from .models import ScheduledEmail
    from core.models import EmailTemplate
    
    try:
        scheduled_email = ScheduledEmail.objects.get(id=scheduled_email_id)
        
        quote = scheduled_email.lead.quotes.last()
        context = {
            'lead': scheduled_email.lead,
            'company': {
                'name': settings.SITE_NAME,
                'phone': settings.SITE_PHONE,
                'email': settings.SITE_EMAIL,
                'website': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
                'maps_url': getattr(settings, 'SITE_GOOGLE_BUSINESS_URL', ''),
            },
            'contact_name': scheduled_email.lead.contact_name,
            'quote_number': quote.quote_number if quote else '',
            'valid_until': quote.valid_until if quote else '',
            'quote': quote,
        }

        tpl = EmailTemplate.objects.filter(template_type=scheduled_email.email_type, is_active=True).first()
        if not tpl:
            # Backward compatibility for scheduled emails created before we introduced the
            # generic follow-up template types.
            if scheduled_email.template_path.endswith('welcome.html'):
                tpl = EmailTemplate.objects.filter(template_type='welcome', is_active=True).first()
            elif scheduled_email.template_path.endswith('quote_ready.html'):
                tpl = EmailTemplate.objects.filter(template_type='quote', is_active=True).first()
            else:
                tpl = EmailTemplate.objects.filter(template_type='followup', is_active=True).first()

        if tpl and tpl.body:
            subject = Template(tpl.subject or scheduled_email.subject).render(Context(context)).strip()
            html_content = Template(tpl.body).render(Context(context))
            text_content = strip_tags(html_content)
        else:
            html_content = render_to_string(scheduled_email.template_path, context)
            text_content = strip_tags(html_content)
            subject = scheduled_email.subject

        # Use centralized email utility
        email_sent = send_email_notification(
            subject=subject,
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
