from django.urls import re_path

from authn import views as authn_views

api_pattern = [
    re_path(r"register", authn_views.Register.as_view()),
    re_path(r"login", authn_views.Login.as_view()),
    re_path(r"changepassword", authn_views.Password.as_view()),
]
