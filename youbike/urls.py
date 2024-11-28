from django.urls import re_path

from youbike import views as youbike_views

api_pattern = [
    re_path(r"^bikestationstatus", youbike_views.YoubikeStationsStatus.as_view()),
]
