# Generated by Django 4.1 on 2022-10-07 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0022_alter_businessdeal_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='dial_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]