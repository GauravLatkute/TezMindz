from django.contrib import admin
from learning.models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "concept", "order"]
    list_filter = ["concept__chapter__class_subject__subject"]
    search_fields = ["title", "content_markdown"]
    ordering = ["concept", "order"]
