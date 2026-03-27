from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .models import Service, Fleet, Testimonial, FAQ
from leads.models import Lead
from leads.forms import LeadForm
from .utils import send_lead_notification


def handle_lead_form_submission(request, source='website'):
    """
    Centralized lead form handling to reduce duplication
    
    Args:
        request: HTTP request
        source: Lead source (website, contact form, etc.)
    
    Returns:
        tuple: (form_valid: bool, lead: Lead or None)
    """
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = source
            lead.save()
            
            # Send notifications (email + WhatsApp)
            send_lead_notification(lead)
            
            return True, lead
        return False, form
    else:
        return False, LeadForm()


def home(request):
    services = Service.objects.filter(is_featured=True)[:6]
    fleet = Fleet.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_approved=True)[:3]
    faqs = FAQ.objects.filter(is_active=True)[:6]
    
    form_valid, result = handle_lead_form_submission(request, source='website')
    
    if form_valid:
        messages.success(request, 'Thank you for your interest! We will contact you shortly.')
        return redirect('thank_you')
    
    form = result if isinstance(result, LeadForm) else LeadForm()
    
    context = {
        'services': services,
        'fleet': fleet,
        'testimonials': testimonials,
        'faqs': faqs,
        'form': form,
        'active_page': 'home',
    }
    return render(request, 'home.html', context)


def services(request):
    services = Service.objects.all()
    fleet = Fleet.objects.filter(is_active=True)
    
    context = {
        'services': services,
        'fleet': fleet,
        'active_page': 'services',
    }
    return render(request, 'services.html', context)


def about(request):
    testimonials = Testimonial.objects.filter(is_approved=True)
    fleet = Fleet.objects.filter(is_active=True)
    
    context = {
        'testimonials': testimonials,
        'fleet': fleet,
        'active_page': 'about',
    }
    return render(request, 'about.html', context)


def contact(request):
    form_valid, result = handle_lead_form_submission(request, source='contact_form')
    
    if form_valid:
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('thank_you')
    
    form = result if isinstance(result, LeadForm) else LeadForm()
    
    context = {
        'form': form,
        'active_page': 'contact',
    }
    return render(request, 'contact.html', context)


def thank_you(request):
    return render(request, 'thank_you.html')