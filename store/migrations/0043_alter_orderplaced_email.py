# Generated by Django 4.1 on 2022-11-01 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0042_alter_ordercardcheckout_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderplaced',
            name='email',
            field=models.EmailField(default='', max_length=255, verbose_name='email'),
        ),
    ]