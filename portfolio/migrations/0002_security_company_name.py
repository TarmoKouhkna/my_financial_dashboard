# Generated by Django 5.1 on 2024-08-31 09:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="security",
            name="company_name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
