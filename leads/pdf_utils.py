"""
Centralized PDF generation utilities to reduce code duplication
"""
from django.contrib import messages
from .quote_generator import QuoteGenerator
import logging

logger = logging.getLogger(__name__)


def generate_and_save_quote_pdf(lead, quote):
    """
    Centralized function to generate PDF and save to quote object
    
    Args:
        lead: Lead object
        quote: Quote object
    
    Returns:
        dict: {'success': bool, 'message': str, 'pdf_filename': str or None}
    """
    try:
        generator = QuoteGenerator(lead, quote)
        # Prefer the HTML template PDF so business-specific quote layout is used.
        pdf_filename = generator.generate_pdf_html() or generator.generate_pdf_reportlab()
        
        if pdf_filename:
            quote.pdf_file = pdf_filename
            quote.status = 'sent'
            quote.save()
            
            logger.info(f"PDF generated successfully for quote {quote.quote_number}")
            return {
                'success': True,
                'message': f"Quote {quote.quote_number} PDF generated successfully",
                'pdf_filename': pdf_filename
            }
        else:
            logger.warning(f"PDF generation returned None for quote {quote.quote_number}")
            return {
                'success': False,
                'message': f"Quote PDF generation failed. Please check logs.",
                'pdf_filename': None
            }
            
    except Exception as e:
        logger.error(f"Error generating PDF for quote {quote.quote_number}: {str(e)}")
        return {
            'success': False,
            'message': f"Error during PDF generation: {str(e)}",
            'pdf_filename': None
        }


def send_quote_pdf_email(lead, quote, email_system=None):
    """
    Send generated quote PDF via email
    
    Args:
        lead: Lead object
        quote: Quote object
        email_system: Optional EmailFollowUpSystem instance
    
    Returns:
        bool: True if sent successfully
    """
    try:
        if email_system is None:
            from .email_automation import EmailFollowUpSystem
            email_system = EmailFollowUpSystem(lead)
        
        email_system.send_quote_email()
        logger.info(f"Quote email sent for {quote.quote_number}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending quote email: {str(e)}")
        return False
