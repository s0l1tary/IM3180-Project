from django.contrib import admin

from .models import UserTopicProgress  # Direct import is fine here

@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'topic', 'score', 'mastery_level', 'last_updated']
    list_filter = ['user', 'topic', 'mastery_level']
    search_fields = ['user__username', 'topic__name']
    ordering = ['-last_updated']