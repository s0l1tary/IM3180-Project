from django.urls import path
from . import views

urlpatterns = [
    path("", views.content, name="content"),
    path("topic/<int:topic_id>/", views.content_pdf, name="content_pdf"),
]