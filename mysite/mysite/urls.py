from django.contrib import admin
from django.urls import path, include
from register import views as v

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your team's main app (keep this)
    path('', include('main.urls')),

    # Signup from the register app (keep this)
    path('register/', v.signup, name='signup'),

    # Django auth (login/logout/password). Using 'accounts/' avoids clashing with main.
    path('accounts/', include('django.contrib.auth.urls')),

    # Your quiz feature
    path('quiz/', include('quiz.urls')),
]


