from django.contrib import admin
from .models import *

class OptionInline(admin.TabularInline):  # or StackedInline
    model = Option
    extra = 4  # Show 4 empty option fields by default
    min_num = 4  # Require exactly 4 options
    max_num = 4

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "topic", "difficulty")
    list_filter = ("topic", "difficulty")
    search_fields = ("text",)
    inlines = [OptionInline]


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
    list_display = ("id", "question", "get_question_difficulty", "chosen_option", "is_correct")

    def get_question_difficulty(self, obj):
        return obj.question.difficulty
    get_question_difficulty.short_description = "Difficulty"