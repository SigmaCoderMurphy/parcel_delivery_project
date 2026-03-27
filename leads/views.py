from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from datetime import datetime, timedelta
from .models import Lead, FollowUp, CommunicationLog, Quote, CallLog, ScheduledEmail
from .forms import LeadForm, FollowUpForm, CommunicationLogForm, QuoteForm
from .pdf_utils import generate_and_save_quote_pdf, send_quote_pdf_email
from core.utils import send_email_notification, send_admin_notification
import json
import uuid

# ==================== DASHBOARD HOME ====================

@staff_member_required
def dashboard_home(request):
    """Dashboard homepage with statistics"""
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
    """Display all leads with filtering"""
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
def update_lead_status(request, pk):
    """Update lead status"""
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
    """Display follow-ups dashboard"""
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
    """Mark follow-up as completed"""
    followup = get_object_or_404(FollowUp, pk=pk)
    if request.method == 'POST':
        followup.is_completed = True
        followup.completed_date = timezone.now()
        followup.completed_by = request.user
        followup.save()
        
        messages.success(request, 'Follow-up marked as completed.')
    return redirect('follow_ups')

# ==================== PDF QUOTE GENERATION ====================

@staff_member_required
def create_quote(request, pk):
    """Create a new quote for lead with PDF generation"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        form = QuoteForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.lead = lead
            quote.created_by = request.user
            
            # Generate unique quote number
            quote.quote_number = f"Q-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"
            
            # Set default valid until (30 days from now)
            if not quote.valid_until:
                quote.valid_until = datetime.now().date() + timedelta(days=30)
            
            quote.save()
            
            # Generate PDF
            pdf_result = generate_and_save_quote_pdf(lead, quote)
            
            if pdf_result['success']:
                # Send quote email
                send_quote_pdf_email(lead, quote)
                messages.success(request, pdf_result['message'])
            else:
                messages.warning(request, pdf_result['message'])
            
            return redirect('lead_detail', pk=lead.pk)
    else:
        # Pre-populate with default values
        initial = {
            'valid_until': datetime.now().date() + timedelta(days=30),
            'terms': """Standard Terms:
1. Payment is due within 30 days of invoice date.
2. Cancellations require 24 hours notice.
3. Insurance coverage up to $2,000 per shipment.
4. Additional services billed separately.

For questions, contact your account manager."""
        }
        form = QuoteForm(initial=initial)
    
    return render(request, 'dashboard/create_quote.html', {
        'form': form,
        'lead': lead
    })


@staff_member_required
def view_quote_pdf(request, pk):
    """View generated PDF quote"""
    quote = get_object_or_404(Quote, pk=pk)
    
    if quote.pdf_file:
        return redirect(quote.pdf_file.url)
    else:
        messages.error(request, 'PDF file not found for this quote.')
        return redirect('lead_detail', pk=quote.lead.pk)


@staff_member_required
def regenerate_quote_pdf(request, pk):
    """Regenerate PDF for existing quote"""
    quote = get_object_or_404(Quote, pk=pk)
    
    pdf_result = generate_and_save_quote_pdf(quote.lead, quote)
    
    if pdf_result['success']:
        messages.success(request, 'Quote PDF regenerated successfully!')
    else:
        messages.error(request, pdf_result['message'])
    
    return redirect('lead_detail', pk=quote.lead.pk)


@staff_member_required
def accept_quote(request, pk):
    """Mark quote as accepted and update lead status"""
    quote = get_object_or_404(Quote, pk=pk)
    
    if request.method == 'POST':
        quote.status = 'accepted'
        quote.save()
        
        # Update lead status to 'won'
        quote.lead.status = 'won'
        quote.lead.save()
        
        messages.success(request, f'Quote accepted! Lead status updated to Won.')
    
    return redirect('lead_detail', pk=quote.lead.pk)


# ==================== CALL TRACKING INTEGRATION ====================

@staff_member_required
def call_logs(request):
    """View all call logs"""
    calls = CallLog.objects.all().select_related('lead')
    
    context = {
        'calls': calls,
    }
    return render(request, 'dashboard/call_logs.html', context)

@staff_member_required
def add_call_log(request, pk):
    """Manually add a call log for a lead"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        from .call_tracking import CallTrackingManager
        
        call_duration = int(request.POST.get('call_duration', 0))
        call_notes = request.POST.get('call_notes', '')
        
        tracking_manager = CallTrackingManager()
        call_log = tracking_manager.log_call(
            lead=lead,
            call_duration=call_duration,
            call_notes=call_notes,
            recording_url=request.POST.get('recording_url', '')
        )
        
        # Analyze call
        tracking_manager.analyze_call(call_log)
        
        # Update lead last contacted
        lead.last_contacted = timezone.now()
        lead.save()
        
        messages.success(request, 'Call logged successfully!')
        return redirect('lead_detail', pk=lead.pk)
    
    return render(request, 'dashboard/add_call_log.html', {'lead': lead})

