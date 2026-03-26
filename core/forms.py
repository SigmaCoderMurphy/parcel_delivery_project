from django import forms
from leads.models import Lead

class QuickQuoteForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            'company_name', 'contact_name', 'email', 'phone',
            'business_type', 'address', 'service_area', 
            'delivery_frequency', 'typical_items', 'notes'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company Name'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(416) 555-0123'}),
            'business_type': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Business Address'}),
            'service_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toronto, Mississauga'}),
            'delivery_frequency': forms.Select(attrs={'class': 'form-select'}),
            'typical_items': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'What do you typically deliver?'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional requirements...'}),
        }