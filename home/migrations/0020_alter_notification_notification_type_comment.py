# Generated by Django 4.2.1 on 2025-01-30 21:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0019_alter_notification_notification_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('follower', 'Follower'), ('request', 'Follow Request'), ('event_registration', 'Event Registration')], max_length=25),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_author', to='home.user')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_event', to='home.event')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='home.comment')),
            ],
        ),
    ]