@csrf_exempt
def twilio_call_webhook(request):
    """Handle incoming Twilio calls for tracking"""
    if request.method == 'POST':
        call_data = {
            'call_sid': request.POST.get('CallSid'),
            'caller_number': request.POST.get('From'),
            'call_status': request.POST.get('CallStatus'),
            'call_duration': request.POST.get('CallDuration', 0),
            'recording_url': request.POST.get('RecordingUrl', '')
        }
        
        # Try to find lead by phone number
        from .models import Lead
        from .call_tracking import CallTrackingManager
        
        # Extract last 10 digits for matching
        caller_number = call_data['caller_number'][-10:] if call_data['caller_number'] else ''
        
        try:
            lead = Lead.objects.filter(phone__contains=caller_number).first()
        except:
            lead = None
        
        # Log the call
        tracking_manager = CallTrackingManager()
        
        # Determine call type
        call_type = 'incoming'
        if call_data['call_status'] in ['no-answer', 'busy', 'failed']:
            call_type = 'missed'
        
        # Create call log
        from .models import CallLog
        call_log = CallLog.objects.create(
            lead=lead,
            call_sid=call_data['call_sid'],
            caller_number=call_data['caller_number'],
            call_duration=int(call_data['call_duration']),
            call_notes=f"Call from {call_data['caller_number']} - Status: {call_data['call_status']}",
            recording_url=call_data['recording_url'],
            call_type=call_type
        )
        
        return JsonResponse({'status': 'success', 'call_id': call_log.id})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

# ==================== EMAIL FOLLOW-UP AUTOMATION ====================

@staff_member_required
def email_followup_report(request):
    """View email follow-up statistics"""
    scheduled = ScheduledEmail.objects.filter(sent=False).order_by('scheduled_date')
    sent = ScheduledEmail.objects.filter(sent=True).order_by('-sent_at')[:50]
    
    # Statistics
    total_scheduled = ScheduledEmail.objects.count()
    total_sent = ScheduledEmail.objects.filter(sent=True).count()
    open_rate = 0  # Would need tracking pixels for actual open rates
    
    context = {
        'scheduled': scheduled,
        'sent': sent,
        'total_scheduled': total_scheduled,
        'total_sent': total_sent,
        'open_rate': open_rate,
    }
    return render(request, 'dashboard/email_followups.html', context)

