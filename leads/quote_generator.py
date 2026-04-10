import os
from io import BytesIO
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from django.conf import settings
from django.template.loader import render_to_string
import uuid

class QuoteGenerator:
    def __init__(self, lead, quote):
        self.lead = lead
        self.quote = quote
        self.quote_number = quote.quote_number
        
    def generate_pdf_reportlab(self):
        """Generate PDF using ReportLab"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Company Header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        story.append(Paragraph(getattr(settings, "SITE_NAME", "Eastern Logistics").upper(), header_style))
        
        # Quote Info
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666')
        )
        
        story.append(Paragraph(f"Quote Number: {self.quote.quote_number}", info_style))
        story.append(Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", info_style))
        story.append(Paragraph(f"Valid Until: {self.quote.valid_until.strftime('%B %d, %Y')}", info_style))
        story.append(Spacer(1, 20))
        
        # Company Info
        story.append(Paragraph("<b>BILL TO:</b>", styles['Normal']))
        story.append(Paragraph(self.lead.company_name, styles['Normal']))
        story.append(Paragraph(self.lead.contact_name, styles['Normal']))
        story.append(Paragraph(self.lead.address.replace('\n', ', '), styles['Normal']))
        story.append(Paragraph(f"Phone: {self.lead.phone}", styles['Normal']))
        story.append(Paragraph(f"Email: {self.lead.email}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Quote Details Table
        data = [
            ['Service Description', 'Quantity', 'Unit Price', 'Total'],
            ['Delivery Services', '1', f'${self.quote.amount}', f'${self.quote.amount}'],
        ]
        
        table = Table(data, colWidths=[250, 80, 80, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Delivery Requirements
        story.append(Paragraph("<b>DELIVERY REQUIREMENTS:</b>", styles['Normal']))
        story.append(Paragraph(f"Business Type: {self.lead.get_business_type_display()}", styles['Normal']))
        story.append(Paragraph(f"Service Area: {self.lead.service_area}", styles['Normal']))
        if self.lead.delivery_frequency:
            story.append(Paragraph(f"Frequency: {self.lead.delivery_frequency}", styles['Normal']))
        if self.lead.typical_items:
            story.append(Paragraph(f"Items: {self.lead.typical_items}", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Terms and Conditions
        story.append(Paragraph("<b>TERMS & CONDITIONS:</b>", styles['Normal']))
        story.append(Paragraph(self.quote.terms, styles['Normal']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>PAYMENT TERMS:</b>", styles['Normal']))
        story.append(Paragraph("Net 30 days from invoice date", styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Signature
        story.append(Paragraph("_________________________", styles['Normal']))
        story.append(Paragraph("Authorized Signature", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Save to file
        filename = f"quotes/quote_{self.quote_number}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(buffer.getvalue())
        
        return filename
    
    def generate_pdf_html(self):
        """Generate PDF using HTML template"""
        # `xhtml2pdf` is only needed for the HTML->PDF path. Keep it optional so
        # ReportLab-based generation still works when `xhtml2pdf` isn't installed.
        try:
            from xhtml2pdf import pisa
        except ModuleNotFoundError:
            return None

        context = {
            'quote': self.quote,
            'lead': self.lead,
            'company': {
                'name': getattr(settings, 'SITE_NAME', 'Eastern Logistics'),
                'phone': getattr(settings, 'SITE_PHONE', '416-710-0361'),
                'email': getattr(settings, 'SITE_EMAIL', 'shahzaibsadiq256@gmail.com'),
                'address': getattr(settings, 'SITE_ADDRESS', '828 Eastern Ave, Toronto, ON M4L 1A1, Canada'),
                'website': getattr(settings, 'SITE_URL', ''),
            },
            'date': datetime.now(),
        }

        html_string = render_to_string('quote_template.html', context)
        
        filename = f"quotes/quote_{self.quote_number}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as pdf:
            pisa_status = pisa.CreatePDF(html_string, dest=pdf)
            
        return filename if not pisa_status.err else None