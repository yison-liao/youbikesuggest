import uuid

from django.db import models
from django.utils import timezone


# Create your models here.
class YoubikeStationsInfo(models.Model):
    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    area_uuid = models.UUIDField(blank=False)
    district_uuid = models.UUIDField(blank=False)
    name_tw = models.CharField(max_length=256, blank=False, editable=True)
    name_en = models.CharField(max_length=256, blank=False, editable=True)
    address_tw = models.CharField(max_length=256, blank=False, editable=True)
    address_en = models.CharField(max_length=256, blank=False, editable=True)
    lat = models.FloatField(unique=False, blank=False, null=False)
    lng = models.FloatField(unique=False, blank=False, null=False)
    station_no = models.CharField(max_length=256, blank=False, editable=True)


class YoubikeStationsStatus(models.Model):
    status_option = ((1, "work"), (2, "not work"))

    _id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    station_uuid = models.UUIDField(blank=False)
    parking_spaces = models.BigIntegerField(blank=False, editable=True)
    available_spaces = models.BigIntegerField(blank=False, editable=True)
    record_time = models.DateTimeField(blank=False, editable=True)
    station_status = models.IntegerField(choices=status_option)
    update_at = models.DateTimeField(default=timezone.now, auto_created=True)
