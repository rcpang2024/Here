# Generated by Django 4.2.1 on 2024-07-17 01:55

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_remove_user_phone_number_alter_user_user_privacy'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='location',
            new_name='location_addr',
        ),
        migrations.AddField(
            model_name='event',
            name='location_point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_privacy',
            field=models.CharField(choices=[('private', 'private'), ('public', 'public')], default='public', max_length=50),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('organization', 'organization'), ('individual', 'individual')], default='individual', max_length=50),
        ),
    ]
