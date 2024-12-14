# Generated by Django 4.2.17 on 2024-12-14 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("taiwan_area_info", "0004_districtinfo"),
    ]

    operations = [
        migrations.AddField(
            model_name="areainfo",
            name="station_end",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="areainfo",
            name="station_start",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]