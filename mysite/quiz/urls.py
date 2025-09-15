from django.urls import path
from . import views

urlpatterns = [
    path('', views.choose, name='quiz_choose'),
    path('take/', views.take_quiz, name='quiz_take'),
]
