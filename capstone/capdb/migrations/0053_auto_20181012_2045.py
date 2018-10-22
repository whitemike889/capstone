# Generated by Django 2.0.8 on 2018-10-12 20:45

from django.db import migrations


def create_tribal_jurisdiction(apps, schema_editor):
    Jurisdiction = apps.get_model("capdb", "Jurisdiction")
    if not Jurisdiction.objects.filter(name="Tribal").exists():
        Jurisdiction(name="Tribal", name_long="Tribal Jurisdictions", slug="tribal").save()

class Migration(migrations.Migration):

    dependencies = [
        ('capdb', '0052_auto_20181003_2041'),
    ]

    operations = [
        migrations.RunPython(create_tribal_jurisdiction, migrations.RunPython.noop),
    ]
