# Generated by Django 4.1 on 2022-10-17 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_currency_currency_symbol'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessdeal',
            name='deal_status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=255, null=True),
        ),
    ]