from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('content/', views.content, name='content'),
    path('grades/', views.grades, name='grades'),
    path('index/', views.index, name='index'),
    path('quiz/', views.quiz, name='quiz'),
    path('practice/', views.practice, name='practice'),
    path('home/', views.home, name='home'),
]