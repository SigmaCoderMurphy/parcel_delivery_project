from django import forms
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

from .models import SiteSettings

class SiteSettingsForm(forms.ModelForm):
	class Meta:
		model = SiteSettings
		fields = [
			'site_name',
			'site_phone',
			'site_email',
			'contact_phone_1',
			'contact_phone_2',
			'contact_email_1',
			'contact_email_2',
			'site_address',
			'service_area',
			'business_hours',
			'facebook_url',
			'instagram_url',
			'linkedin_url',
			'google_business_url',
			'twitter_url',
		]
		widgets = {
			'site_address': forms.Textarea(attrs={'rows': 2}),
			'business_hours': forms.Textarea(attrs={'rows': 4}),
		}


class CustomPasswordResetForm(DjangoPasswordResetForm):
	"""
	Password reset email: plain text only (no HTML part), with branding context.
	Matches the style of typical security emails from large platforms.
	"""

	def save(
		self,
		domain_override=None,
		subject_template_name='registration/password_reset_subject.txt',
		email_template_name='registration/password_reset_email.txt',
		use_https=False,
		token_generator=default_token_generator,
		from_email=None,
		request=None,
		html_email_template_name=None,
		extra_email_context=None,
		**kwargs,
	):
		if extra_email_context is None:
			extra_email_context = {}

		extra_email_context.update({
			'site_name': getattr(settings, 'SITE_NAME', 'Eastern Logistics'),
			'site_email': getattr(settings, 'SITE_EMAIL', ''),
			'site_phone': getattr(settings, 'SITE_PHONE', ''),
			'site_address': getattr(settings, 'SITE_ADDRESS', ''),
		})

		return super().save(
			domain_override=domain_override,
			subject_template_name=subject_template_name,
			email_template_name=email_template_name,
			use_https=use_https,
			token_generator=token_generator,
			from_email=from_email,
			request=request,
			html_email_template_name=html_email_template_name,
			extra_email_context=extra_email_context,
			**kwargs,
		)

