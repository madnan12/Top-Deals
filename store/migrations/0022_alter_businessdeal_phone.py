# Generated by Django 4.1 on 2022-10-07 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0021_businessdeal_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessdeal',
            name='phone',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
    ]
