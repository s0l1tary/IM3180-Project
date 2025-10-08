# mysite/main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('take_quiz/', views.take_quiz, name='take_quiz'),
    path('submit_quiz/<int:quiz_id>', views.submit_quiz, name='submit_quiz'),
]