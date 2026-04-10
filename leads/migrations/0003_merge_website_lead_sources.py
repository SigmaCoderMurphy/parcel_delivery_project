from django.db import migrations


def merge_website_sources(apps, schema_editor):
    Lead = apps.get_model('leads', 'Lead')
    Lead.objects.filter(source__in=['contact_form', 'services_page']).update(source='website')


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_scheduledemail_calllog_callanalysis'),
    ]

    operations = [
        migrations.RunPython(merge_website_sources, noop_reverse),
    ]
