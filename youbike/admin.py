from django.contrib import admin

# Register your models here.
from youbike import models


@admin.register(models.YoubikeStationsInfo)
class YoubikeStationsInfo(admin.ModelAdmin):
    search_fields = ["_id", "area_uuid", "district_uuid", "name_tw", "station_no"]
    list_filter = ["_id", "area_uuid", "district_uuid"]
    list_display = ["_id", "area_uuid", "district_uuid", "name_tw", "station_no"]
    list_editable = []
    ordering = ["area_uuid"]


@admin.register(models.YoubikeStationsStatus)
class YoubikeStationsStatus(admin.ModelAdmin):
    search_fields = ["_id", "station_uuid"]
    list_filter = ["_id", "station_uuid"]
    list_display = ["_id", "station_uuid"]
    list_editable = []
    ordering = ["station_uuid"]
