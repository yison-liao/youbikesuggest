import uuid

from django.db import models
from django.utils import timezone


# Create your models here.
class ObservationStationInfo(models.Model):
    _id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    station_name = models.CharField(
        max_length=256, unique=False, blank=False, null=False
    )
    station_id = models.CharField(max_length=256, unique=True, blank=True, null=True)
    altitude = models.FloatField(unique=False, blank=False, null=False)
    area_uuid = models.UUIDField(max_length=256)
    district_uuid = models.UUIDField(max_length=256)
    lat = models.FloatField(unique=False, blank=False, null=False)
    lng = models.FloatField(unique=False, blank=False, null=False)


class PrecipitationObservationStatics(models.Model):
    _id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    station_uuid = models.UUIDField(max_length=256)
    observe_time = models.DateTimeField(
        max_length=256, blank=False, editable=False, null=False
    )
    precipi_obstime = models.FloatField(unique=False, blank=False, null=False)
    precipi_past_10_min = models.FloatField(unique=False, blank=False, null=False)
    precipi_past_1_hr = models.FloatField(unique=False, blank=False, null=False)
    precipi_past_3_hr = models.FloatField(unique=False, blank=False, null=False)
    updated_at = models.DateTimeField(default=timezone.now, auto_created=True)
