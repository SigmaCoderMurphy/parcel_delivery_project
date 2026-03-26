from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Service, Fleet, Testimonial, FAQ
from leads.models import Lead
from leads.forms import LeadForm
from .utils import send_whatsapp_notification

def home(request):
    services = Service.objects.filter(is_featured=True)[:6]
    fleet = Fleet.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_approved=True)[:3]
    faqs = FAQ.objects.filter(is_active=True)[:6]
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = 'website'
            lead.save()
            
            # Send email notification
            try:
                send_mail(
                    f'New Lead: {lead.company_name}',
                    f'New lead received from {lead.company_name}\nContact: {lead.contact_name}\nPhone: {lead.phone}\nEmail: {lead.email}',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.SITE_EMAIL],
                    fail_silently=True,
                )
            except:
                pass
            
            # Send WhatsApp notification (if configured)
            send_whatsapp_notification(lead)
            
            messages.success(request, 'Thank you for your interest! We will contact you shortly.')
            return redirect('thank_you')
    else:
        form = LeadForm()
    
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
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = 'website'
            lead.save()
            
            messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
            return redirect('thank_you')
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'active_page': 'contact',
    }
    return render(request, 'contact.html', context)

def thank_you(request):
    return render(request, 'thank_you.html')