# Generated by Django 4.2.1 on 2025-03-04 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_alter_message_media_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('follower', 'Follower'), ('request', 'Follow Request'), ('event_registration', 'Event Registration')], max_length=25),
        ),
        migrations.AlterField(
            model_name='user',
            name='profile_pic',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('individual', 'individual'), ('organization', 'organization')], default='individual', max_length=50),
        ),
    ]
