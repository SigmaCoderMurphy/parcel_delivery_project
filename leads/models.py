from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime

class Lead(models.Model):
    LEAD_STATUS = [
        ('new', 'New Lead'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('proposal', 'Proposal Sent'),
        ('negotiation', 'In Negotiation'),
        ('won', 'Won - Customer'),
        ('lost', 'Lost'),
    ]
    
    LEAD_SOURCE = [
        ('website', 'Website Leads'),
        ('call', 'Phone Call'),
        ('whatsapp', 'WhatsApp'),
        ('google', 'Google Business'),
        ('referral', 'Referral'),
        ('telemarketing', 'Telemarketing'),
        ('social_media', 'Social Media'),
        ('other', 'Other'),
    ]
    
    BUSINESS_TYPES = [
        ('ecommerce', 'E-commerce Seller'),
        ('retail', 'Small Retailer'),
        ('pharmacy', 'Pharmacy'),
        ('warehouse', 'Warehouse'),
        ('furniture', 'Furniture Store'),
        ('office', 'Office/Service Provider'),
        ('other', 'Other'),
    ]
    
    # Contact Information
    company_name = models.CharField(max_length=200)
    contact_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, blank=True)
    
    # Business Information
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    website = models.URLField(blank=True)
    address = models.TextField()
    service_area = models.CharField(max_length=200, help_text="Delivery areas needed")
    
    # Lead Information
    status = models.CharField(max_length=20, choices=LEAD_STATUS, default='new')
    source = models.CharField(max_length=20, choices=LEAD_SOURCE, default='website')
    
    # Delivery Requirements
    delivery_frequency = models.CharField(max_length=100, blank=True, help_text="e.g., Daily, Weekly, On-demand")
    typical_items = models.TextField(blank=True, help_text="Types of items to deliver")
    monthly_volume = models.IntegerField(null=True, blank=True, help_text="Estimated monthly deliveries")
    
    # Notes
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Internal staff only")
    
    # Tracking
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    
    # Google Business Profile
    google_review_requested = models.BooleanField(default=False)
    google_review_given = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.contact_name}"
    
    def get_status_color(self):
        colors = {
            'new': 'primary',
            'contacted': 'info',
            'qualified': 'success',
            'proposal': 'warning',
            'negotiation': 'warning',
            'won': 'success',
            'lost': 'danger',
        }
        return colors.get(self.status, 'secondary')

class FollowUp(models.Model):
    FOLLOW_UP_TYPE = [
        ('call', 'Phone Call'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('meeting', 'In-person Meeting'),
        ('quote', 'Quote Sent'),
        ('other', 'Other'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='followups')
    followup_type = models.CharField(max_length=20, choices=FOLLOW_UP_TYPE)
    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField()
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.lead.company_name} - {self.get_followup_type_display()} - {self.scheduled_date}"

class CommunicationLog(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='communications')
    communication_type = models.CharField(max_length=20, choices=FollowUp.FOLLOW_UP_TYPE)
    direction = models.CharField(max_length=10, choices=[('in', 'Inbound'), ('out', 'Outbound')])
    subject = models.CharField(max_length=200)
    content = models.TextField()
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class Quote(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='quotes')
    quote_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_until = models.DateField()
    terms = models.TextField()
    pdf_file = models.FileField(upload_to='quotes/', blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"Quote {self.quote_number} - {self.lead.company_name}"
    

# Add these new models after your existing models:

class CallLog(models.Model):
    CALL_TYPES = [
        ('incoming', 'Incoming Call'),
        ('outgoing', 'Outgoing Call'),
        ('missed', 'Missed Call'),
    ]
    
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True, related_name='calls')
    call_sid = models.CharField(max_length=100, unique=True)
    caller_number = models.CharField(max_length=20)
    call_duration = models.IntegerField(help_text="Duration in seconds", default=0)
    call_notes = models.TextField(blank=True)
    recording_url = models.URLField(blank=True, null=True)
    call_type = models.CharField(max_length=20, choices=CALL_TYPES, default='incoming')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Call from {self.caller_number} - {self.created_at}"

class CallAnalysis(models.Model):
    call = models.OneToOneField(CallLog, on_delete=models.CASCADE, related_name='analysis')
    sentiment_score = models.CharField(max_length=20, choices=[
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ])
    keywords_extracted = models.CharField(max_length=500, blank=True)
    conversion_likelihood = models.IntegerField(default=0, help_text="0-100")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for call {self.call.call_sid}"

class ScheduledEmail(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='scheduled_emails')
    email_type = models.CharField(max_length=50)
    subject = models.CharField(max_length=200)
    scheduled_date = models.DateTimeField()
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    template_path = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"Email for {self.lead.company_name} - {self.email_type}"