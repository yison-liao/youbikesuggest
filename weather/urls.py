from django.urls import re_path

from weather import views as weather_views

api_pattern = [
    re_path(r"^precipitation", weather_views.Precipitation.as_view()),
]
