# Generated by Django 4.1 on 2022-10-27 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_businessstore_is_account_officer'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessdeal',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=30, null=True),
        ),
        migrations.AddField(
            model_name='businessdeal',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=16, max_digits=30, null=True),
        ),
        migrations.AlterModelTable(
            name='businessdeal',
            table='BusinessDeal',
        ),
    ]