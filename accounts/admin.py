from django.contrib import admin
from accounts.models import StudentProfile

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "student_class", "xp", "coins", "current_level", "streak", "last_activity_date"]
    list_filter = ["student_class", "current_level"]
    search_fields = ["user__username", "user__email", "user__first_name"]
    readonly_fields = ["created_at", "updated_at"]
