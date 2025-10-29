# mysite/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("grades/", views.grades, name="grades"),
]
