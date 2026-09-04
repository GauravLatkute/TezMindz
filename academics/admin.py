from django.contrib import admin
from academics.models import (
    Class, Subject, ClassSubject, Chapter, Concept,
    Quiz, QuizQuestion, QuizOption, DailyChallenge,
)


# ── Inlines ──────────────────────────────────────────────────────────────────

class ClassSubjectInline(admin.TabularInline):
    model = ClassSubject
    extra = 0


class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ["order", "name", "slug", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


class ConceptInline(admin.TabularInline):
    model = Concept
    extra = 0
    fields = ["order", "name", "slug", "difficulty", "estimated_time", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


class QuizOptionInline(admin.TabularInline):
    model = QuizOption
    extra = 4
    fields = ["order", "option_text", "is_correct"]


class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 0
    fields = ["display_order", "question_text", "marks", "explanation"]


# ── Model Admins ──────────────────────────────────────────────────────────────

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ["grade_number", "class_label", "stage", "age_group", "category", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "class_label"]
    prepopulated_fields = {"slug": ("class_label",)}
    inlines = [ClassSubjectInline]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["title", "subtitle", "olympiad_code", "icon_type", "is_active"]
    list_filter = ["icon_type", "is_active"]
    search_fields = ["title", "olympiad_code"]


@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ["student_class", "subject", "total_modules"]
    list_filter = ["student_class", "subject"]
    search_fields = ["student_class__class_label", "subject__title"]


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ["name", "class_subject", "order", "is_active"]
    list_filter = ["class_subject__student_class", "class_subject__subject", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["class_subject", "order"]
    inlines = [ConceptInline]


@admin.register(Concept)
class ConceptAdmin(admin.ModelAdmin):
    list_display = ["name", "chapter", "order", "difficulty", "estimated_time", "is_active"]
    list_filter = ["chapter__class_subject__subject", "chapter__class_subject__student_class", "difficulty", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["chapter", "order"]


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ["title", "concept", "difficulty", "time_limit", "passing_percentage", "xp_reward", "is_active"]
    list_filter = ["difficulty", "is_active", "concept__chapter__class_subject__student_class"]
    search_fields = ["title", "concept__name"]
    inlines = [QuizQuestionInline]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ["question_text_preview", "quiz", "marks", "display_order"]
    list_filter = ["quiz__concept__chapter__class_subject__student_class"]
    search_fields = ["question_text"]
    inlines = [QuizOptionInline]

    def question_text_preview(self, obj):
        return obj.question_text[:60] + ("..." if len(obj.question_text) > 60 else "")
    question_text_preview.short_description = "Question"


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ["title", "student_class", "date", "difficulty", "xp_reward", "coin_reward", "is_active"]
    list_filter = ["student_class", "difficulty", "is_active", "date"]
    search_fields = ["title", "description"]
    date_hierarchy = "date"
