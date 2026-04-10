from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Eastern Logistics")
    site_phone = models.CharField(max_length=20, default="416-710-0361")
    site_email = models.EmailField(default="support@easternlogistics.app")
    contact_phone_1 = models.CharField(
        max_length=20, 
        blank=True,
        default="+1 (416) 710-0361",
        help_text="First phone number for contact page. Format: +1 (XXX) XXX-XXXX"
    )
    contact_phone_2 = models.CharField(
        max_length=20, 
        blank=True,
        default="+1 (416) 555-1234",
        help_text="Second phone number for contact page. Format: +1 (XXX) XXX-XXXX"
    )
    contact_email_1 = models.EmailField(
        blank=True,
        default="support@easternlogistics.app",
        help_text="First email address for contact page"
    )
    contact_email_2 = models.EmailField(
        blank=True,
        default="info@easternlogistics.app",
        help_text="Second email address for contact page"
    )
    site_address = models.TextField(default="828 Eastern Ave, Toronto, ON M4L 1A1, Canada")
    service_area = models.CharField(max_length=200, default="Greater Toronto Area")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    google_business_url = models.URLField(
        blank=True,
        default="https://maps.app.goo.gl/gEr1qAS8g4DRXYkNA?g_st=aw",
    )
    twitter_url = models.URLField(blank=True)
    business_hours = models.TextField(
        blank=True,
        default=(
            "Monday–Sunday: 6 AM – 6 PM\n\n"
            "Holiday hours (e.g. Good Friday, Easter Sunday, Easter Monday) may differ—confirm on Google Maps or call us."
        ),
        help_text="Shown on the contact page. Use line breaks between lines.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def sync_primary_from_contact_fields(self):
        """Keep site_phone / site_email aligned with contact page (footer, schema.org, etc.)."""
        phone_max = self._meta.get_field("site_phone").max_length
        phone = (self.contact_phone_1 or "").strip() or (self.contact_phone_2 or "").strip()
        if phone:
            self.site_phone = phone[:phone_max]
        email = (self.contact_email_1 or "").strip() or (self.contact_email_2 or "").strip()
        if email:
            self.site_email = email

class Fleet(models.Model):
    name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=100, help_text="e.g., Sprinter High Roof, Bright Drop, Light Duty Box Truck")
    capacity = models.CharField(max_length=50, help_text="e.g., 3,500 lbs")
    dimensions = models.CharField(max_length=100, help_text="e.g., 12ft L x 6ft W x 6ft H")
    image = models.ImageField(
        upload_to='fleet/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif'])],
    )
    short_description = models.TextField(help_text="Brief description of the vehicle", default="")
    full_description = models.TextField(blank=True, help_text="Detailed description and best uses")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text="Display on homepage")
    order = models.IntegerField(default=0, help_text="Display order on homepage")
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.vehicle_type} - {self.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to handle automatic ordering for active fleet vehicles.
        Ensures no two active fleet vehicles have the same order.
        Enforces maximum of 4 active fleet vehicles.
        """
        from .utils import normalize_fleet_orders, get_next_fleet_order
        
        # Check if we're trying to activate a 5th fleet
        if self.is_active:
            # Count active fleets, excluding this one if it's already active
            active_count = Fleet.objects.filter(is_active=True).exclude(pk=self.pk).count()
            
            # If this is a new fleet being activated and we already have 4 active
            if not self.pk and active_count >= 4:
                raise ValueError("Maximum of 4 active fleet vehicles allowed. Please deactivate one before activating another.")
            
            # If this was inactive and we're activating it while 4 are already active
            if self.pk and not Fleet.objects.filter(pk=self.pk).first().is_active and active_count >= 4:
                raise ValueError("Maximum of 4 active fleet vehicles allowed. Please deactivate one before activating another.")
        
        # If this is a new object and it's active, assign next available order
        if not self.pk and self.is_active and self.order == 0:
            self.order = get_next_fleet_order()
        
        # Save the fleet vehicle first
        super().save(*args, **kwargs)

        # Renumber all active vehicles whenever any fleet row changes (activate,
        # deactivate, or edit) so orders stay contiguous and unique.
        normalize_fleet_orders()

class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField()
    full_description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    image = models.ImageField(
        upload_to='services/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp', 'gif'])],
    )
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """
        Override save to handle automatic ordering for active services.
        Ensures no two active services have the same order.
        """
        from .utils import normalize_service_orders, get_next_service_order
        
        # If this is a new object and it's active, assign next available order
        if not self.pk and self.is_active and self.order == 0:
            self.order = get_next_service_order()
        
        # Save the service first
        super().save(*args, **kwargs)
        
        # After saving, normalize all active service orders to ensure uniqueness
        # Only do this if the service is active
        if self.is_active:
            normalize_service_orders()

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


class EmailTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('welcome', 'Welcome Email'),
        ('quote', 'Quote Email'),
        ('followup', 'Follow-up Email'),
    ]

    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES, unique=True)
    subject = models.CharField(max_length=255, default='')
    body = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return f"{self.get_template_type_display()}"