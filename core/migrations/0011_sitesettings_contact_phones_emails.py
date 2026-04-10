# Generated migration - Add contact_phones and contact_emails to SiteSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_sitesettings_business_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='contact_phones',
            field=models.TextField(blank=True, default='+1 (416) 710-0361\n+1 (416) 555-1234', help_text='Multiple phone numbers for contact page. Use line breaks between entries. Format: +1 (XXX) XXX-XXXX'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='contact_emails',
            field=models.TextField(blank=True, default='support@easternlogistics.app\ninfo@easternlogistics.app', help_text='Multiple emails for contact page. Use line breaks between entries.'),
        ),
    ]
