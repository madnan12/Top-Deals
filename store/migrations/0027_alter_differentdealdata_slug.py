# Generated by Django 4.1 on 2022-10-22 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0026_businessstore_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='differentdealdata',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]