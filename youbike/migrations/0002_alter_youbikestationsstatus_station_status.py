# Generated by Django 4.2.16 on 2024-11-10 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("youbike", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="youbikestationsstatus",
            name="station_status",
            field=models.IntegerField(choices=[(1, "work"), (2, "not work")]),
        ),
    ]
