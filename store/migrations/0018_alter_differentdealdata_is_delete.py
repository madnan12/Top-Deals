# Generated by Django 4.1 on 2022-10-05 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0017_alter_businessdeal_discount_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='differentdealdata',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
