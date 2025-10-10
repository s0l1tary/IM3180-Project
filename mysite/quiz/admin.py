from django.contrib import admin
from .models import *

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "topic", "difficulty")
    list_filter = ("topic", "difficulty")
    search_fields = ("text",)


@admin.register(UserTopicProgress)
class UserTopicProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "topic", "score", "mastery_level", "last_updated")
    list_filter = ("topic", "user", "mastery_level")
    search_fields = ("user__username", "topic__name")

@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "quiz_type", "score")

@admin.register(QuizQuestionRecord)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "chosen_option", "is_correct")