from django.contrib import admin
from django.utils.html import format_html
from .models import SiteSettings, Fleet, Service, Testimonial, FAQ, EmailTemplate

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_phone', 'site_email']
    fieldsets = (
        ('Primary Contact Information', {
            'fields': ('site_name', 'site_phone', 'site_email', 'site_address', 'service_area'),
            'description': 'Primary contact details shown across the website.'
        }),
        ('Multiple Contact Options (Contact Page)', {
            'fields': ('contact_phones', 'contact_emails', 'business_hours'),
            'description': 'Add multiple phone numbers and emails for the contact page. Use line breaks to separate entries.',
            'classes': ('collapse',)
        }),
        ('Social Media & Business Profiles', {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url', 'twitter_url', 'google_business_url'),
            'description': 'Links to your social media and business profiles.',
            'classes': ('collapse',)
        }),
    )

@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle_type', 'capacity', 'image_preview', 'is_active', 'is_featured', 'order', 'status_badge']
    list_filter = ['is_active', 'is_featured']
    search_fields = ['name', 'vehicle_type', 'short_description', 'full_description']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'vehicle_type', 'capacity', 'dimensions')
        }),
        ('Description & Media', {
            'fields': ('short_description', 'full_description', 'image', 'image_preview_display')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'order'),
            'description': 'Order is automatically managed for active fleet vehicles. Inactive vehicles do not affect the sequence.'
        }),
    )
    readonly_fields = ['image_preview_display']
    
    def image_preview_display(self, obj):
        """Display image preview in change form"""
        if obj.image:
            return format_html(
                '<img src="{}" width="300" height="200" style="object-fit: cover; border-radius: 8px; margin-top: 10px;" />',
                obj.image.url
            )
        return "No image uploaded"
    image_preview_display.short_description = "Image Preview"
    
    def image_preview(self, obj):
        """Display thumbnail in list view"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" /></a>',
                obj.image.url,
                obj.image.url
            )
        return "—"
    image_preview.short_description = "Image"
    
    def status_badge(self, obj):
        """Display status badge in list view"""
        if obj.is_active:
            return f'✓ Active (#{obj.order})'
        return 'Inactive'
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_preview', 'is_active', 'is_featured', 'order', 'status_badge']
    list_filter = ['is_active', 'is_featured']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'icon')
        }),
        ('Description', {
            'fields': ('short_description', 'full_description')
        }),
        ('Media', {
            'fields': ('image', 'image_preview_display')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'is_featured', 'order'),
            'description': 'Order is automatically managed for active services. Inactive services do not affect the sequence.'
        }),
    )
    readonly_fields = ['image_preview_display']
    
    def image_preview_display(self, obj):
        """Display image preview in change form"""
        if obj.image:
            return format_html(
                '<img src="{}" width="300" height="200" style="object-fit: cover; border-radius: 8px; margin-top: 10px;" />',
                obj.image.url
            )
        return "No image uploaded"
    image_preview_display.short_description = "Image Preview"
    
    def image_preview(self, obj):
        """Display thumbnail in list view"""
        if obj.image:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" /></a>',
                obj.image.url,
                obj.image.url
            )
        return "—"
    image_preview.short_description = "Image"
    
    def status_badge(self, obj):
        """Display status badge in list view"""
        if obj.is_active:
            return f'✓ Active (#{obj.order})'
        return 'Inactive'
    status_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Override save to trigger ordering normalization"""
        super().save_model(request, obj, form, change)
        
        # After saving, if the service is being deactivated, normalize all other active services
        if change and not obj.is_active:
            from .utils import normalize_service_orders
            normalize_service_orders()

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['client_name', 'client_company', 'rating', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'rating']
    search_fields = ['client_name', 'client_company', 'content']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_type', 'subject', 'is_active', 'updated_at']
    list_filter = ['template_type', 'is_active']
    search_fields = ['subject', 'body']