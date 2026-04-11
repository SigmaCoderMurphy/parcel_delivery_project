from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings as django_settings
from django.http import HttpResponse
from .models import Service, Fleet, Testimonial, FAQ
from .service_defaults import ensure_default_services
from leads.models import Lead
from leads.forms import LeadForm
from leads.source_utils import canonical_source
from .utils import send_lead_notification
import logging

logger = logging.getLogger(__name__)


def handle_lead_form_submission(request, source='website'):
    """
    Centralized lead form handling to reduce duplication
    Non-blocking: saves lead first, sends notifications asynchronously
    
    Args:
        request: HTTP request
        source: Lead source (website, contact form, etc.)
    
    Returns:
        tuple: (form_valid: bool, result: Lead or LeadForm)
    """
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = canonical_source(source)
            lead.save()
            
            # Send notifications in background (non-blocking)
            # Use try-except to not block form submission if notifications fail
            try:
                send_lead_notification(lead)
            except Exception as e:
                logger.warning(f"Notification failed for lead {lead.id}: {str(e)}")
            
            return True, lead
        return False, form
    else:
        return False, LeadForm()


def home(request):
    services = Service.objects.filter(is_active=True, is_featured=True)[:6]
    featured_fleet_qs = Fleet.objects.filter(is_active=True, is_featured=True).order_by('order')
    fleet = featured_fleet_qs[:4]
    fleet_vehicles = featured_fleet_qs  # For carousel
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
        'fleet_vehicles': fleet_vehicles,
        'testimonials': testimonials,
        'faqs': faqs,
        'form': form,
        'active_page': 'home',
    }
    return render(request, 'home.html', context)


def services(request):
    ensure_default_services()
    services = Service.objects.filter(is_active=True).order_by('order', 'title')
    active_fleet_qs = Fleet.objects.filter(is_active=True).order_by('order')
    fleet = active_fleet_qs
    fleet_vehicles = active_fleet_qs  # For carousel
    
    form_valid, result = handle_lead_form_submission(request, source='services_page')
    
    if form_valid:
        messages.success(request, 'Thank you for your interest! We will contact you shortly.')
        return redirect('thank_you')
    
    form = result if isinstance(result, LeadForm) else LeadForm()
    
    context = {
        'services': services,
        'fleet': fleet,
        'fleet_vehicles': fleet_vehicles,
        'form': form,
        'active_page': 'services',
    }
    return render(request, 'services.html', context)


def about(request):
    testimonials = Testimonial.objects.filter(is_approved=True)
    active_fleet_qs = Fleet.objects.filter(is_active=True).order_by('order')
    fleet = active_fleet_qs
    fleet_vehicles = active_fleet_qs  # For carousel
    
    context = {
        'testimonials': testimonials,
        'fleet': fleet,
        'fleet_vehicles': fleet_vehicles,
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
        'google_maps_api_key': django_settings.GOOGLE_MAPS_API_KEY,
        'contact_map_config': {
            'lat': django_settings.MAP_BUSINESS_LAT,
            'lng': django_settings.MAP_BUSINESS_LNG,
            'radiusM': django_settings.MAP_SERVICE_RADIUS_METERS,
            'markerTitle': django_settings.SITE_NAME,
        },
        'map_service_radius_km': max(1, round(django_settings.MAP_SERVICE_RADIUS_METERS / 1000)),
        'map_embed_address': django_settings.SITE_ADDRESS,
    }
    return render(request, 'contact_page.html', context)


def thank_you(request):
    return render(request, 'thank_you.html')


def robots_txt(request):
    """Tell crawlers where the sitemap is; tune Disallow when you add private areas."""
    base = django_settings.SITE_URL.rstrip('/')
    body = (
        'User-agent: *\n'
        'Allow: /\n'
        'Disallow: /dashboard/\n'
        'Disallow: /admin/\n'
        f'Sitemap: {base}/sitemap.xml\n'
    )
    return HttpResponse(body, content_type='text/plain; charset=utf-8')


def access_denied(request):
    """
    Custom access denied page for non-staff users trying to access dashboard
    """
    return render(request, 'access_denied.html', {
        'title': 'Access Denied',
        'message': 'You do not have permission to access this area.',
        'help_text': 'Please contact an administrator if you believe this is an error.'
    })


def user_logout(request):
    """
    Logout view that redirects to home page instead of admin login
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')


def handler404(request, exception):
    """Production-safe 404 (no stack traces in templates)."""
    return render(request, "404.html", status=404)


def handler500(request):
    """Production-safe 500 (no exception details leaked to clients)."""
    return render(request, "500.html", status=500)