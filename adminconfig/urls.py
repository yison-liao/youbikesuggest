"""
URL configuration for adminconfig project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path, re_path

from authn import urls as authn_urls
from weather import urls as weather_urls
from youbike import urls as youbike_urls

url_route = [
    re_path(r"authn/", include(authn_urls.api_pattern)),
    re_path(r"youbike/", include(youbike_urls.api_pattern)),
    re_path(r"weather/", include(weather_urls.api_pattern)),
]
urlpatterns = [path("admin/", admin.site.urls), re_path(r"^api/", include(url_route))]
