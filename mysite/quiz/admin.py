from django.contrib import admin
from .models import Topic, Question, Option

class OptionInline(admin.TabularInline):
    model = Option
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "topic", "difficulty", "text")
    list_filter = ("topic", "difficulty")
    search_fields = ("text",)
    inlines = [OptionInline]

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
