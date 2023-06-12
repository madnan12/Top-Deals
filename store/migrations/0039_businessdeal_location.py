# Generated by Django 4.1 on 2022-10-31 12:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0038_businessdeal_end_time_businessdeal_start_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessdeal',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='businessdeal_location', to='store.storelocation'),
        ),
    ]
