from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.content, name="content"),
    path('content/pdf/<int:topic_id>/', views.content_pdf, name='content_pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)