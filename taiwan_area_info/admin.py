from django.contrib import admin

# Register your models here.
from taiwan_area_info import models


@admin.register(models.AreaInfo)
class AreaInfo(admin.ModelAdmin):
    search_fields = ["_id", "area_name_cn", "area_name_en"]
    list_filter = ["_id", "area_name_cn", "area_name_en"]
    list_display = ["_id", "area_name_cn", "area_name_en"]
    list_editable = []
    ordering = ["area_name_cn"]


@admin.register(models.DistrictInfo)
class DistrictInfo(admin.ModelAdmin):
    search_fields = ["_id", "district_tw", "district_en"]
    list_filter = ["_id", "district_tw", "district_en", "area_uuid"]
    list_display = ["_id", "district_tw", "district_en", "area_uuid"]
    list_editable = []
    ordering = ["area_uuid"]


@admin.register(models.ServiceInfo)
class ServiceInfo(admin.ModelAdmin):
    search_fields = ["_id", "area_uuid"]
    list_filter = ["_id", "area_uuid"]
    list_display = ["_id", "area_uuid"]
    list_editable = []
    ordering = ["area_uuid"]
