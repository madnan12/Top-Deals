# Generated by Django 4.1 on 2022-10-24 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_alter_cartitem_deal_alter_cartitem_option_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessstore',
            name='total_order',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
