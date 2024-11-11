import uuid

from django.db import models
from multiselectfield import MultiSelectField


# Create your models here.
class AreaInfo(models.Model):
    _id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    area_name_cn = models.CharField(
        max_length=256, unique=True, blank=False, null=False
    )
    area_name_en = models.CharField(max_length=256, unique=False, blank=True, null=True)
    area_code = models.CharField(max_length=10, unique=False, blank=True, null=True)
    area_code_2 = models.CharField(max_length=10, unique=False, blank=True, null=True)
    lat_from = models.FloatField(unique=False, blank=False, null=False)
    lat_to = models.FloatField(unique=False, blank=False, null=False)
    lng_from = models.FloatField(unique=False, blank=False, null=False)
    lng_to = models.FloatField(unique=False, blank=False, null=False)


class DistrictInfo(models.Model):
    _id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    area_uuid = models.UUIDField(max_length=256)
    district_tw = models.CharField(max_length=256, unique=False, blank=True, null=True)
    district_en = models.CharField(max_length=256, unique=False, blank=True, null=True)


class ServiceInfo(models.Model):
    BIKES_TYPES = (
        ("Type1", "Generation 1"),
        ("Type2", "Generation 2"),
        ("Type3", "E-Bike"),
    )
    _id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    area_uuid = models.UUIDField(max_length=256, unique=True)
    station_no_start = models.CharField(
        max_length=256, unique=False, blank=False, null=False
    )
    station_no_end = models.CharField(
        max_length=256, unique=False, blank=False, null=False
    )
    bike_types = MultiSelectField(choices=BIKES_TYPES, max_length=50)
    member_count = models.BigIntegerField(blank=False, null=False)
    ride_count1 = models.BigIntegerField(blank=False, null=False)
    ride_count2 = models.BigIntegerField(blank=False, null=False)
    visit_count = models.BigIntegerField(blank=False, null=False)
