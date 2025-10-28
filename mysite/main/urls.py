# mysite/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("content/", views.content, name="content"),
    path("grades/", views.grades, name="grades"),
    path("practice/", views.practice, name="practice"),
    path("quiz/", views.quiz, name="quiz"),        # quiz flow (picker diff then 5Qs then results)
    path("explain/", views.explain, name="explain"),  # AI explanation endpoint
]
