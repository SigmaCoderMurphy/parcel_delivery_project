from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ("SuperAdmin", "Admin", "User"):
        Group.objects.get_or_create(name=name)


def remove_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=("SuperAdmin", "Admin", "User")).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_alter_fleet_image_alter_service_image"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