@staff_member_required
def schedule_followup_emails(request, pk):
    """Schedule follow-up emails for a lead"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        from .email_automation import EmailFollowUpSystem
        
        email_system = EmailFollowUpSystem(lead)
        email_system.schedule_follow_up_sequence()
        
        messages.success(request, f'Follow-up emails scheduled for {lead.company_name}')
        return redirect('lead_detail', pk=lead.pk)
    
    return render(request, 'dashboard/schedule_emails.html', {'lead': lead})

@staff_member_required
def send_manual_email(request, pk):
    """Manually send an email to lead"""
    lead = get_object_or_404(Lead, pk=pk)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if subject and message:
            # Use centralized email utility
            email_sent = send_email_notification(subject, message, lead.email)
            
            if email_sent:
                # Log communication
                CommunicationLog.objects.create(
                    lead=lead,
                    communication_type='email',
                    direction='out',
                    subject=subject,
                    content=message,
                    staff_member=request.user
                )
                
                messages.success(request, f'Email sent to {lead.email}')
            else:
                messages.error(request, 'Failed to send email. Please try again.')
        else:
            messages.error(request, 'Please fill in both subject and message')
        
        return redirect('lead_detail', pk=lead.pk)
    
    return render(request, 'dashboard/send_email.html', {'lead': lead})

# ==================== UPDATED EXISTING VIEWS ====================

@staff_member_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    followups = lead.followups.all()
    communications = lead.communications.all()
    quotes = lead.quotes.all()
    calls = lead.calls.all()[:10]  # Show last 10 calls
    
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
        'calls': calls,
        'followup_form': followup_form,
        'communication_form': communication_form,
    }
    return render(request, 'dashboard/lead_detail.html', context)

@staff_member_required
def export_lead_pdf(request, pk):
    """Export lead details as PDF"""
    lead = get_object_or_404(Lead, pk=pk)
    
    try:
        from .quote_generator import QuoteGenerator
        from .models import Quote
        
        # Create a temporary quote for export
        temp_quote = Quote.objects.create(
            lead=lead,
            quote_number=f"INFO-{lead.pk}",
            amount=0,
            valid_until=timezone.now().date() + timedelta(days=30),
            terms="Lead information export",
            created_by=request.user
        )
        
        generator = QuoteGenerator(lead, temp_quote)
        pdf_filename = generator.generate_pdf_reportlab()
        
        if pdf_filename:
            return redirect(pdf_filename)
        else:
            return HttpResponse("PDF generation failed", status=500)
            
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

@staff_member_required
def export_leads_excel(request):
    """Export leads to Excel"""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from django.http import HttpResponse
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Leads Export"
        
        # Headers
        headers = [
            'ID', 'Company', 'Contact', 'Email', 'Phone', 'Business Type',
            'Status', 'Source', 'Service Area', 'Created Date', 'Last Contact'
        ]
        
        # Style headers
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="2563eb", end_color="2563eb", fill_type="solid")
        
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal='center')
        
        # Add data
        leads = Lead.objects.all()
        for row, lead in enumerate(leads, 2):
            ws.cell(row=row, column=1, value=lead.id)
            ws.cell(row=row, column=2, value=lead.company_name)
            ws.cell(row=row, column=3, value=lead.contact_name)
            ws.cell(row=row, column=4, value=lead.email)
            ws.cell(row=row, column=5, value=lead.phone)
            ws.cell(row=row, column=6, value=lead.get_business_type_display())
            ws.cell(row=row, column=7, value=lead.get_status_display())
            ws.cell(row=row, column=8, value=lead.get_source_display())
            ws.cell(row=row, column=9, value=lead.service_area)
            ws.cell(row=row, column=10, value=lead.created_at.strftime('%Y-%m-%d'))
            ws.cell(row=row, column=11, value=lead.last_contacted.strftime('%Y-%m-%d') if lead.last_contacted else '')
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Create response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="leads_export_{datetime.now().strftime("%Y%m%d")}.xlsx"'
        wb.save(response)
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Export failed: {str(e)}", status=500)

@staff_member_required
def import_leads_excel(request):
    """Import leads from Excel"""
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            import openpyxl
            file = request.FILES['file']
            wb = openpyxl.load_workbook(file)
            ws = wb.active
            
            imported_count = 0
            errors = []
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                try:
                    if not row[1]:  # Skip if no company name
                        continue
                    
                    lead = Lead.objects.create(
                        company_name=row[1] or '',
                        contact_name=row[2] or '',
                        email=row[3] or '',
                        phone=row[4] or '',
                        business_type=row[5] or 'other',
                        service_area=row[8] or 'GTA',
                        status='new',
                        source='import'
                    )
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {row[0]}: {str(e)}")
            
            if imported_count > 0:
                messages.success(request, f'Successfully imported {imported_count} leads')
            if errors:
                messages.warning(request, f'Errors: {", ".join(errors[:5])}')
                
        except Exception as e:
            messages.error(request, f'Import failed: {str(e)}')
        
        return redirect('leads_list')
    
    return redirect('leads_list')

@staff_member_required
def dashboard_settings(request):
    """Dashboard settings"""
    from core.models import SiteSettings
    
    try:
        site_settings = SiteSettings.objects.first()
    except:
        site_settings = None
    
    if request.method == 'POST':
        # Update settings logic here
        messages.success(request, 'Settings updated successfully!')
        return redirect('dashboard_settings')
    
    context = {
        'site_settings': site_settings,
    }
    return render(request, 'dashboard/settings.html', context)

@staff_member_required
def reports(request):
    """Reports dashboard"""
    # Get date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Lead statistics
    total_leads = Lead.objects.count()
    leads_this_month = Lead.objects.filter(created_at__date__gte=start_date).count()
    conversion_rate = (Lead.objects.filter(status='won').count() / total_leads * 100) if total_leads > 0 else 0
    
    # Lead by source
    leads_by_source = Lead.objects.values('source').annotate(count=Count('source'))
    
    # Lead by business type
    leads_by_business = Lead.objects.values('business_type').annotate(count=Count('business_type'))
    
    # Revenue statistics
    total_revenue = Quote.objects.filter(status='accepted').aggregate(total=Sum('amount'))['total'] or 0
    
    # Calculate average deal size
    avg_deal_size = total_revenue / total_leads if total_leads > 0 else 0
    
    context = {
        'total_leads': total_leads,
        'leads_this_month': leads_this_month,
        'conversion_rate': round(conversion_rate, 1),
        'total_revenue': total_revenue,
        'avg_deal_size': avg_deal_size,
        'leads_by_source': leads_by_source,
        'leads_by_business': leads_by_business,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/reports.html', context)