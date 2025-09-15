from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('quiz/', include('quiz.urls')),                     # <- needs quiz/urls.py
    path('accounts/', include('django.contrib.auth.urls')),  # login/logout/password pages
    path('', RedirectView.as_view(url='/quiz/', permanent=False)),
]


