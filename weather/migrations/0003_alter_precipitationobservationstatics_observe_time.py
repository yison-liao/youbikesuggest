# Generated by Django 4.2.16 on 2024-11-14 05:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weather", "0002_alter_observationstationinfo_station_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="precipitationobservationstatics",
            name="observe_time",
            field=models.DateTimeField(editable=False, max_length=256),
        ),
    ]
