from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="GTA Parcel Delivery")
    site_phone = models.CharField(max_length=20, default="+1 (416) 555-0123")
    site_email = models.EmailField(default="info@gtaparceldelivery.com")
    site_address = models.TextField(default="123 Business Ave, Toronto, ON")
    service_area = models.CharField(max_length=200, default="Greater Toronto Area")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    google_business_url = models.URLField(blank=True)
    
    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

class Fleet(models.Model):
    VEHICLE_TYPES = [
        ('sprinter', 'Sprinter High Roof Van (12ft)'),
        ('brightdrop', 'Bright Drop (14ft)'),
        ('light_box', 'Light Duty Box Truck (16ft)'),
        ('medium_box', 'Medium Box Truck (26ft)'),
    ]
    
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    capacity = models.CharField(max_length=50, help_text="e.g., 3,500 lbs")
    dimensions = models.CharField(max_length=100, help_text="e.g., 12ft L x 6ft W x 6ft H")
    image = models.ImageField(upload_to='fleet/', blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.get_vehicle_type_display()} - {self.name}"

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    image = models.ImageField(upload_to='services/', blank=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Testimonial(models.Model):
    client_name = models.CharField(max_length=100)
    client_company = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.client_name} - {self.client_company}"

class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.question