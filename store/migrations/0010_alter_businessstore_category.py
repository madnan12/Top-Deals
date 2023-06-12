# Generated by Django 4.1 on 2022-09-28 18:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_user_is_account_officer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='businessstore',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categorystore_category', to='store.category'),
        ),
    ]
