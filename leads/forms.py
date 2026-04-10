from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from .models import Lead, FollowUp, CommunicationLog, Quote

class LeadForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    
    class Meta:
        model = Lead
        fields = ['company_name', 'contact_name', 'email', 'phone', 'business_type', 'address', 'service_area', 'delivery_frequency', 'typical_items', 'notes']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your company name',
                'required': 'required'
            }),
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name',
                'required': 'required'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com',
                'required': 'required'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '416-710-0361',
                'required': 'required'
            }),
            'business_type': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Your business address',
                'required': 'required'
            }),
            'service_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Toronto, Mississauga, GTA',
                'required': 'required'
            }),
            'delivery_frequency': forms.Select(attrs={
                'class': 'form-select',
                'id': 'delivery_frequency'
            }),
            'typical_items': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'e.g., clothing, electronics, furniture parts...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us more about your delivery needs...'
            }),
        }

class FollowUpForm(forms.ModelForm):
    class Meta:
        model = FollowUp
        fields = ['followup_type', 'scheduled_date', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'followup_type': forms.Select(attrs={'class': 'form-select'}),
        }

class CommunicationLogForm(forms.ModelForm):
    class Meta:
        model = CommunicationLog
        fields = ['communication_type', 'direction', 'subject', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'communication_type': forms.Select(attrs={'class': 'form-select'}),
            'direction': forms.Select(attrs={'class': 'form-select'}),
        }

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['amount', 'valid_until', 'terms', 'status']
        widgets = {
            'valid_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'terms': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }