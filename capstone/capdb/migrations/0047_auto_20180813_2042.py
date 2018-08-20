# Generated by Django 2.0.8 on 2018-08-13 20:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('capdb', '0046_court_denormalization'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='casemetadata',
            name='tsvector',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='casetext',
            name='metadata',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='case_text', to='capdb.CaseMetadata'),
        ),
    ]