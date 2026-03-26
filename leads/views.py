from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
from .models import Lead, FollowUp, CommunicationLog, Quote
from .forms import LeadForm, FollowUpForm, CommunicationLogForm, QuoteForm
from core.utils import send_followup_reminder

@staff_member_required
def dashboard_home(request):
    # Statistics
    total_leads = Lead.objects.count()
    new_leads = Lead.objects.filter(status='new').count()
    won_leads = Lead.objects.filter(status='won').count()
    
    # Leads by source
    leads_by_source = Lead.objects.values('source').annotate(count=Count('source'))
    
    # Recent leads
    recent_leads = Lead.objects.order_by('-created_at')[:10]
    
    # Today's follow-ups
    today = timezone.now().date()
    todays_followups = FollowUp.objects.filter(
        scheduled_date__date=today,
        is_completed=False
    ).select_related('lead')
    
    context = {
        'total_leads': total_leads,
        'new_leads': new_leads,
        'won_leads': won_leads,
        'leads_by_source': leads_by_source,
        'recent_leads': recent_leads,
        'todays_followups': todays_followups,
    }
    return render(request, 'dashboard/dashboard_home.html', context)

@staff_member_required
def leads_list(request):
    leads = Lead.objects.all().select_related('assigned_to')
    
    # Filtering
    status = request.GET.get('status')
    source = request.GET.get('source')
    business_type = request.GET.get('business_type')
    
    if status:
        leads = leads.filter(status=status)
    if source:
        leads = leads.filter(source=source)
    if business_type:
        leads = leads.filter(business_type=business_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        leads = leads.filter(
            Q(company_name__icontains=search) |
            Q(contact_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    context = {
        'leads': leads,
        'status_choices': Lead.LEAD_STATUS,
        'source_choices': Lead.LEAD_SOURCE,
        'business_types': Lead.BUSINESS_TYPES,
    }
    return render(request, 'dashboard/leads_list.html', context)

@staff_member_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    followups = lead.followups.all()
    communications = lead.communications.all()
    quotes = lead.quotes.all()
    
    if request.method == 'POST':
        if 'add_followup' in request.POST:
            form = FollowUpForm(request.POST)
            if form.is_valid():
                followup = form.save(commit=False)
                followup.lead = lead
                followup.save()
                messages.success(request, 'Follow-up scheduled successfully.')
                return redirect('lead_detail', pk=lead.pk)
        
        elif 'add_communication' in request.POST:
            form = CommunicationLogForm(request.POST)
            if form.is_valid():
                comm = form.save(commit=False)
                comm.lead = lead
                comm.staff_member = request.user
                comm.save()
                
                # Update last contacted
                lead.last_contacted = timezone.now()
                lead.save()
                
                messages.success(request, 'Communication logged successfully.')
                return redirect('lead_detail', pk=lead.pk)
    
    followup_form = FollowUpForm()
    communication_form = CommunicationLogForm()
    
    context = {
        'lead': lead,
        'followups': followups,
        'communications': communications,
        'quotes': quotes,
        'followup_form': followup_form,
        'communication_form': communication_form,
    }
    return render(request, 'dashboard/lead_detail.html', context)

@staff_member_required
def update_lead_status(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Lead.LEAD_STATUS).keys():
            lead.status = new_status
            lead.save()
            messages.success(request, f'Lead status updated to {lead.get_status_display()}')
    return redirect('lead_detail', pk=lead.pk)

@staff_member_required
def follow_ups(request):
    # Upcoming follow-ups
    upcoming = FollowUp.objects.filter(
        scheduled_date__gte=timezone.now(),
        is_completed=False
    ).select_related('lead').order_by('scheduled_date')
    
    # Overdue follow-ups
    overdue = FollowUp.objects.filter(
        scheduled_date__lt=timezone.now(),
        is_completed=False
    ).select_related('lead').order_by('scheduled_date')
    
    # Completed follow-ups
    completed = FollowUp.objects.filter(
        is_completed=True
    ).select_related('lead').order_by('-completed_date')[:50]
    
    context = {
        'upcoming': upcoming,
        'overdue': overdue,
        'completed': completed,
    }
    return render(request, 'dashboard/follow_ups.html', context)

@staff_member_required
def complete_followup(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk)
    if request.method == 'POST':
        followup.is_completed = True
        followup.completed_date = timezone.now()
        followup.completed_by = request.user
        followup.save()
        
        messages.success(request, 'Follow-up marked as completed.')
    return redirect('follow_ups')


# The following views are referenced by `leads/urls.py`.
# Implementing full PDF/Excel export requires additional libraries/templates.
# For now, we provide safe placeholders so the project can start.

@staff_member_required
def export_lead_pdf(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    return HttpResponse(
        f"PDF export is not implemented yet for lead #{lead.pk}.",
        content_type="text/plain",
        status=501,
    )


@staff_member_required
def reports(request):
    return HttpResponse("Reports page is not implemented yet.", content_type="text/plain", status=501)


@staff_member_required
def export_leads_excel(request):
    return HttpResponse("Excel export is not implemented yet.", content_type="text/plain", status=501)


@staff_member_required
def import_leads_excel(request):
    return HttpResponse("Excel import is not implemented yet.", content_type="text/plain", status=501)


@staff_member_required
def dashboard_settings(request):
    return HttpResponse("Dashboard settings is not implemented yet.", content_type="text/plain", status=501)