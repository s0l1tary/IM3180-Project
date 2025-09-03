from . import views
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('v1/', views.v1, name='View 1'),
]