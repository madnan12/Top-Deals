# Generated by Django 4.1 on 2022-10-25 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_webdynamiccontent_about_us_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account_officer',
            name='business_store',
            field=models.ManyToManyField(blank=True, null=True, related_name='account_officer_business_store', to='store.businessstore'),
        ),
    ]
