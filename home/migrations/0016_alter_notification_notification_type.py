# Generated by Django 4.2.1 on 2024-09-27 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_remove_user_password_user_expo_push_token_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('request', 'Follow Request'), ('event_registration', 'Event Registration'), ('follower', 'Follower')], max_length=25),
        ),
    ]