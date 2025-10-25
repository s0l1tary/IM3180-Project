# mysite/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("content/", views.content, name="content"),

    path('grades/', views.grades, name='grades'),

    path("practice/", views.practice, name="practice"),

]
