# Generated by Django 4.1 on 2022-10-06 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_alter_differentdealdata_is_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessdeal',
            name='deal_status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], max_length=255, null=True),
        ),
    ]
