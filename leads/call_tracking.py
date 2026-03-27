from django.db import models
from django.utils import timezone
import phonenumbers
from phonenumbers import carrier, geocoder, timezone as phone_timezone
import uuid

class CallTrackingManager:
    def __init__(self):
        self.tracking_numbers = {}
        
    def generate_tracking_number(self, lead_id, source):
        """Generate unique tracking phone number for each lead source"""
        # In production, integrate with Twilio to get actual phone numbers
        tracking_id = str(uuid.uuid4())[:8]
        tracking_number = f"+1 (416) 555-{tracking_id}"
        
        return {
            'tracking_id': tracking_id,
            'tracking_number': tracking_number,
            'lead_id': lead_id,
            'source': source,
            'created_at': timezone.now()
        }
    
    def log_call(self, lead, call_duration, call_notes, recording_url=None):
        """Log incoming/outgoing call"""
        from .models import CallLog
        
        call_log = CallLog.objects.create(
            lead=lead,
            call_sid=str(uuid.uuid4()),
            caller_number=lead.phone,
            call_duration=call_duration,
            call_notes=call_notes,
            recording_url=recording_url,
            call_type='incoming' if call_notes.startswith('Incoming') else 'outgoing'
        )
        
        # Update lead last contacted
        lead.last_contacted = timezone.now()
        lead.save()
        
        return call_log
    
    def analyze_call(self, call_log):
        """Analyze call for conversion insights"""
        from .models import CallAnalysis
        
        analysis = CallAnalysis.objects.create(
            call=call_log,
            sentiment_score=self.analyze_sentiment(call_log.call_notes),
            keywords_extracted=self.extract_keywords(call_log.call_notes),
            conversion_likelihood=self.calculate_conversion_likelihood(call_log)
        )
        
        return analysis
    
    def analyze_sentiment(self, text):
        """Basic sentiment analysis"""
        positive_words = ['interested', 'yes', 'great', 'perfect', 'schedule', 'quote']
        negative_words = ['no', 'not interested', 'expensive', 'busy', 'later']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        return 'neutral'
    
    def extract_keywords(self, text):
        """Extract key phrases from call notes"""
        keywords = []
        important_terms = ['price', 'discount', 'schedule', 'urgent', 'today', 'tomorrow']
        
        text_lower = text.lower()
        for term in important_terms:
            if term in text_lower:
                keywords.append(term)
        
        return ', '.join(keywords)
    
    def calculate_conversion_likelihood(self, call_log):
        """Calculate likelihood of conversion based on call"""
        score = 50  # Base score
        
        # Positive indicators
        if 'interested' in call_log.call_notes.lower():
            score += 20
        if 'quote' in call_log.call_notes.lower():
            score += 15
        if call_log.call_duration > 300:  # Longer than 5 minutes
            score += 10
            
        # Negative indicators
        if 'not interested' in call_log.call_notes.lower():
            score -= 30
        if call_log.call_duration < 60:  # Very short call
            score -= 20
            
        return min(max(score, 0), 100)

# Add to leads/models.py
class CallLog(models.Model):
    CALL_TYPES = [
        ('incoming', 'Incoming Call'),
        ('outgoing', 'Outgoing Call'),
        ('missed', 'Missed Call'),
    ]
    
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='calls')
    call_sid = models.CharField(max_length=100, unique=True)
    caller_number = models.CharField(max_length=20)
    call_duration = models.IntegerField(help_text="Duration in seconds")
    call_notes = models.TextField()
    recording_url = models.URLField(blank=True, null=True)
    call_type = models.CharField(max_length=20, choices=CALL_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class CallAnalysis(models.Model):
    call = models.OneToOneField(CallLog, on_delete=models.CASCADE)
    sentiment_score = models.CharField(max_length=20, choices=[
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ])
    keywords_extracted = models.CharField(max_length=500, blank=True)
    conversion_likelihood = models.IntegerField(default=0, help_text="0-100")
    created_at = models.DateTimeField(auto_now_add=True)