# Generated by Django 2.0.2 on 2018-07-11 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capapi', '0005_auto_20180710_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteLimits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daily_signup_limit', models.IntegerField(default=50)),
                ('daily_signups', models.IntegerField(default=0)),
                ('daily_download_limit', models.IntegerField(default=50000)),
                ('daily_downloads', models.IntegerField(default=0)),
            ],
        ),
    ]