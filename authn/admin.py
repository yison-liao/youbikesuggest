from django.contrib import admin

from authn import models


# Register your models here.
@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ["_id"]
    list_filter = []
    list_display = ["_id", "username"]
    list_editable = []
    ordering = ["_id"]
