# Generated by Django 4.1 on 2022-10-05 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_user_facebook_link_user_instagram_link_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='businessdeal',
            name='condition',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='differentdealdata',
            name='is_delete',
            field=models.BooleanField(default=True),
        ),
    ]