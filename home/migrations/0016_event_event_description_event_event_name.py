# Generated by Django 4.2.1 on 2023-06-03 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_alter_user_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='event',
            name='event_name',
            field=models.CharField(default='', max_length=200),
        ),
    ]
