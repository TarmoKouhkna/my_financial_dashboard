# Generated by Django 5.1 on 2024-08-31 11:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portfolio", "0002_security_company_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="security",
            name="company_name",
            field=models.CharField(default="Unknown", max_length=255),
        ),
    ]
