from django.contrib import admin
from .models import SiteSettings, Fleet, Service, Testimonial, FAQ

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'site_phone', 'site_email']

@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ['name', 'vehicle_type', 'capacity', 'is_active']
    list_filter = ['vehicle_type', 'is_active']
    search_fields = ['name', 'description']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_featured', 'order']
    list_filter = ['is_featured']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}

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