from django.contrib import admin

# Register your models here.
from weather import models


@admin.register(models.ObservationStationInfo)
class ObservationStationInfo(admin.ModelAdmin):
    search_fields = ["_id", "station_name", "station_id"]
    list_filter = ["_id", "station_name", "station_id"]
    list_display = ["_id", "station_name", "station_id"]
    list_editable = []
    ordering = ["station_id"]


@admin.register(models.PrecipitationObservationStatics)
class PrecipitationObservationStatics(admin.ModelAdmin):
    search_fields = ["_id", "station_uuid", "observe_time"]
    list_filter = ["_id", "station_uuid", "observe_time"]
    list_display = ["_id", "station_uuid", "observe_time"]
    list_editable = []
    ordering = ["observe_time"]
