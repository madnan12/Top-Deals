# Generated by Django 4.1 on 2022-09-27 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_user_business_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessstore',
            name='store_status',
            field=models.CharField(choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=50),
        ),
    ]
